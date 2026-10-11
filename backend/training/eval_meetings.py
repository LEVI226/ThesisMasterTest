"""
TÂCHE B.2 — BLOC 7 : Diarisation pyannote sur les 7 réunions simulées.

Pour chaque réunion :
  1. Chargement WAV via librosa → dict en mémoire (bypass torchcodec)
  2. Pipeline pyannote/speaker-diarization-3.1
  3. DER calculé avec pyannote.metrics.diarization
  4. Cartographie optimale hypothèse → référence (via pyannote.metrics interne)

Sortie : results/meeting_eval_results.csv
"""
import csv
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import torch
import librosa
from pyannote.audio import Pipeline
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path("datasets/meetings/audio")
GT_PATH      = Path("datasets/meetings/ground_truth.json")
OUTPUT_CSV   = Path("results/meeting_eval_results.csv")

FIELDNAMES = [
    "meeting_id", "language", "noise_condition", "n_speakers",
    "total_duration_s", "n_ref_segments",
    "der", "missed_speech", "false_alarm", "confusion",
    "n_hyp_segments", "hyp_n_speakers",
    "limitation",
]

LIMITATION = (
    "Sequential turns, no overlap — weak diarization testbed; "
    "cross-talk not tested."
)


def build_reference(segments: list[dict]) -> Annotation:
    """Construit l'Annotation pyannote à partir du ground truth JSON."""
    ref = Annotation()
    for seg in segments:
        ref[Segment(seg["start"], seg["end"])] = seg["speaker"]
    return ref


def load_audio_for_pyannote(wav_path: Path) -> dict:
    """
    Charge un WAV avec librosa → dict en mémoire pour pyannote.
    Bypass total torchcodec / FFmpeg DLL manquantes.
    Format attendu : {"waveform": (1, N) float32 tensor, "sample_rate": int}
    """
    arr, sr = librosa.load(str(wav_path), sr=16_000, mono=True)
    waveform = torch.from_numpy(arr).unsqueeze(0).float()   # (1, N)
    return {"waveform": waveform, "sample_rate": sr}


def main():
    hf_token = os.getenv("HF_TOKEN", "")
    if not hf_token:
        logger.warning("HF_TOKEN manquant — pyannote pourrait échouer sur modèles privés.")

    logger.info("Chargement pyannote/speaker-diarization-3.1…")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=hf_token,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipeline.to(device)
    logger.info("  OK — pipeline sur %s", device)

    with open(GT_PATH, encoding="utf-8") as f:
        ground_truth: list[dict] = json.load(f)

    metric = DiarizationErrorRate()
    rows = []

    for meeting in ground_truth:
        mid      = meeting["meeting_id"]
        wav_path = MEETINGS_DIR / meeting["audio_file"]

        if not wav_path.exists():
            logger.error("  WAV manquant : %s — skipping", wav_path)
            continue

        logger.info("\n--- %s ---", mid)
        try:
            audio_input = load_audio_for_pyannote(wav_path)
            raw = pipeline(audio_input)
            # pyannote.audio 4.x retourne DiarizeOutput — extraire l'Annotation
            diarization: Annotation = (
                raw.speaker_diarization if hasattr(raw, "speaker_diarization") else raw
            )

            reference = build_reference(meeting["segments"])

            # DER avec cartographie optimale des locuteurs (interne à pyannote.metrics)
            components = metric(reference, diarization, detailed=True)
            der_val    = components["diarization error rate"]
            missed     = components["missed detection"]
            fa         = components["false alarm"]
            confusion  = components["confusion"]
            ref_total  = components["total"]

            hyp_turns    = list(diarization.itertracks(yield_label=True))
            hyp_n_spk    = len(set(item[2] for item in hyp_turns))

            logger.info(
                "  DER=%.3f  missed=%.3f  FA=%.3f  confusion=%.3f  (ref_total=%.1fs)",
                der_val, missed / ref_total if ref_total else 0,
                fa / ref_total if ref_total else 0,
                confusion / ref_total if ref_total else 0,
                ref_total,
            )
            logger.info(
                "  Hyp: %d segments, %d locuteurs | Ref: %d locuteurs",
                len(hyp_turns), hyp_n_spk, meeting["n_speakers"]
            )

            rows.append({
                "meeting_id":       mid,
                "language":         meeting["language"],
                "noise_condition":  meeting["noise_condition"],
                "n_speakers":       meeting["n_speakers"],
                "total_duration_s": round(meeting["total_duration"], 2),
                "n_ref_segments":   len(meeting["segments"]),
                "der":              round(der_val, 4),
                "missed_speech":    round(missed / ref_total, 4) if ref_total else float("nan"),
                "false_alarm":      round(fa / ref_total, 4)     if ref_total else float("nan"),
                "confusion":        round(confusion / ref_total, 4) if ref_total else float("nan"),
                "n_hyp_segments":   len(hyp_turns),
                "hyp_n_speakers":   hyp_n_spk,
                "limitation":       LIMITATION,
            })

        except Exception as e:
            logger.error("  ERREUR %s : %s", mid, e)
            rows.append({
                "meeting_id":       mid,
                "language":         meeting["language"],
                "noise_condition":  meeting["noise_condition"],
                "n_speakers":       meeting["n_speakers"],
                "total_duration_s": round(meeting.get("total_duration", 0), 2),
                "n_ref_segments":   len(meeting.get("segments", [])),
                "der":              float("nan"),
                "missed_speech":    float("nan"),
                "false_alarm":      float("nan"),
                "confusion":        float("nan"),
                "n_hyp_segments":   0,
                "hyp_n_speakers":   0,
                "limitation":       LIMITATION,
            })

    # ── Écriture CSV ─────────────────────────────────────────────────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("\nRésultats diarisation → %s (%d lignes)", OUTPUT_CSV, len(rows))

    # ── Résumé final ──────────────────────────────────────────────────────
    valid = [r for r in rows if r["der"] == r["der"]]
    if valid:
        import statistics
        ders = [r["der"] for r in valid]
        print(f"\n=== RÉSUMÉ DIARISATION ({len(valid)}/7 réunions) ===")
        print(f"  DER moyen   : {statistics.mean(ders):.3f}")
        print(f"  DER médiane : {statistics.median(ders):.3f}")
        print()
        print(f"  {'Réunion':<35} {'DER':>6} {'Missed':>8} {'FA':>6} {'Conf.':>8} {'HypSpk':>7}")
        print(f"  {'-'*70}")
        for r in valid:
            print(f"  {r['meeting_id']:<35} {r['der']:>6.3f} "
                  f"{r['missed_speech']:>8.3f} {r['false_alarm']:>6.3f} "
                  f"{r['confusion']:>8.3f} {r['hyp_n_speakers']:>7}")
        print()
        print(f"  Limitation : {LIMITATION}")


if __name__ == "__main__":
    main()
