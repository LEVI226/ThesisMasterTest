"""
ÉTAPE 3 — Évaluation comparative sur les 36 échantillons canoniques.

Deux passes via le MÊME chemin d'inférence HF (isolation parfaite) :
  J0_small_hf_vanilla : whisper-small HF sans adaptateur
  J_lora_small        : whisper-small HF + adaptateur LoRA fusionné

Inférence directe model.generate() — bypass total du pipeline HF et de
torchcodec (DLLs FFmpeg absentes sur Windows avec PyTorch 2.6+cu124).

Même scoreur WER/CER que backend/evaluation/metrics.py.
Sortie : results/stt_eval_lora_results.csv (mêmes colonnes que pilot_results).

Comparaison primaire  : J_lora vs J0_vanilla (seuls les poids diffèrent).
Comparaison secondaire: G_model_small (faster-whisper, noisereduce) — caveat
                        inter-implémentations à mentionner dans la thèse.
"""
import sys
import csv
import time
import logging
from pathlib import Path

sys.path.insert(0, ".")

import torch
import librosa
import numpy as np
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from peft import PeftModel

from backend.evaluation.metrics import wer, cer
from backend.evaluation.dataset import load_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADAPTER_DIR   = Path("models/lora_small_minds14")
OUTPUT_CSV    = Path("results/stt_eval_lora_results.csv")
EVAL_METADATA = Path("datasets/stt_eval/metadata.csv")
BASE_MODEL    = "openai/whisper-small"
TARGET_SR     = 16_000

FIELDNAMES = [
    "filename", "language", "noise_condition", "speaker_count",
    "model", "preprocessing_enabled", "domain_prompt_enabled", "forced_language",
    "duration_audio_seconds", "processing_time_seconds", "real_time_factor",
    "wer", "cer", "detected_language",
    "transcript_output_path", "reference_text", "hypothesis_text", "error",
    "condition_tag",
]


def get_duration(path: str) -> float:
    try:
        a, sr = librosa.load(path, sr=None, mono=True)
        return float(len(a) / sr)
    except Exception:
        return 0.0


def transcribe_direct(model, processor, audio_array: np.ndarray,
                      device: torch.device, dtype: torch.dtype) -> str:
    """Inférence directe sans pipeline — bypass torchcodec totalement."""
    input_features = processor.feature_extractor(
        audio_array,
        sampling_rate=TARGET_SR,
        return_tensors="pt",
    ).input_features.to(device=device, dtype=dtype)

    with torch.no_grad():
        predicted_ids = model.generate(input_features)

    return processor.tokenizer.batch_decode(
        predicted_ids, skip_special_tokens=True
    )[0].strip()


def run_eval_pass(model, processor, device, dtype,
                  samples, tag: str, model_label: str) -> list[dict]:
    """Transcrit les 36 échantillons, retourne les lignes CSV."""
    rows = []
    for s in samples:
        try:
            dur = get_duration(str(s.audio_path))
            ref = s.reference_path.read_text(encoding="utf-8").strip()
            audio_array, _ = librosa.load(str(s.audio_path), sr=TARGET_SR, mono=True)
            t0      = time.time()
            hyp     = transcribe_direct(model, processor, audio_array, device, dtype)
            elapsed = time.time() - t0
            w   = wer(ref, hyp) if ref else float("nan")
            c   = cer(ref, hyp) if ref else float("nan")
            rtf = elapsed / dur if dur > 0 else float("inf")
            rows.append({
                "filename": s.audio_filename, "language": s.language,
                "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
                "model": model_label,
                "preprocessing_enabled": False, "domain_prompt_enabled": False,
                "forced_language": None,
                "duration_audio_seconds":  round(dur, 2),
                "processing_time_seconds": round(elapsed, 2),
                "real_time_factor":        round(rtf, 4),
                "wer": round(w, 4) if w == w else w,
                "cer": round(c, 4) if c == c else c,
                "detected_language": "", "transcript_output_path": "",
                "reference_text": ref, "hypothesis_text": hyp, "error": "",
                "condition_tag": tag,
            })
            logger.info("  [%s] %s | WER=%.3f CER=%.3f RTF=%.3f",
                        tag, s.audio_filename, w, c, rtf)
        except Exception as e:
            logger.error("  [%s] ERREUR %s : %s", tag, s.audio_filename, e)
            rows.append({
                "filename": s.audio_filename, "language": s.language,
                "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
                "model": model_label,
                "preprocessing_enabled": False, "domain_prompt_enabled": False,
                "forced_language": None,
                "duration_audio_seconds": 0, "processing_time_seconds": 0,
                "real_time_factor": float("inf"),
                "wer": float("nan"), "cer": float("nan"),
                "detected_language": "", "transcript_output_path": "",
                "reference_text": "", "hypothesis_text": "", "error": str(e),
                "condition_tag": tag,
            })
    return rows


def make_summary(rows: list[dict], tag: str) -> None:
    import statistics
    valid = [r for r in rows if not r["error"]]
    if not valid:
        print(f"\n  {tag} : AUCUN résultat valide")
        return
    wers = [r["wer"] for r in valid if r["wer"] == r["wer"]]
    cers = [r["cer"] for r in valid if r["cer"] == r["cer"]]
    rtfs = [r["real_time_factor"] for r in valid
            if r["real_time_factor"] != float("inf")]
    print(f"\n=== {tag} ({len(valid)}/36 valides) ===")
    print(f"  WER moyen : {statistics.mean(wers):.3f}")
    print(f"  CER moyen : {statistics.mean(cers):.3f}")
    print(f"  RTF moyen : {statistics.mean(rtfs):.3f}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype  = torch.float16 if device.type == "cuda" else torch.float32
    logger.info("Device : %s  dtype : %s", device, dtype)

    samples = [s for s in load_metadata(str(EVAL_METADATA))
               if s.audio_path.exists() and s.reference_path.exists()]
    logger.info("%d échantillons à évaluer", len(samples))

    all_rows: list[dict] = []

    # ── PASSE 1 : J0_small_hf_vanilla ────────────────��───────────────────────
    logger.info("\n=== PASSE 1 : J0_small_hf_vanilla (poids originaux, sans LoRA) ===")
    vanilla_proc  = WhisperProcessor.from_pretrained(BASE_MODEL)
    vanilla_model = WhisperForConditionalGeneration.from_pretrained(
        BASE_MODEL, torch_dtype=dtype
    ).to(device)
    vanilla_model.eval()

    all_rows += run_eval_pass(
        vanilla_model, vanilla_proc, device, dtype,
        samples, tag="J0_small_hf_vanilla", model_label="whisper-small-hf-vanilla",
    )

    del vanilla_model
    if device.type == "cuda":
        torch.cuda.empty_cache()

    # ── PASSE 2 : J_lora_small ───────────────────────────────────────────────
    logger.info("\n=== PASSE 2 : J_lora_small (poids fusionnés LoRA) ===")
    lora_proc  = WhisperProcessor.from_pretrained(str(ADAPTER_DIR))
    base_model = WhisperForConditionalGeneration.from_pretrained(
        BASE_MODEL, torch_dtype=dtype
    )
    lora_model = PeftModel.from_pretrained(base_model, str(ADAPTER_DIR)).merge_and_unload()
    lora_model = lora_model.to(device)
    lora_model.eval()

    all_rows += run_eval_pass(
        lora_model, lora_proc, device, dtype,
        samples, tag="J_lora_small", model_label="whisper-small+lora",
    )

    # ── Écriture CSV ───────────────────────────────────────────────��─────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)
    logger.info("Résultats → %s (%d lignes)", OUTPUT_CSV, len(all_rows))

    # ── Résumés comparatifs ─���─────────────────────────────���───────────────────
    j0_rows = [r for r in all_rows if r["condition_tag"] == "J0_small_hf_vanilla"]
    j_rows  = [r for r in all_rows if r["condition_tag"] == "J_lora_small"]
    make_summary(j0_rows, "J0_small_hf_vanilla")
    make_summary(j_rows,  "J_lora_small")

    # Delta fine-tuning (comparaison primaire)
    j0_valid = [r for r in j0_rows if not r["error"] and r["wer"] == r["wer"]]
    j_valid  = [r for r in j_rows  if not r["error"] and r["wer"] == r["wer"]]
    if j0_valid and j_valid:
        import statistics
        delta_wer = (statistics.mean(r["wer"] for r in j_valid) -
                     statistics.mean(r["wer"] for r in j0_valid))
        direction = "amélioration" if delta_wer < 0 else "dégradation"
        print(f"\nΔWER fine-tuning (J_lora − J0_vanilla) : {delta_wer:+.3f}  ({direction})")
        print("(Comparaison G_model_small : voir pilot_results, caveat inter-implémentations)")


if __name__ == "__main__":
    main()
