"""Does the last sentence survive when the stream stops mid-speech?

The earlier simulation (05_live_sim) could not tell: MInDS-14 clips end with
>= 0.6 s of natural silence, so the VAD fired before the disconnect. Here each
clip is cut at 55 % of its duration (mid-utterance, no trailing silence) and
pushed to BOTH handlers, fixed and pristine, under two stop scenarios.

Success criterion is delivery of a non-empty transcript, not WER: the
reference no longer matches a truncated utterance.
"""
import asyncio, importlib.util, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).parent
os.environ["LIVE_LATENCY_CSV"] = str(OUT / "live_latency_validation.csv")
os.environ["STT_SESSION_LOG_DIR"] = str(OUT / "sessions")

import numpy as np
import librosa
from fastapi import WebSocketDisconnect
import backend.stt.engine as engine
import backend.main as fixed

spec = importlib.util.spec_from_file_location("main_pristine", OUT / "pristine" / "main_pristine.py")
pristine = importlib.util.module_from_spec(spec); spec.loader.exec_module(pristine)
pristine.RealTimeSTTHandler.LATENCY_CSV = OUT / "live_latency_validation_PRISTINE.csv"

SR = 16000
FILES = ["minds14_fr_clean_01", "minds14_en_clean_01", "minds14_de_clean_01"]
CUT = 0.55


def truncated_chunks(stem):
    y, _ = librosa.load(str(ROOT / f"datasets/stt_eval/audio/{stem}.wav"), sr=SR, mono=True)
    y = y[: int(len(y) * CUT)]
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    # last 0.3 s must still carry energy, otherwise the cut landed in a pause
    tail_rms = float(np.sqrt(np.mean((pcm[-int(0.3 * SR):] / 32768.0) ** 2)))
    return [pcm[i:i + SR].tobytes() for i in range(0, len(pcm), SR)], round(len(y) / SR, 2), round(tail_rms, 4)


class Socket:
    def __init__(self, script):
        self.script = list(script); self.sent = []

    async def accept(self): pass

    async def receive(self):
        if not self.script:
            return {"type": "websocket.disconnect"}
        it = self.script.pop(0)
        if it == "DISCONNECT":
            raise WebSocketDisconnect()
        if isinstance(it, bytes):
            await asyncio.sleep(0)
            return {"type": "websocket.receive", "bytes": it}
        return {"type": "websocket.receive", "text": it}

    async def receive_bytes(self):            # pristine handler path
        m = await self.receive()
        if m.get("type") == "websocket.disconnect" or "bytes" not in m:
            raise WebSocketDisconnect()
        return m["bytes"]

    async def send_json(self, o): self.sent.append(o)

    async def close(self, code=1000): pass


async def one(mod, label, stem, scenario, chunks):
    script = {"end_signal": chunks + ["__end__"], "disconnect": chunks + ["DISCONNECT"]}[scenario]
    sock = Socket(script)
    h = mod.RealTimeSTTHandler(sock)
    await h.process()
    utts = [m["text"] for m in sock.sent if "text" in m]
    return {"handler": label, "file": stem, "scenario": scenario,
            "utterances_delivered": len(utts), "text": " ".join(utts),
            "flushed_ack": any(m.get("type") == "flushed" for m in sock.sent)}


async def main_():
    engine.load_model("small"); engine.load_vad_model()
    print("loaded:", engine.get_model_info())
    rows = []
    for stem in FILES:
        chunks, secs, tail = truncated_chunks(stem)
        print(f"\n{stem}: cut at {secs}s, {len(chunks)} chunks, tail RMS {tail} (must be well above 0.01)")
        for scenario in ("end_signal", "disconnect"):
            for mod, label in ((pristine, "PRISTINE"), (fixed, "FIXED")):
                r = await one(mod, label, stem, scenario, chunks)
                r.update(cut_seconds=secs, tail_rms=tail); rows.append(r)
                print(f"   {label:8s} {scenario:10s} delivered={r['utterances_delivered']} ack={r['flushed_ack']!s:5s} {r['text'][:60]!r}")
    rep = {"scope": "real VAD + real Whisper small; clips truncated mid-speech; fixed vs pristine handler; fake socket",
           "cut_fraction": CUT, "model_loaded": engine.get_model_info(), "rows": rows}
    (OUT / "05b_live_flush_before_after.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwritten:", OUT / "05b_live_flush_before_after.json")

asyncio.run(main_())
