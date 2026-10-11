"""Audio helpers. All study audio is 16 kHz mono PCM-16 wav."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from study_real_meetings.config import SAMPLE_RATE


def convert_to_wav16k(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(src),
         "-ac", "1", "-ar", str(SAMPLE_RATE), "-sample_fmt", "s16", str(dst)],
        check=True,
    )


def load_segment(path: Path, start: float, end: float) -> np.ndarray:
    info = sf.info(str(path))
    if info.samplerate != SAMPLE_RATE:
        raise ValueError(f"{path} is {info.samplerate} Hz, expected {SAMPLE_RATE}")
    audio, _ = sf.read(
        str(path),
        start=int(round(start * SAMPLE_RATE)),
        stop=int(round(end * SAMPLE_RATE)),
        dtype="float32",
        always_2d=False,
    )
    return audio.mean(axis=1).astype(np.float32) if audio.ndim > 1 else audio


def write_wav(path: Path, audio: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.clip(audio, -1.0, 1.0), SAMPLE_RATE, subtype="PCM_16")


def wav_duration(path: Path) -> float:
    info = sf.info(str(path))
    return info.frames / info.samplerate
