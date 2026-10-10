"""Drive the REAL live handler (real Silero VAD + real Whisper) with a WAV file
pushed as 1-second 16 kHz PCM chunks, the way the browser does. No microphone,
no browser, no network: this checks the server-side live path, including the
end-of-stream flush that preserves the last sentence.

Three scenarios per file:
  end_signal  : chunks, then the text frame "__end__", then disconnect
  disconnect  : chunks, then immediate disconnect (no silence, no signal)
  silence     : chunks, then 1.5 s of digital silence (natural VAD end)

Outputs go only to this run folder (LIVE_LATENCY_CSV + STT_SESSION_LOG_DIR).
"""
import asyncio, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).parent
os.environ["LIVE_LATENCY_CSV"] = str(OUT / "live_latency_validation_PRISTINE.csv")
os.environ["STT_SESSION_LOG_DIR"] = str(OUT / "sessions")

import numpy as np
import librosa
from fastapi import WebSocketDisconnect
import backend.stt.engine as engine
from backend.evaluation.metrics import wer
import importlib.util
spec = importlib.util.spec_from_file_location("main_pristine", OUT / "pristine" / "main_pristine.py")
main = importlib.util.module_from_spec(spec); spec.loader.exec_module(main)
main.RealTimeSTTHandler.LATENCY_CSV = OUT / "live_latency_validation_PRISTINE.csv"  # never the historical file

SR = 16000
FILES = [("minds14_fr_clean_01", "fr"), ("minds14_en_clean_01", "en"), ("minds14_de_clean_01", "de")]


def pcm_chunks(stem):
    y, _ = librosa.load(str(ROOT / f"datasets/stt_eval/audio/{stem}.wav"), sr=SR, mono=True)
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    return [pcm[i:i + SR].tobytes() for i in range(0, len(pcm), SR)]


class Socket:
    def __init__(self, script):
        self.script = list(script); self.sent = []; self.t_first_send = None

    async def accept(self): pass

    async def receive(self):
        if not self.script:
            return {"type": "websocket.disconnect"}
        it = self.script.pop(0)
        if it == "DISCONNECT":
            raise WebSocketDisconnect()
        if isinstance(it, bytes):
            await asyncio.sleep(0)          # yield like a real socket would
            return {"type": "websocket.receive", "bytes": it}
        return {"type": "websocket.receive", "text": it}

    async def receive_bytes(self):
        m = await self.receive()
        if m.get("type") == "websocket.disconnect" or "bytes" not in m:
            raise WebSocketDisconnect()
        return m["bytes"]

    async def send_json(self, o):
        self.sent.append(o)

    async def close(self, code=1000): pass


async def run(stem, lang, scenario, language=None):
    chunks = pcm_chunks(stem)
    silence = (np.zeros(int(SR * 1.5), dtype=np.int16)).tobytes()
    script = {"end_signal": chunks + ["__end__"],
              "disconnect": chunks + ["DISCONNECT"],
              "silence": chunks + [silence]}[scenario]
    sock = Socket(script)
    h = main.RealTimeSTTHandler(sock, language=language)
    t0 = time.perf_counter()
    await h.process()
    wall = round(time.perf_counter() - t0, 3)
    utts = [m for m in sock.sent if "text" in m]
    text = " ".join(m["text"] for m in utts).strip()
    ref = (ROOT / f"datasets/stt_eval/references/{stem}.txt").read_text(encoding="utf-8").strip()
    return {"file": stem, "true_language": lang, "forced_language": language, "scenario": scenario,
            "chunks_sent": len(chunks), "utterances_delivered": len(utts),
            "flushed_ack": any(m.get("type") == "flushed" for m in sock.sent),
            "text": text, "reference": ref, "wer": round(wer(ref, text), 4) if text else None,
            "wall_s": wall, "session_log": None}


async def main_():
    engine.load_model("small"); engine.load_vad_model()
    # the handler imports these names from the engine module at call time
    info = engine.get_model_info()
    print("loaded:", info)
    rows = []
    for stem, lang in FILES:
        for sc in ("end_signal", "disconnect", "silence"):
            r = await run(stem, lang, sc)
            rows.append(r)
            print(f"  {stem:22s} {sc:10s} utt={r['utterances_delivered']} ack={r['flushed_ack']!s:5s} "
                  f"WER={r['wer']!s:6s} {r['text'][:55]!r}")
    # forced-language variant on one file, end_signal scenario
    r = await run("minds14_de_clean_01", "de", "end_signal", language="de")
    rows.append(r); print(f"  {'de forced':22s} end_signal utt={r['utterances_delivered']} WER={r['wer']} {r['text'][:55]!r}")
    rep = {"scope": "PRISTINE handler (before fixes); real VAD + real Whisper small through RealTimeSTTHandler; fake socket; no browser/mic/network; diarization not loaded",
           "model_loaded": info, "rows": rows,
           "latency_csv": os.environ["LIVE_LATENCY_CSV"], "session_log_dir": os.environ["STT_SESSION_LOG_DIR"]}
    (OUT / "05_live_sim_PRISTINE.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print("written:", OUT / "05_live_sim_PRISTINE.json")

asyncio.run(main_())
