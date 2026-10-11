"""T4 probe — within-utterance language switch through the REAL live path.

Two MInDS-14 clips are joined with their silences trimmed so that the VAD sees
ONE utterance containing two languages. The manuscript states Whisper makes one
language decision per segment; this checks what the live path actually emits.
Also run: same pair with a 1.5 s pause (two utterances -> two decisions).
Scores each half against its own reference with the canonical scorer.
"""
import asyncio, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
OUT = Path(__file__).parent
os.environ["LIVE_LATENCY_CSV"] = str(OUT / "live_latency_validation.csv")
os.environ["STT_SESSION_LOG_DIR"] = str(OUT / "sessions")
import numpy as np, librosa
from fastapi import WebSocketDisconnect
import backend.stt.engine as engine
import backend.main as main
from backend.evaluation.metrics import wer

SR = 16000
PAIRS = [("minds14_fr_clean_01", "minds14_en_clean_01"), ("minds14_fr_clean_01", "minds14_de_clean_01"),
         ("minds14_en_clean_04", "minds14_fr_clean_02")]

def load_trim(stem):
    y, _ = librosa.load(str(ROOT / f"datasets/stt_eval/audio/{stem}.wav"), sr=SR, mono=True)
    y, _ = librosa.effects.trim(y, top_db=30)
    return y
def ref(stem): return (ROOT / f"datasets/stt_eval/references/{stem}.txt").read_text(encoding="utf-8").strip()
def chunks(y):
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    return [pcm[i:i + SR].tobytes() for i in range(0, len(pcm), SR)]

class Socket:
    def __init__(self, script): self.script = list(script); self.sent = []
    async def accept(self): pass
    async def receive(self):
        if not self.script: return {"type": "websocket.disconnect"}
        it = self.script.pop(0)
        if isinstance(it, bytes):
            await asyncio.sleep(0); return {"type": "websocket.receive", "bytes": it}
        return {"type": "websocket.receive", "text": it}
    async def send_json(self, o): self.sent.append(o)
    async def close(self, code=1000): pass

async def run(a, b, gap_s, language=None):
    ya, yb = load_trim(a), load_trim(b)
    gap = np.zeros(int(SR * gap_s), dtype=np.float32)
    y = np.concatenate([ya, gap, yb, np.zeros(SR * 2, dtype=np.float32)])
    sock = Socket(chunks(y) + ["__end__"])
    h = main.RealTimeSTTHandler(sock, language=language)
    await h.process()
    utts = [m["text"] for m in sock.sent if "text" in m]
    joined = " ".join(utts)
    return {"pair": f"{a} + {b}", "gap_s": gap_s, "forced_language": language, "utterances": len(utts),
            "texts": utts, "wer_vs_first_ref": round(wer(ref(a), joined), 3), "wer_vs_second_ref": round(wer(ref(b), joined), 3),
            "wer_vs_concatenated_refs": round(wer(ref(a) + " " + ref(b), joined), 3),
            "ref_first": ref(a), "ref_second": ref(b)}

async def main_():
    engine.load_model("small"); engine.load_vad_model()
    print("loaded:", engine.get_model_info()); rows = []
    for a, b in PAIRS:
        for gap in (0.0, 1.5):
            r = await run(a, b, gap); rows.append(r)
            print(f"\n{r['pair']}  gap={gap}s  -> {r['utterances']} utterance(s)  WER(concat refs)={r['wer_vs_concatenated_refs']}")
            for t in r["texts"]: print("   ", t.encode("ascii", "backslashreplace").decode())
    rep = {"scope": "real VAD + Whisper small via RealTimeSTTHandler; clips trimmed and joined; fake socket", "model": engine.get_model_info(), "rows": rows}
    (OUT / "08_codeswitch_live.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwritten:", OUT / "08_codeswitch_live.json")
asyncio.run(main_())
