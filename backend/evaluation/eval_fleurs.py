"""
BLOC 8 — ÉTAPE 2 + 3 : Évaluation Whisper (tiny/base/small/medium/large-v3) sur FLEURS.

ÉTAPE 2 :
  60 clips (20 × 3 langues) depuis datasets/fleurs_eval/
  GPU fp16, langue auto (forced_decoder_ids=None)
  output → results/stt_eval_fleurs_results.csv
  tags : FLEURS_tiny, FLEURS_base, FLEURS_small, FLEURS_medium, FLEURS_large_v3

ÉTAPE 3 :
  Tableau résumé WER/CER par modèle × langue
  Rappel que FLEURS ≠ MInDS-14 (parole lue propre vs téléphonique bruité)
"""
import sys
import time
import csv
import logging
import librosa
import torch
import numpy as np
from pathlib import Path

# Fix : éviter que le dossier datasets/ local masque le package HF datasets.
_root = str(Path(__file__).resolve().parents[2])
sys.path = [p for p in sys.path if p not in ("", ".", _root)]

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

# Import depuis le module backend
sys.path.insert(0, _root)
from backend.evaluation.metrics import wer, cer
from backend.evaluation.dataset import load_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────────────────
FLEURS_META    = Path("datasets/fleurs_eval/metadata.csv")
FLEURS_AUDIO   = Path("datasets/fleurs_eval/audio")
FLEURS_REFS    = Path("datasets/fleurs_eval/references")
RESULTS_CSV    = Path("results/stt_eval_fleurs_results.csv")
TRANSCRIPT_DIR = Path("results/fleurs_transcripts")
SR_TARGET      = 16_000

MODELS = [
    ("openai/whisper-tiny",     "FLEURS_tiny"),
    ("openai/whisper-base",     "FLEURS_base"),
    ("openai/whisper-small",    "FLEURS_small"),
    ("openai/whisper-medium",   "FLEURS_medium"),
    ("openai/whisper-large-v3", "FLEURS_large_v3"),
]

RESULTS_FIELDS = [
    "filename", "language", "noise_condition", "speaker_count",
    "model", "preprocessing_enabled", "domain_prompt_enabled",
    "forced_language", "duration_audio_seconds", "processing_time_seconds",
    "real_time_factor", "wer", "cer", "detected_language",
    "transcript_output_path", "reference_text", "hypothesis_text",
    "error", "condition_tag",
]


def load_audio(wav_path: Path) -> tuple[np.ndarray, float]:
    arr, _ = librosa.load(str(wav_path), sr=SR_TARGET, mono=True)
    return arr.astype(np.float32), len(arr) / SR_TARGET


def transcribe(model, processor, arr: np.ndarray, device: str, dtype) -> tuple[str, str]:
    """Retourne (hypothèse, langue_détectée)."""
    features = processor.feature_extractor(
        arr, sampling_rate=SR_TARGET, return_tensors="pt"
    ).input_features.to(device=device, dtype=dtype)

    model.config.forced_decoder_ids = None

    with torch.no_grad():
        ids = model.generate(features, forced_decoder_ids=None)

    hyp = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

    # Langue détectée : génère avec tokens spéciaux pour lire la langue
    try:
        with torch.no_grad():
            ids_full = model.generate(features, forced_decoder_ids=None, return_dict_in_generate=False)
        dec_full = processor.batch_decode(ids_full, skip_special_tokens=False)[0]
        # Extract <|lang_code|> token
        import re
        m = re.search(r"<\|([a-z]{2,})\|>", dec_full)
        lang_detected = m.group(1) if m else "unknown"
    except Exception:
        lang_detected = "unknown"

    return hyp, lang_detected


def main():
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    samples = load_metadata(
        FLEURS_META,
        audio_dir=FLEURS_AUDIO,
        reference_dir=FLEURS_REFS,
    )
    logger.info("Chargé %d clips depuis %s", len(samples), FLEURS_META)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32
    logger.info("Device : %s  dtype : %s", device, dtype)

    all_rows: list[dict] = []

    for model_id, tag in MODELS:
        logger.info("\n══ %s (%s) ══", model_id, tag)

        try:
            processor = AutoProcessor.from_pretrained(model_id)
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
            ).to(device)
            model.eval()
        except Exception as e:
            logger.error("Échec de chargement %s : %s", model_id, e)
            for s in samples:
                all_rows.append(_error_row(s, model_id, tag, str(e)))
            continue

        for s in samples:
            wav_path = FLEURS_AUDIO / s.audio_filename
            ref_path = FLEURS_REFS  / s.reference_filename

            ref_text = ref_path.read_text(encoding="utf-8").strip() if ref_path.exists() else ""

            try:
                arr, duration = load_audio(wav_path)
            except Exception as e:
                all_rows.append(_error_row(s, model_id, tag, f"audio load error: {e}", ref_text))
                continue

            t0 = time.perf_counter()
            try:
                hyp, lang_detected = transcribe(model, processor, arr, device, dtype)
            except Exception as e:
                all_rows.append(_error_row(s, model_id, tag, f"transcription error: {e}", ref_text))
                continue
            elapsed = time.perf_counter() - t0

            wer_val = wer(ref_text, hyp)
            cer_val = cer(ref_text, hyp)

            stem = Path(s.audio_filename).stem
            out_path = TRANSCRIPT_DIR / f"{stem}_{tag}.txt"
            out_path.write_text(hyp, encoding="utf-8")

            row = {
                "filename":               s.audio_filename,
                "language":               s.language,
                "noise_condition":        s.noise_condition,
                "speaker_count":          s.speaker_count,
                "model":                  model_id,
                "preprocessing_enabled":  False,
                "domain_prompt_enabled":  False,
                "forced_language":        None,
                "duration_audio_seconds": round(duration, 3),
                "processing_time_seconds": round(elapsed, 3),
                "real_time_factor":       round(elapsed / duration, 3) if duration > 0 else None,
                "wer":                    round(wer_val, 4),
                "cer":                    round(cer_val, 4),
                "detected_language":      lang_detected,
                "transcript_output_path": str(out_path),
                "reference_text":         ref_text,
                "hypothesis_text":        hyp,
                "error":                  None,
                "condition_tag":          tag,
            }
            all_rows.append(row)

            logger.info(
                "  %-45s lang=%-2s  WER=%.3f  CER=%.3f  det=%s  RTF=%.2f",
                s.audio_filename, s.language, wer_val, cer_val,
                lang_detected, row["real_time_factor"] or 0,
            )

        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    # ── Écriture CSV ────────────────────────────────────────────────────────
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RESULTS_FIELDS)
        w.writeheader()
        w.writerows(all_rows)
    logger.info("\nRésultats → %s  (%d lignes)", RESULTS_CSV, len(all_rows))

    # ── ÉTAPE 3 : Tableau résumé ─────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("ÉTAPE 3 — Résumé WER/CER par modèle × langue")
    print("=" * 72)
    print(f"{'Modèle':<22}{'Lang':<6}{'N':>4}  {'WER (moy)':>10}  {'CER (moy)':>10}")
    print("-" * 72)

    pivot: dict[tuple, list] = {}
    for r in all_rows:
        if r["error"]:
            continue
        key = (r["condition_tag"], r["language"])
        if key not in pivot:
            pivot[key] = []
        pivot[key].append((r["wer"], r["cer"]))

    tags_order = [t for _, t in MODELS]
    langs_order = ["en", "fr", "de"]

    for tag in tags_order:
        for lang in langs_order:
            vals = pivot.get((tag, lang), [])
            if not vals:
                continue
            avg_wer = np.mean([v[0] for v in vals])
            avg_cer = np.mean([v[1] for v in vals])
            print(f"{tag:<22}{lang:<6}{len(vals):>4}  {avg_wer:>10.3f}  {avg_cer:>10.3f}")
        # Moyenne toutes langues pour ce tag
        all_vals = [v for lang in langs_order for v in pivot.get((tag, lang), [])]
        if all_vals:
            avg_wer = np.mean([v[0] for v in all_vals])
            avg_cer = np.mean([v[1] for v in all_vals])
            print(f"{tag:<22}{'ALL':<6}{len(all_vals):>4}  {avg_wer:>10.3f}  {avg_cer:>10.3f}")
            print()

    print("=" * 72)
    print()
    print("⚠  AVERTISSEMENT COMPARAISON :")
    print("   FLEURS = parole lue propre, haute qualité (studio).")
    print("   MInDS-14 = parole téléphonique bruitée, domaine call-center.")
    print("   Ces deux benchmarks NE SONT PAS comparables directement.")
    print("   Les WER FLEURS seront systématiquement inférieurs aux WER MInDS-14")
    print("   pour les mêmes modèles — c'est la nature du domaine, pas la perf.")
    print("=" * 72)


def _error_row(s, model_id: str, tag: str, error: str, ref_text: str = "") -> dict:
    return {
        "filename":               s.audio_filename,
        "language":               s.language,
        "noise_condition":        s.noise_condition,
        "speaker_count":          s.speaker_count,
        "model":                  model_id,
        "preprocessing_enabled":  False,
        "domain_prompt_enabled":  False,
        "forced_language":        None,
        "duration_audio_seconds": None,
        "processing_time_seconds": None,
        "real_time_factor":       None,
        "wer":                    None,
        "cer":                    None,
        "detected_language":      None,
        "transcript_output_path": None,
        "reference_text":         ref_text,
        "hypothesis_text":        None,
        "error":                  error,
        "condition_tag":          tag,
    }


if __name__ == "__main__":
    main()
