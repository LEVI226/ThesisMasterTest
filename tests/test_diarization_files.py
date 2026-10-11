"""File diarization uses decoded audio and accepts both pyannote output formats."""
from types import SimpleNamespace

import numpy as np
import pytest
import soundfile as sf
from backend.stt import engine


@pytest.mark.parametrize("wrapped", [False, True])
def test_file_speaker_assignment_uses_waveform_and_supported_output(monkeypatch, tmp_path, wrapped):
    audio = tmp_path / "stereo_8k.wav"
    sf.write(audio, np.zeros((8000, 2), dtype=np.float32), 8000)
    calls = []

    class Diarizer:
        def __call__(self, source):
            calls.append(source)
            assert isinstance(source, dict), "Use decoded waveform, not TorchCodec path decoding"
            assert source["sample_rate"] == 16000
            assert source["waveform"].shape == (1, 16000)
            assert source["waveform"].device.type == "cpu"
            annotation = SimpleNamespace(itertracks=lambda **kw: iter([
                (SimpleNamespace(start=0.0, end=1.0), None, "SPEAKER_00")
            ]))
            return SimpleNamespace(speaker_diarization=annotation) if wrapped else annotation

    fake_model = SimpleNamespace(transcribe=lambda *a, **kw: (
        iter([SimpleNamespace(start=0.0, end=1.0, text="Bonjour")]),
        SimpleNamespace(language="fr"),
    ))
    monkeypatch.setattr(engine, "load_model", lambda *a: fake_model)
    monkeypatch.setattr(engine, "load_diarization_pipeline", lambda: Diarizer())
    result = engine.transcribe_file(str(audio), config=engine.TranscribeConfig(preprocessing=False))
    assert len(calls) == 1
    assert result["segments"][0]["speaker"] == "SPEAKER_00"
