"""Regression tests for three contract defects found in the 2026-09-16 audit.

All ASR / VAD / RAG dependencies are faked. These tests establish that the
software contract holds; they say nothing about transcription quality.
"""
import asyncio
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest
import torch
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient


# ---------------------------------------------------------------- fixtures
@pytest.fixture
def fake_engine():
    """A backend.stt.engine stand-in that records the forced language."""
    engine = ModuleType("backend.stt.engine")
    engine.calls = []

    def transcribe_file(path, forced_language=None, **kw):
        engine.calls.append(forced_language)
        return {"text": "ok", "language": forced_language or "auto"}

    class Vad:
        def __call__(self, *a):
            return torch.tensor(1.0)

        def reset_states(self):
            pass

    engine.transcribe_file = transcribe_file
    engine._model = object()
    engine._vad_model = Vad()
    engine._diarization_pipeline = None
    engine.get_model_info = lambda: {"model": "fake", "device": "cpu", "compute_type": "int8",
                                     "cuda_available": False, "gpu_name": None,
                                     "vad_loaded": True, "diarization_loaded": False}
    return engine


@pytest.fixture
def app_client(fake_engine, tmp_path):
    vector = ModuleType("backend.rag.vectorstore")
    vector.ingest = lambda *a: 1
    with patch.dict(sys.modules, {"backend.stt.engine": fake_engine,
                                  "backend.rag.vectorstore": vector}):
        import backend.main as main
        with patch.object(main, "UPLOAD_DIR", tmp_path):
            yield TestClient(main.app), fake_engine, main


# ---------------------------------------------------------------- defect 1
def test_transcribe_forwards_language_from_multipart_form(app_client):
    client, engine, _ = app_client
    r = client.post("/transcribe",
                    files={"file": ("a.wav", b"x", "audio/wav")},
                    data={"language": "fr"})
    assert r.status_code == 200
    assert engine.calls[-1] == "fr"


def test_transcribe_still_accepts_language_in_query_string(app_client):
    client, engine, _ = app_client
    r = client.post("/transcribe?language=de",
                    files={"file": ("a.wav", b"x", "audio/wav")})
    assert r.status_code == 200
    assert engine.calls[-1] == "de"


def test_transcribe_without_language_means_auto_detect(app_client):
    client, engine, _ = app_client
    client.post("/transcribe", files={"file": ("a.wav", b"x", "audio/wav")})
    assert engine.calls[-1] is None


# ---------------------------------------------------------------- defect 2
class _Socket:
    """Minimal WebSocket stand-in driven by a scripted message list."""

    def __init__(self, script):
        self.script = list(script)
        self.sent = []

    async def accept(self):
        pass

    async def receive(self):
        if not self.script:
            return {"type": "websocket.disconnect"}
        item = self.script.pop(0)
        if item == "DISCONNECT":
            raise WebSocketDisconnect()
        if isinstance(item, bytes):
            return {"type": "websocket.receive", "bytes": item}
        return {"type": "websocket.receive", "text": item}

    async def send_json(self, obj):
        self.sent.append(obj)

    async def close(self, code=1000):
        pass


SPEECH_1S = (np.ones(16000, dtype=np.int16) * 1000).tobytes()


def _run(handler):
    return asyncio.run(handler.process())


def test_pending_speech_is_flushed_when_client_disconnects(app_client):
    _, _, main = app_client
    h = main.RealTimeSTTHandler(_Socket([SPEECH_1S, "DISCONNECT"]))
    h._transcribe_and_diarize = AsyncMock()
    _run(h)
    assert h._transcribe_and_diarize.await_count == 1
    assert len(h.audio_buffer) == 0


def test_end_signal_flushes_and_acknowledges(app_client):
    _, _, main = app_client
    sock = _Socket([SPEECH_1S, "__end__"])
    h = main.RealTimeSTTHandler(sock)
    h._transcribe_and_diarize = AsyncMock()
    _run(h)
    # flushed once on the signal; the disconnect that follows has nothing left
    assert h._transcribe_and_diarize.await_count == 1
    assert {"type": "flushed"} in sock.sent


def test_end_signal_with_empty_buffer_is_harmless(app_client):
    _, _, main = app_client
    sock = _Socket(["__end__"])
    h = main.RealTimeSTTHandler(sock)
    h._transcribe_and_diarize = AsyncMock()
    _run(h)
    assert h._transcribe_and_diarize.await_count == 0
    assert {"type": "flushed"} in sock.sent


def test_latency_csv_path_comes_from_environment(app_client, tmp_path, monkeypatch):
    _, _, main = app_client
    target = tmp_path / "session" / "latency.csv"
    monkeypatch.setenv("LIVE_LATENCY_CSV", str(target))
    h = main.RealTimeSTTHandler(_Socket([]))
    assert h.latency_csv == target
    monkeypatch.delenv("LIVE_LATENCY_CSV")
    h2 = main.RealTimeSTTHandler(_Socket([]))
    assert h2.latency_csv == Path("results/live_latency.csv")


# ---------------------------------------------------------------- defect 3
@pytest.fixture
def runner_env(tmp_path, monkeypatch):
    """Fake engine returning the model size it was asked for; isolated output dir."""
    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path / "transcripts"))
    engine = ModuleType("backend.stt.engine")

    class Cfg:
        def __init__(self, preprocessing, domain_prompt, language, word_timestamps, vad):
            self.preprocessing, self.domain_prompt = preprocessing, domain_prompt
            self.language, self.vad = language, vad
            self.model_size = "default"

    def transcribe_file(path, config):
        return {"text": f"hyp-{config.model_size}-vad{int(config.vad)}",
                "model": config.model_size, "language": config.language or "auto"}

    engine.TranscribeConfig = Cfg
    engine.transcribe_file = transcribe_file
    engine.get_audio_duration = lambda p: 1.0

    audio = tmp_path / "s.wav"
    audio.write_bytes(b"x")
    ref = tmp_path / "s.txt"
    ref.write_text("hello", encoding="utf-8")

    class Sample:
        audio_filename = "s.wav"
        audio_path = audio
        reference_path = ref
        language, noise_condition, speaker_count = "en", "clean", 1

    with patch.dict(sys.modules, {"backend.stt.engine": engine}):
        import importlib
        import backend.evaluation.runner as runner
        importlib.reload(runner)          # pick up TRANSCRIPT_DIR from env
        yield runner, Sample()


def test_transcript_paths_differ_between_models(runner_env):
    runner, sample = runner_env
    a = runner.run_single(sample, model_size="tiny")
    b = runner.run_single(sample, model_size="base")
    assert a.transcript_output_path != b.transcript_output_path
    assert Path(a.transcript_output_path).read_text(encoding="utf-8") == "hyp-tiny-vad0"
    assert Path(b.transcript_output_path).read_text(encoding="utf-8") == "hyp-base-vad0"


def test_transcript_paths_differ_between_vad_settings(runner_env):
    runner, sample = runner_env
    a = runner.run_single(sample, model_size="tiny", vad=False)
    b = runner.run_single(sample, model_size="tiny", vad=True)
    assert a.transcript_output_path != b.transcript_output_path
    assert "_vad1" in b.transcript_output_path and "_vad0" in a.transcript_output_path


def test_transcript_dir_honours_environment(runner_env, tmp_path):
    runner, sample = runner_env
    r = runner.run_single(sample, model_size="tiny")
    assert Path(r.transcript_output_path).parent == tmp_path / "transcripts"


# ---------------------------------------------------------------- session log
def test_session_log_written_when_dir_is_set(app_client, tmp_path, monkeypatch):
    import json
    _, _, main = app_client
    monkeypatch.setenv("STT_SESSION_LOG_DIR", str(tmp_path / "sessions"))
    sock = _Socket([SPEECH_1S, "__end__"])
    h = main.RealTimeSTTHandler(sock, language="fr")
    h._transcribe_and_diarize = AsyncMock()
    _run(h)
    files = list((tmp_path / "sessions").glob("live_*.jsonl"))
    assert len(files) == 1
    events = [json.loads(l) for l in files[0].read_text(encoding="utf-8").splitlines()]
    assert events[0]["event"] == "session_start"
    assert events[0]["options"]["language"] == "fr"
    assert "latency_seconds" in events[0]["clock_domains"]
    assert events[-1]["event"] == "session_end"
    assert events[-1]["chunks"]["count"] == 1
    assert events[-1]["chunks"]["bytes"] == len(SPEECH_1S)


def test_session_log_disabled_without_dir(app_client, monkeypatch):
    _, _, main = app_client
    monkeypatch.delenv("STT_SESSION_LOG_DIR", raising=False)
    h = main.RealTimeSTTHandler(_Socket([]), language=None)
    assert h.slog.path is None
    h.slog.event("utterance", text="x")   # must be a no-op, not an error


# ---------------------------------------------------------------- stop scenarios (review 2026-09-16)
RESIDUAL_04S = (np.ones(6400, dtype=np.int16) * 1000).tobytes()   # 0.4 s, less than one 1 s packet


def test_residual_packet_shorter_than_one_second_is_flushed(app_client):
    """The browser now sends its < 1 s residual before __end__; the server must transcribe it."""
    _, _, main = app_client
    sock = _Socket([RESIDUAL_04S, "__end__"])
    h = main.RealTimeSTTHandler(sock)
    seen = []
    async def fake(model, diarizer):
        seen.append(len(h.audio_buffer))
    h._transcribe_and_diarize = fake
    _run(h)
    assert seen == [len(RESIDUAL_04S)]
    assert {"type": "flushed"} in sock.sent


def test_flushed_ack_is_sent_only_after_a_slow_flush_completes(app_client):
    """A decode longer than the old 2 s browser cap must still precede the ack."""
    _, _, main = app_client
    sock = _Socket([SPEECH_1S, "__end__"])
    h = main.RealTimeSTTHandler(sock)
    order = []
    async def slow(model, diarizer):
        await asyncio.sleep(2.3)
        await sock.send_json({"speaker": "S", "text": "last words", "start": 0, "end": 1})
        order.append("transcribed")
    h._transcribe_and_diarize = slow
    orig_send = sock.send_json
    async def send(o):
        if o.get("type") == "flushed":
            order.append("ack")
        await orig_send(o)
    sock.send_json = send
    _run(h)
    assert order == ["transcribed", "ack"]
    texts = [m for m in sock.sent if "text" in m]
    assert len(texts) == 1 and texts[0]["text"] == "last words"


def test_stop_then_disconnect_does_not_duplicate_the_last_utterance(app_client):
    """Stop Recording sends __end__; Disconnect sends it again: one transcription only."""
    _, _, main = app_client
    sock = _Socket([SPEECH_1S, "__end__", "__end__", "DISCONNECT"])
    h = main.RealTimeSTTHandler(sock)
    h._transcribe_and_diarize = AsyncMock()
    _run(h)
    assert h._transcribe_and_diarize.await_count == 1
    assert sum(1 for m in sock.sent if m.get("type") == "flushed") == 2


def test_file_path_writes_a_session_log(app_client, tmp_path, monkeypatch):
    import json
    client, _, _ = app_client
    monkeypatch.setenv("STT_SESSION_LOG_DIR", str(tmp_path / "sessions"))
    r = client.post("/transcribe", files={"file": ("a.wav", b"x", "audio/wav")}, data={"language": "fr"})
    assert r.status_code == 200
    assert r.json()["diarization_available"] is False
    files = list((tmp_path / "sessions").glob("file_*.jsonl"))
    assert len(files) == 1
    events = [json.loads(l) for l in files[0].read_text(encoding="utf-8").splitlines()]
    assert [e["event"] for e in events] == ["session_start", "transcribed", "session_end"]
    assert events[0]["options"]["forced_language"] == "fr"
    assert events[1]["detected_language"] == "fr" and events[1]["text"] == "ok"
