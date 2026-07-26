"""
TÂCHE B.1 — BLOC 7 : Construction de réunions simulées pour la diarisation.

7 réunions construites par concaténation séquentielle de clips MInDS-14 :
  meeting_en_clean_2spk   — 8 clips EN clean   (SPEAKER_A : impairs, SPEAKER_B : pairs)
  meeting_fr_clean_2spk   — 8 clips FR clean
  meeting_de_clean_2spk   — 8 clips DE clean
  meeting_en_noisy_2spk   — 4 clips EN noisy
  meeting_fr_noisy_2spk   — 4 clips FR noisy
  meeting_de_noisy_2spk   — 4 clips DE noisy
  meeting_trilingual_3spk — 6 clips trilingues EN+FR+DE (tour : A,B,C,A,B,C)

Entre chaque tour : 0,5 s de silence.
Limitation documentée : tours séquentiels, aucun chevauchement — testbed faible,
  cross-talk et hallucinations de locuteur non couverts.

Sorties :
  datasets/meetings/audio/*.wav
  datasets/meetings/ground_truth.json
"""
import json
import logging
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUDIO_SRC = Path("datasets/stt_eval/audio")
REF_SRC   = Path("datasets/stt_eval/references")
OUT_DIR   = Path("datasets/meetings/audio")
GT_PATH   = Path("datasets/meetings/ground_truth.json")
SR        = 16_000
SILENCE_S = 0.5

SILENCE = np.zeros(int(SR * SILENCE_S), dtype=np.float32)


def load_clip(filename: str) -> np.ndarray:
    arr, _ = librosa.load(str(AUDIO_SRC / filename), sr=SR, mono=True)
    return arr.astype(np.float32)


def load_ref(stem: str) -> str:
    p = REF_SRC / f"{stem}.txt"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def build_meeting(clips: list[tuple[str, str, str]]) -> tuple[np.ndarray, list[dict]]:
    """
    clips : liste de (filename_without_ext, speaker_id, language)
    Retourne (audio_array, segments) avec timing précis.
    """
    arrays, segments = [], []
    offset = 0.0

    for stem, speaker, lang in clips:
        wav_name = f"{stem}.wav"
        arr = load_clip(wav_name)
        duration = len(arr) / SR
        transcript = load_ref(stem)

        segments.append({
            "start":       round(offset, 4),
            "end":         round(offset + duration, 4),
            "speaker":     speaker,
            "language":    lang,
            "transcript":  transcript,
            "source_clip": wav_name,
        })

        arrays.append(arr)
        arrays.append(SILENCE)
        offset += duration + SILENCE_S

    audio = np.concatenate(arrays)
    return audio, segments


MEETINGS = [
    {
        "meeting_id":     "meeting_en_clean_2spk",
        "language":       "en",
        "noise_condition": "clean",
        "n_speakers":     2,
        "clips": [
            ("minds14_en_clean_01", "SPEAKER_A", "en"),
            ("minds14_en_clean_02", "SPEAKER_B", "en"),
            ("minds14_en_clean_03", "SPEAKER_A", "en"),
            ("minds14_en_clean_04", "SPEAKER_B", "en"),
            ("minds14_en_clean_05", "SPEAKER_A", "en"),
            ("minds14_en_clean_06", "SPEAKER_B", "en"),
            ("minds14_en_clean_07", "SPEAKER_A", "en"),
            ("minds14_en_clean_08", "SPEAKER_B", "en"),
        ],
    },
    {
        "meeting_id":     "meeting_fr_clean_2spk",
        "language":       "fr",
        "noise_condition": "clean",
        "n_speakers":     2,
        "clips": [
            ("minds14_fr_clean_01", "SPEAKER_A", "fr"),
            ("minds14_fr_clean_02", "SPEAKER_B", "fr"),
            ("minds14_fr_clean_03", "SPEAKER_A", "fr"),
            ("minds14_fr_clean_04", "SPEAKER_B", "fr"),
            ("minds14_fr_clean_05", "SPEAKER_A", "fr"),
            ("minds14_fr_clean_06", "SPEAKER_B", "fr"),
            ("minds14_fr_clean_07", "SPEAKER_A", "fr"),
            ("minds14_fr_clean_08", "SPEAKER_B", "fr"),
        ],
    },
    {
        "meeting_id":     "meeting_de_clean_2spk",
        "language":       "de",
        "noise_condition": "clean",
        "n_speakers":     2,
        "clips": [
            ("minds14_de_clean_01", "SPEAKER_A", "de"),
            ("minds14_de_clean_02", "SPEAKER_B", "de"),
            ("minds14_de_clean_03", "SPEAKER_A", "de"),
            ("minds14_de_clean_04", "SPEAKER_B", "de"),
            ("minds14_de_clean_05", "SPEAKER_A", "de"),
            ("minds14_de_clean_06", "SPEAKER_B", "de"),
            ("minds14_de_clean_07", "SPEAKER_A", "de"),
            ("minds14_de_clean_08", "SPEAKER_B", "de"),
        ],
    },
    {
        "meeting_id":     "meeting_en_noisy_2spk",
        "language":       "en",
        "noise_condition": "noisy",
        "n_speakers":     2,
        "clips": [
            ("minds14_en_noisy_01", "SPEAKER_A", "en"),
            ("minds14_en_noisy_02", "SPEAKER_B", "en"),
            ("minds14_en_noisy_03", "SPEAKER_A", "en"),
            ("minds14_en_noisy_04", "SPEAKER_B", "en"),
        ],
    },
    {
        "meeting_id":     "meeting_fr_noisy_2spk",
        "language":       "fr",
        "noise_condition": "noisy",
        "n_speakers":     2,
        "clips": [
            ("minds14_fr_noisy_01", "SPEAKER_A", "fr"),
            ("minds14_fr_noisy_02", "SPEAKER_B", "fr"),
            ("minds14_fr_noisy_03", "SPEAKER_A", "fr"),
            ("minds14_fr_noisy_04", "SPEAKER_B", "fr"),
        ],
    },
    {
        "meeting_id":     "meeting_de_noisy_2spk",
        "language":       "de",
        "noise_condition": "noisy",
        "n_speakers":     2,
        "clips": [
            ("minds14_de_noisy_01", "SPEAKER_A", "de"),
            ("minds14_de_noisy_02", "SPEAKER_B", "de"),
            ("minds14_de_noisy_03", "SPEAKER_A", "de"),
            ("minds14_de_noisy_04", "SPEAKER_B", "de"),
        ],
    },
    {
        "meeting_id":     "meeting_trilingual_3spk",
        "language":       "mixed",
        "noise_condition": "clean",
        "n_speakers":     3,
        # SPEAKER_A=EN, SPEAKER_B=FR, SPEAKER_C=DE — tour : A,B,C,A,B,C
        "clips": [
            ("minds14_en_clean_01", "SPEAKER_A", "en"),
            ("minds14_fr_clean_01", "SPEAKER_B", "fr"),
            ("minds14_de_clean_01", "SPEAKER_C", "de"),
            ("minds14_en_clean_02", "SPEAKER_A", "en"),
            ("minds14_fr_clean_02", "SPEAKER_B", "fr"),
            ("minds14_de_clean_02", "SPEAKER_C", "de"),
        ],
    },
]

LIMITATION = (
    "Sequential turns, no overlap — simulated meeting (weak diarization testbed). "
    "Cross-talk, interruptions, and speaker overlap not tested. "
    "Each turn is an isolated telephone-banking utterance — content continuity is not guaranteed."
)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GT_PATH.parent.mkdir(parents=True, exist_ok=True)

    ground_truth = []

    for meeting in MEETINGS:
        mid = meeting["meeting_id"]
        out_wav = OUT_DIR / f"{mid}.wav"

        audio, segments = build_meeting(meeting["clips"])
        sf.write(str(out_wav), audio, SR)

        total_s = len(audio) / SR
        logger.info(
            "%s  →  %.1f s, %d tours, %d loc.",
            mid, total_s, len(segments), meeting["n_speakers"]
        )

        ground_truth.append({
            "meeting_id":     mid,
            "audio_file":     f"{mid}.wav",
            "language":       meeting["language"],
            "noise_condition": meeting["noise_condition"],
            "n_speakers":     meeting["n_speakers"],
            "total_duration": round(total_s, 3),
            "limitation":     LIMITATION,
            "segments":       segments,
        })

    with open(GT_PATH, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, ensure_ascii=False, indent=2)

    logger.info("\n%d réunions → %s", len(ground_truth), OUT_DIR)
    logger.info("Ground truth → %s", GT_PATH)
    for m in ground_truth:
        logger.info(
            "  %-35s  %.1f s  %d spk  %d seg",
            m["meeting_id"], m["total_duration"], m["n_speakers"], len(m["segments"])
        )


if __name__ == "__main__":
    main()
