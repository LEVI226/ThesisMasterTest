"""Transcribe the 11 en/fr MInDS-14 clean control clips."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from stt.engine import TranscribeConfig, transcribe_file  # noqa: E402

FILES = [
    ("minds14_en_clean_04.wav", "en"),
    ("minds14_en_clean_05.wav", "en"),
    ("minds14_en_clean_06.wav", "en"),
    ("minds14_en_clean_08.wav", "en"),
    ("minds14_fr_clean_01.wav", "fr"),
    ("minds14_fr_clean_02.wav", "fr"),
    ("minds14_fr_clean_04.wav", "fr"),
    ("minds14_fr_clean_05.wav", "fr"),
    ("minds14_fr_clean_06.wav", "fr"),
    ("minds14_fr_clean_07.wav", "fr"),
    ("minds14_fr_clean_08.wav", "fr"),
]

audio = ROOT / "datasets/stt_eval/audio"

for name, lang in FILES:
    cfg = TranscribeConfig(
        language=lang,
        preprocessing=False,
        domain_prompt=False,
        vad=False,
        model_size="large-v3",
    )
    result = transcribe_file(str(audio / name), config=cfg)
    print(f"=== {name} ({lang}) ===")
    print(result["text"])
    print()
