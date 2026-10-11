"""Real-noise mixing (DEMAND) at a controlled signal-to-noise ratio."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf

from study_real_meetings.config import DEMAND_ENVS, SAMPLE_RATE


def stable_rng(*parts) -> np.random.Generator:
    digest = hashlib.sha256(":".join(map(str, parts)).encode("utf-8")).hexdigest()
    return np.random.default_rng(int(digest[:16], 16))


def mix_at_snr(speech: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    if len(noise) < len(speech):
        noise = np.tile(noise, int(np.ceil(len(speech) / len(noise))))
    s = speech.astype(np.float64)
    n = noise[: len(speech)].astype(np.float64)
    p_speech, p_noise = np.mean(s ** 2), np.mean(n ** 2)
    if p_speech == 0 or p_noise == 0:
        return speech.astype(np.float32).copy()
    scale = np.sqrt(p_speech / (p_noise * 10 ** (snr_db / 10)))
    mix = s + scale * n
    peak = np.max(np.abs(mix))
    if peak > 0.999:
        mix *= 0.999 / peak  # scales speech and noise together: SNR unchanged
    return mix.astype(np.float32)


def pick_noise(bank: dict[str, np.ndarray], segment_id: str, snr_db: float,
               n_samples: int, seed: int) -> tuple[str, np.ndarray]:
    rng = stable_rng(seed, segment_id, snr_db)
    kinds = sorted(bank)
    kind = kinds[int(rng.integers(len(kinds)))]
    source = bank[kind]
    if len(source) <= n_samples:
        return kind, source
    offset = int(rng.integers(0, len(source) - n_samples))
    return kind, source[offset : offset + n_samples]


def load_demand_bank(demand_dir: Path) -> dict[str, np.ndarray]:
    bank: dict[str, np.ndarray] = {}
    for env in DEMAND_ENVS:
        path = next(p for p in demand_dir.rglob("ch01.wav") if p.parent.name == env)
        audio, sr = sf.read(str(path), dtype="float32", always_2d=False)
        if sr != SAMPLE_RATE:
            raise ValueError(f"{path}: {sr} Hz, expected {SAMPLE_RATE}")
        bank[env] = audio if audio.ndim == 1 else audio[:, 0]
    return bank
