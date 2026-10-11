"""
TÂCHE A — BLOC 7 : Benchmark wav2vec 2.0 / MMS-1B sur les 36 clips canoniques.

Modèle : facebook/mms-1b-all (CTC, ~2 GB fp16 GPU)
Inférence directe — bypass total pipeline et torchcodec.
Par langue : processor.tokenizer.set_target_lang() + model.load_adapter()

Tag           : K_wav2vec
Sortie        : results/stt_eval_wav2vec_results.csv
Comparaison   : K_wav2vec vs J0_small_hf_vanilla (même 36 clips, même WER normalisé)
"""
import sys
import csv
import time
import logging
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Fix : éviter que datasets/ local masque le package HF.
_root = str(Path(__file__).resolve().parents[2])
sys.path = [p for p in sys.path if p not in ("", ".", _root)]
sys.path.insert(0, _root)

import torch
import librosa
import numpy as np
from transformers import Wav2Vec2ForCTC, AutoProcessor

from backend.evaluation.metrics import wer, cer
from backend.evaluation.dataset import load_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_CSV    = Path("results/stt_eval_wav2vec_results.csv")
LORA_CSV      = Path("results/stt_eval_lora_results.csv")
EVAL_METADATA = Path("datasets/stt_eval/metadata.csv")
MMS_MODEL     = "facebook/mms-1b-all"
TARGET_SR     = 16_000

# ISO 639-3 codes pour MMS-1B-all
LANG_MAP = {"en": "eng", "fr": "fra", "de": "deu"}

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


def transcribe_ctc(model: Wav2Vec2ForCTC, processor: AutoProcessor,
                   audio_array: np.ndarray,
                   device: torch.device, dtype: torch.dtype) -> str:
    """Décodage CTC direct — processor pré-configuré avec set_target_lang."""
    inputs_raw = processor(audio_array, sampling_rate=TARGET_SR, return_tensors="pt")
    input_values = inputs_raw.input_values.to(device=device, dtype=dtype)

    kw = {"input_values": input_values}
    if hasattr(inputs_raw, "attention_mask") and inputs_raw.attention_mask is not None:
        kw["attention_mask"] = inputs_raw.attention_mask.to(device=device)

    with torch.no_grad():
        logits = model(**kw).logits

    predicted_ids = torch.argmax(logits, dim=-1)[0]
    return processor.decode(predicted_ids).strip()


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # fp32 par défaut pour wav2vec2 : évite les NaN en fp16 sur conv1d
    dtype  = torch.float16 if device.type == "cuda" else torch.float32
    logger.info("Device : %s  dtype : %s", device, dtype)

    samples = [s for s in load_metadata(str(EVAL_METADATA))
               if s.audio_path.exists() and s.reference_path.exists()]
    logger.info("%d échantillons à évaluer", len(samples))

    # ── Chargement du modèle ─────────────────────────────────────────────
    logger.info("Chargement %s…", MMS_MODEL)
    try:
        processor = AutoProcessor.from_pretrained(MMS_MODEL)
        model = Wav2Vec2ForCTC.from_pretrained(
            MMS_MODEL, torch_dtype=dtype, ignore_mismatched_sizes=True
        ).to(device)
        model.eval()
        logger.info("  OK — %s chargé sur %s", MMS_MODEL, device)
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            logger.error("OOM GPU — essayer CPU en retirant la variable CUDA_VISIBLE_DEVICES.")
        raise

    # ── Évaluation groupée par langue (1 load_adapter / langue) ─────────
    by_lang: dict[str, list] = defaultdict(list)
    for s in samples:
        by_lang[s.language].append(s)

    rows = []
    for lang in ["en", "fr", "de"]:
        lang_samples = by_lang.get(lang, [])
        if not lang_samples:
            continue
        mms_lang = LANG_MAP[lang]
        logger.info("\n--- Langue : %s → %s (%d clips) ---", lang, mms_lang, len(lang_samples))

        processor.tokenizer.set_target_lang(mms_lang)
        model.load_adapter(mms_lang)

        for s in lang_samples:
            try:
                dur = get_duration(str(s.audio_path))
                ref = s.reference_path.read_text(encoding="utf-8").strip()
                audio_array, _ = librosa.load(str(s.audio_path), sr=TARGET_SR, mono=True)

                t0      = time.time()
                hyp     = transcribe_ctc(model, processor, audio_array, device, dtype)
                elapsed = time.time() - t0

                w   = wer(ref, hyp) if ref else float("nan")
                c   = cer(ref, hyp) if ref else float("nan")
                rtf = elapsed / dur if dur > 0 else float("inf")

                rows.append({
                    "filename": s.audio_filename, "language": s.language,
                    "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
                    "model": "mms-1b-all",
                    "preprocessing_enabled": False, "domain_prompt_enabled": False,
                    "forced_language": mms_lang,
                    "duration_audio_seconds":  round(dur, 2),
                    "processing_time_seconds": round(elapsed, 2),
                    "real_time_factor":        round(rtf, 4),
                    "wer": round(w, 4) if w == w else w,
                    "cer": round(c, 4) if c == c else c,
                    "detected_language": mms_lang,
                    "transcript_output_path": "",
                    "reference_text": ref, "hypothesis_text": hyp, "error": "",
                    "condition_tag": "K_wav2vec",
                })
                logger.info("  [K] %s | WER=%.3f CER=%.3f RTF=%.3f",
                            s.audio_filename, w, c, rtf)

            except Exception as e:
                logger.error("  ERREUR %s : %s", s.audio_filename, e)
                rows.append({
                    "filename": s.audio_filename, "language": s.language,
                    "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
                    "model": "mms-1b-all",
                    "preprocessing_enabled": False, "domain_prompt_enabled": False,
                    "forced_language": mms_lang,
                    "duration_audio_seconds": 0, "processing_time_seconds": 0,
                    "real_time_factor": float("inf"),
                    "wer": float("nan"), "cer": float("nan"),
                    "detected_language": "", "transcript_output_path": "",
                    "reference_text": "", "hypothesis_text": "", "error": str(e),
                    "condition_tag": "K_wav2vec",
                })

    # ── Écriture CSV ─────────────────────────────────────────────────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("\nRésultats K_wav2vec → %s (%d lignes)", OUTPUT_CSV, len(rows))

    # ── Résumé K ─────────────────────────────────────────────────────────
    import statistics
    valid = [r for r in rows if not r["error"] and r["wer"] == r["wer"]]
    if valid:
        wers = [r["wer"] for r in valid]
        cers = [r["cer"] for r in valid]
        rtfs = [r["real_time_factor"] for r in valid
                if r["real_time_factor"] != float("inf")]
        print(f"\n=== K_wav2vec ({len(valid)}/{len(rows)} valides) ===")
        print(f"  WER moyen : {statistics.mean(wers):.3f}")
        print(f"  CER moyen : {statistics.mean(cers):.3f}")
        if rtfs:
            print(f"  RTF moyen : {statistics.mean(rtfs):.3f}")
        for lang in ["en", "fr", "de"]:
            lv = [r for r in valid if r["language"] == lang]
            if lv:
                print(f"    {lang}: WER={statistics.mean(r['wer'] for r in lv):.3f} "
                      f"({len(lv)} clips)")

    # ── Comparaison primaire K vs J0 ──────────────────────────────────────
    print("\n=== COMPARAISON PRIMAIRE : K_wav2vec vs J0_small_hf_vanilla ===")
    if LORA_CSV.exists():
        j0_rows = []
        with open(LORA_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["condition_tag"] == "J0_small_hf_vanilla" and not row["error"]:
                    try:
                        j0_rows.append({**row,
                                        "wer": float(row["wer"]),
                                        "cer": float(row["cer"])})
                    except ValueError:
                        pass

        if j0_rows and valid:
            k_wer  = statistics.mean(r["wer"] for r in valid)
            j0_wer = statistics.mean(r["wer"] for r in j0_rows)
            k_cer  = statistics.mean(r["cer"] for r in valid)
            j0_cer = statistics.mean(r["cer"] for r in j0_rows)

            print(f"\n  {'Modèle':<32} {'WER':>8} {'CER':>8}")
            print(f"  {'-'*50}")
            print(f"  {'K_wav2vec  (MMS-1B-all)':<32} {k_wer:>8.3f} {k_cer:>8.3f}")
            print(f"  {'J0_vanilla (whisper-small HF)':<32} {j0_wer:>8.3f} {j0_cer:>8.3f}")
            print(f"  {'ΔWER (K − J0)':<32} {(k_wer - j0_wer):>+8.3f}")
            print()
            print("  Contexte : WER normalisé (pas de ponctuation ni casse).")
            print("  Avantage Whisper attendu : ponctuation, timestamps, multilinguisme natif.")

            # Par bruit
            for cond in ["clean", "noisy"]:
                kv = [r for r in valid if r["noise_condition"] == cond]
                j0v = [r for r in j0_rows if r["noise_condition"] == cond]
                if kv and j0v:
                    kw = statistics.mean(r["wer"] for r in kv)
                    j0w = statistics.mean(r["wer"] for r in j0v)
                    print(f"  [{cond}] K={kw:.3f}  J0={j0w:.3f}  Δ={kw-j0w:+.3f}")
    else:
        print("  (stt_eval_lora_results.csv non trouvé — relancer eval_lora.py d'abord)")


if __name__ == "__main__":
    main()
