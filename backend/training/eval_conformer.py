"""
BLOC 9 — Baseline Conformer CTC sur les 36 clips canoniques MInDS-14.

Plan principal (NeMo) :
  EN : nvidia/stt_en_conformer_ctc_large
  FR : nvidia/stt_fr_conformer_ctc_large
  DE : nvidia/stt_de_conformer_ctc_large

Plan de repli (HuggingFace Wav2Vec2-Conformer), si NeMo non disponible :
  EN : facebook/wav2vec2-conformer-rope-large-960h-ft
  FR / DE : "CONFORMER_UNAVAILABLE" (journalisé, rien n'est fabriqué)

Sortie  : results/stt_eval_conformer_results.csv
Tag     : L_conformer_{en,fr,de}
Scorer  : backend/evaluation/metrics.py (WER/CER Wagner-Fischer, identique
          aux autres campagnes — minuscules + suppression ponctuation + espaces)
"""
import sys
import csv
import time
import logging
import statistics
import numpy as np
from pathlib import Path

# Fix : éviter que datasets/ local masque le package HF datasets.
_root = str(Path(__file__).resolve().parents[2])
sys.path = [p for p in sys.path if p not in ("", ".", _root)]
sys.path.insert(0, _root)

import torch
import librosa

from backend.evaluation.metrics import wer, cer
from backend.evaluation.dataset import load_metadata

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

OUTPUT_CSV    = Path("results/stt_eval_conformer_results.csv")
EVAL_METADATA = Path("datasets/stt_eval/metadata.csv")
TARGET_SR     = 16_000

FIELDNAMES = [
    "filename", "language", "noise_condition", "speaker_count",
    "model", "preprocessing_enabled", "domain_prompt_enabled", "forced_language",
    "duration_audio_seconds", "processing_time_seconds", "real_time_factor",
    "wer", "cer", "detected_language",
    "transcript_output_path", "reference_text", "hypothesis_text", "error",
    "condition_tag",
]

# ── Modèles NeMo ────────────────────────────────────────────────────────────
NEMO_MODELS = {
    "en": "nvidia/stt_en_conformer_ctc_large",
    "fr": "nvidia/stt_fr_conformer_ctc_large",
    "de": "nvidia/stt_de_conformer_ctc_large",
}

# ── Modèle HF (repli) ───────────────────────────────────────────────────────
HF_CONFORMER_EN = "facebook/wav2vec2-conformer-rope-large-960h-ft"


# ─────────────────────────────────────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────────────────────────────────────

def get_duration(path: Path) -> float:
    try:
        a, sr = librosa.load(str(path), sr=None, mono=True)
        return float(len(a) / sr)
    except Exception:
        return 0.0


def load_audio(path: Path) -> np.ndarray:
    arr, _ = librosa.load(str(path), sr=TARGET_SR, mono=True)
    return arr.astype(np.float32)


def make_error_row(s, model_id: str, tag: str, error_msg: str) -> dict:
    return {
        "filename": s.audio_filename, "language": s.language,
        "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
        "model": model_id,
        "preprocessing_enabled": False, "domain_prompt_enabled": False,
        "forced_language": s.language,
        "duration_audio_seconds": 0, "processing_time_seconds": 0,
        "real_time_factor": float("inf"),
        "wer": float("nan"), "cer": float("nan"),
        "detected_language": "", "transcript_output_path": "",
        "reference_text": "", "hypothesis_text": "", "error": error_msg,
        "condition_tag": tag,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Plan A : NeMo
# ─────────────────────────────────────────────────────────────────────────────

def run_nemo(samples_by_lang: dict, device: str) -> tuple[list[dict], str]:
    """Évalue avec NeMo Conformer CTC. Retourne (rows, backend_label)."""
    import nemo.collections.asr as nemo_asr
    logger.info("Backend : NeMo %s", __import__("nemo").__version__)

    rows: list[dict] = []

    for lang in ["en", "fr", "de"]:
        lang_samples = samples_by_lang.get(lang, [])
        if not lang_samples:
            continue

        model_id = NEMO_MODELS[lang]
        tag = f"L_conformer_{lang}"
        logger.info("\n--- NeMo %s (%d clips) ---", model_id, len(lang_samples))

        # Chargement du modèle
        try:
            model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_id)
        except Exception:
            try:
                model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_id)
            except Exception as e2:
                logger.error("NeMo : impossible de charger %s : %s", model_id, e2)
                for s in lang_samples:
                    rows.append(make_error_row(s, model_id, tag, f"MODEL_UNAVAILABLE: {e2}"))
                continue

        actual_id = getattr(model, "_pretrained_model_name", model_id)
        logger.info("  Modèle chargé : %s", actual_id)

        if device == "cuda":
            model = model.cuda()
        model.eval()

        # Préchauffage (clip 0) — excluded du RTF
        warmup_done = False
        for s in lang_samples:
            dur = get_duration(s.audio_path)
            try:
                ref = s.reference_path.read_text(encoding="utf-8").strip()
                # NeMo transcribe accepte des paths directement
                tmp_wav = Path(str(s.audio_path))  # déjà 16kHz mono

                if not warmup_done:
                    # Préchauffage silencieux
                    try:
                        model.transcribe([str(tmp_wav)])
                    except Exception:
                        pass
                    warmup_done = True
                    logger.info("  Préchauffage terminé sur %s", s.audio_filename)

                t0 = time.perf_counter()
                hyp_list = model.transcribe([str(tmp_wav)])
                elapsed = time.perf_counter() - t0

                hyp = hyp_list[0] if hyp_list else ""
                if isinstance(hyp, (list, tuple)):
                    hyp = hyp[0]
                # NeMo 3.x : transcribe() retourne des Hypothesis, pas des str
                if hasattr(hyp, "text"):
                    hyp = hyp.text
                elif not isinstance(hyp, str):
                    hyp = str(hyp)

                w = wer(ref, hyp) if ref else float("nan")
                c = cer(ref, hyp) if ref else float("nan")
                rtf = elapsed / dur if dur > 0 else float("inf")

                rows.append({
                    "filename": s.audio_filename, "language": s.language,
                    "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
                    "model": actual_id,
                    "preprocessing_enabled": False, "domain_prompt_enabled": False,
                    "forced_language": lang,
                    "duration_audio_seconds": round(dur, 3),
                    "processing_time_seconds": round(elapsed, 3),
                    "real_time_factor": round(rtf, 4),
                    "wer": round(w, 4) if w == w else w,
                    "cer": round(c, 4) if c == c else c,
                    "detected_language": lang,
                    "transcript_output_path": "",
                    "reference_text": ref, "hypothesis_text": hyp, "error": "",
                    "condition_tag": tag,
                })
                logger.info("  [NeMo] %s | WER=%.3f CER=%.3f RTF=%.3f",
                            s.audio_filename, w, c, rtf)

            except Exception as e:
                logger.error("  ERREUR %s : %s", s.audio_filename, e)
                rows.append(make_error_row(s, model_id, tag, str(e)))

        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    return rows, "NeMo"


# ─────────────────────────────────────────────────────────────────────────────
# Plan B : HuggingFace Wav2Vec2-Conformer (EN seulement)
# ─────────────────────────────────────────────────────────────────────────────

def run_hf_conformer(samples_by_lang: dict, device: str, dtype: torch.dtype) -> tuple[list[dict], str]:
    """Évalue avec HF Wav2Vec2-Conformer (EN seulement). FR/DE → CONFORMER_UNAVAILABLE."""
    from transformers import AutoProcessor, Wav2Vec2ConformerForCTC
    import transformers
    logger.info("Backend : transformers %s", transformers.__version__)
    logger.info("Modèle EN : %s", HF_CONFORMER_EN)

    rows: list[dict] = []
    tag_en = "L_conformer_en"

    # ── EN ──────────────────────────────────────────────────────────────────
    en_samples = samples_by_lang.get("en", [])
    if en_samples:
        try:
            processor = AutoProcessor.from_pretrained(HF_CONFORMER_EN)
            model = Wav2Vec2ConformerForCTC.from_pretrained(
                HF_CONFORMER_EN, torch_dtype=dtype, ignore_mismatched_sizes=True
            ).to(device)
            model.eval()
            logger.info("  HF Conformer EN chargé sur %s", device)

            warmup_done = False
            for s in en_samples:
                dur = get_duration(s.audio_path)
                try:
                    ref = s.reference_path.read_text(encoding="utf-8").strip()
                    arr = load_audio(s.audio_path)

                    # Préchauffage
                    if not warmup_done:
                        inp_w = processor(arr, sampling_rate=TARGET_SR, return_tensors="pt")
                        inp_v = inp_w.input_values.to(device=device, dtype=dtype)
                        with torch.no_grad():
                            model(input_values=inp_v)
                        warmup_done = True
                        logger.info("  Préchauffage HF EN terminé")

                    inp = processor(arr, sampling_rate=TARGET_SR, return_tensors="pt")
                    input_values = inp.input_values.to(device=device, dtype=dtype)
                    kw = {"input_values": input_values}
                    if hasattr(inp, "attention_mask") and inp.attention_mask is not None:
                        kw["attention_mask"] = inp.attention_mask.to(device=device)

                    t0 = time.perf_counter()
                    with torch.no_grad():
                        logits = model(**kw).logits
                    elapsed = time.perf_counter() - t0

                    predicted_ids = torch.argmax(logits, dim=-1)[0]
                    hyp = processor.decode(predicted_ids).strip()

                    w = wer(ref, hyp) if ref else float("nan")
                    c = cer(ref, hyp) if ref else float("nan")
                    rtf = elapsed / dur if dur > 0 else float("inf")

                    rows.append({
                        "filename": s.audio_filename, "language": s.language,
                        "noise_condition": s.noise_condition, "speaker_count": s.speaker_count,
                        "model": HF_CONFORMER_EN,
                        "preprocessing_enabled": False, "domain_prompt_enabled": False,
                        "forced_language": "en",
                        "duration_audio_seconds": round(dur, 3),
                        "processing_time_seconds": round(elapsed, 3),
                        "real_time_factor": round(rtf, 4),
                        "wer": round(w, 4) if w == w else w,
                        "cer": round(c, 4) if c == c else c,
                        "detected_language": "en",
                        "transcript_output_path": "",
                        "reference_text": ref, "hypothesis_text": hyp, "error": "",
                        "condition_tag": tag_en,
                    })
                    logger.info("  [HF] %s | WER=%.3f CER=%.3f RTF=%.3f",
                                s.audio_filename, w, c, rtf)

                except Exception as e:
                    logger.error("  ERREUR %s : %s", s.audio_filename, e)
                    rows.append(make_error_row(s, HF_CONFORMER_EN, tag_en, str(e)))

            del model
            if device == "cuda":
                torch.cuda.empty_cache()

        except Exception as e:
            logger.error("Impossible de charger HF Conformer EN : %s", e)
            for s in en_samples:
                rows.append(make_error_row(s, HF_CONFORMER_EN, tag_en,
                                           f"MODEL_UNAVAILABLE: {e}"))

    # ── FR / DE : CONFORMER_UNAVAILABLE ────────────────────────────────────
    for lang in ["fr", "de"]:
        tag = f"L_conformer_{lang}"
        msg = (f"CONFORMER_UNAVAILABLE: NeMo non fonctionnel sous Windows "
               f"et aucun modèle Conformer CTC {lang.upper()} disponible via HF "
               f"sans finetuning.")
        logger.warning("%s → %s", lang.upper(), msg)
        for s in samples_by_lang.get(lang, []):
            rows.append(make_error_row(s, f"conformer_ctc_{lang}", tag, msg))

    return rows, "HuggingFace"


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration principale
# ─────────────────────────────────────────────────────────────────────────────

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32
    logger.info("Device : %s  dtype : %s", device, dtype)

    # Chargement des 36 clips canoniques
    samples = [s for s in load_metadata(str(EVAL_METADATA))
               if s.audio_path and s.audio_path.exists()
               and s.reference_path and s.reference_path.exists()]
    logger.info("%d clips valides sur %d listés", len(samples),
                len(load_metadata(str(EVAL_METADATA))))

    samples_by_lang: dict[str, list] = {}
    for s in samples:
        samples_by_lang.setdefault(s.language, []).append(s)

    # ── Sélection du backend ────────────────────────────────────────────────
    nemo_ok = False
    try:
        logger.info("Test import NeMo ASR…")
        import nemo.collections.asr as _nemo_test   # noqa: F401
        nemo_ok = True
        logger.info("  NeMo ASR disponible → plan principal activé")
    except Exception as e:
        logger.warning("  NeMo non disponible (%s) → plan de repli HF", e)

    if nemo_ok:
        rows, backend = run_nemo(samples_by_lang, device)
    else:
        rows, backend = run_hf_conformer(samples_by_lang, device, dtype)

    # ── Écriture CSV ─────────────────────────────────────────────────────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("\nRésultats → %s  (%d lignes)", OUTPUT_CSV, len(rows))

    # ── ÉTAPE 3 : Résumé ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RÉSUMÉ — Conformer CTC baseline")
    print(f"Backend : {backend}")
    print("=" * 70)

    import torch as _torch
    print(f"  torch             : {_torch.__version__}")
    try:
        import nemo as _nemo
        print(f"  nemo_toolkit      : {_nemo.__version__}")
    except ImportError:
        import transformers as _tf
        print(f"  transformers      : {_tf.__version__}")

    print()

    valid = [r for r in rows if not r["error"] and r["wer"] == r["wer"]]
    errors = [r for r in rows if r["error"]]
    unavail = [r for r in errors if "CONFORMER_UNAVAILABLE" in r.get("error", "")]
    real_errors = [r for r in errors if "CONFORMER_UNAVAILABLE" not in r.get("error", "")]

    if valid:
        wers = [r["wer"] for r in valid]
        cers = [r["cer"] for r in valid]
        rtfs = [r["real_time_factor"] for r in valid
                if isinstance(r["real_time_factor"], (int, float))
                and r["real_time_factor"] != float("inf")]

        print(f"  Clips traités     : {len(valid)}/{len(rows)}")
        print(f"  WER moyen global  : {statistics.mean(wers):.3f}")
        print(f"  CER moyen global  : {statistics.mean(cers):.3f}")
        if rtfs:
            print(f"  RTF médian        : {statistics.median(rtfs):.3f}")
        print()

        print(f"  {'Langue':<8} {'N':>4}  {'WER':>8}  {'CER':>8}")
        print(f"  {'-'*34}")
        for lang in ["en", "fr", "de"]:
            lv = [r for r in valid if r["language"] == lang]
            if lv:
                print(f"  {lang:<8} {len(lv):>4}  "
                      f"{statistics.mean(r['wer'] for r in lv):>8.3f}  "
                      f"{statistics.mean(r['cer'] for r in lv):>8.3f}")
        print()

        print(f"  {'Condition':<10} {'N':>4}  {'WER':>8}")
        print(f"  {'-'*28}")
        for cond in ["clean", "noisy"]:
            cv = [r for r in valid if r["noise_condition"] == cond]
            if cv:
                print(f"  {cond:<10} {len(cv):>4}  "
                      f"{statistics.mean(r['wer'] for r in cv):>8.3f}")
    else:
        print("  Aucun clip traité avec succès.")

    if unavail:
        langs_u = sorted(set(r["language"] for r in unavail))
        print(f"\n  CONFORMER_UNAVAILABLE : {', '.join(langs_u).upper()} "
              f"({len(unavail)} clips non évalués)")
        print("  → NeMo non fonctionnel sous Windows ; pas de modèle HF "
              "Conformer CTC FR/DE fine-tuned disponible sans entraînement.")
        print("  → Documenter cette limitation dans la thèse.")

    if real_errors:
        print(f"\n  Erreurs techniques : {len(real_errors)} clips")
        for r in real_errors[:5]:
            print(f"    {r['filename']} : {r['error'][:80]}")

    # Modèles réellement chargés
    loaded_models = sorted({r["model"] for r in rows})
    print(f"\n  Modèle(s) chargé(s) :")
    for m in loaded_models:
        n_clips = sum(1 for r in rows if r["model"] == m)
        print(f"    {m}  ({n_clips} clips)")

    print("=" * 70)

    # ── Aperçu CSV ──────────────────────────────────────────────────────────
    print(f"\nCSV : {OUTPUT_CSV.resolve()}")
    print("\n5 premières lignes :")
    with open(OUTPUT_CSV, encoding="utf-8") as f:
        for i, line in enumerate(f):
            print(" ", line.rstrip())
            if i >= 5:
                break


if __name__ == "__main__":
    main()
