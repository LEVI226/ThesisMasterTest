import numpy as np
import pytest

from study_real_meetings.audio import load_segment, wav_duration, write_wav
from study_real_meetings.noise import mix_at_snr, pick_noise, stable_rng

SR = 16_000


def test_load_segment_returns_requested_span(tmp_path):
    audio = np.linspace(-0.5, 0.5, 3 * SR, dtype=np.float32)
    path = tmp_path / "a.wav"
    write_wav(path, audio)
    assert wav_duration(path) == pytest.approx(3.0)
    chunk = load_segment(path, 1.0, 2.5)
    assert chunk.dtype == np.float32 and len(chunk) == int(1.5 * SR)


@pytest.mark.parametrize("snr", [20.0, 10.0, 5.0, 0.0])
def test_mix_reaches_requested_snr(snr):
    rng = np.random.default_rng(0)
    speech = (0.1 * np.sin(np.arange(SR) / 7.0)).astype(np.float32)
    noise = (0.05 * rng.standard_normal(SR // 3)).astype(np.float32)  # shorter: must be tiled
    mix = mix_at_snr(speech, noise, snr)
    added = mix.astype(np.float64) - speech
    measured = 10 * np.log10(np.mean(speech.astype(np.float64) ** 2) / np.mean(added ** 2))
    assert measured == pytest.approx(snr, abs=0.05)


def test_mix_never_clips():
    speech = np.full(SR, 0.9, dtype=np.float32)
    noise = np.random.default_rng(1).standard_normal(SR).astype(np.float32)
    assert np.max(np.abs(mix_at_snr(speech, noise, 0.0))) <= 0.999 + 1e-6


def test_noise_pick_is_deterministic_and_seed_dependent():
    bank = {"OMEETING": np.arange(100_000, dtype=np.float32),
            "OOFFICE": -np.arange(100_000, dtype=np.float32)}
    a = pick_noise(bank, "agm-fr-0003", 10.0, 1000, seed=1)
    b = pick_noise(bank, "agm-fr-0003", 10.0, 1000, seed=1)
    assert a[0] == b[0] and np.array_equal(a[1], b[1]) and len(a[1]) == 1000
    assert stable_rng(1, "x").integers(1 << 30) == stable_rng(1, "x").integers(1 << 30)
    assert stable_rng(1, "x").integers(1 << 30) != stable_rng(2, "x").integers(1 << 30)
