"""Reproduce the three documented contract defects. Fake ASR/VAD/RAG: this is a
software-contract probe, never evidence of ASR quality. Run with a tag argument
(BEFORE / AFTER) so results can be compared across the fix."""
import asyncio, csv, json, sys
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).parent
TAG = sys.argv[1] if len(sys.argv) > 1 else "BEFORE"

import numpy as np
import torch
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient
import backend.main as main

report = {"tag": TAG, "scope": "contract probes with fake dependencies; no model inference"}

# ---------------------------------------------------------------- defect 1 + 2
seen = []
engine = ModuleType("backend.stt.engine")


def fake_transcribe(path, forced_language=None, **kw):
    seen.append(forced_language)
    return {"text": "probe", "language": forced_language or "auto"}


engine.transcribe_file = fake_transcribe
engine._model = object()
engine._diarization_pipeline = None


class Vad:
    def __call__(self, *a):
        return torch.tensor(1.0)

    def reset_states(self):
        pass


engine._vad_model = Vad()
vector = ModuleType("backend.rag.vectorstore")
vector.ingest = lambda *a: 1
upload = OUT / "probe_uploads"
upload.mkdir(exist_ok=True)

with patch.dict(sys.modules, {"backend.stt.engine": engine, "backend.rag.vectorstore": vector}), \
        patch.object(main, "UPLOAD_DIR", upload):
    client = TestClient(main.app)
    wav = {"file": ("probe.wav", b"fake-audio", "audio/wav")}
    r_form = client.post("/transcribe", files=wav, data={"language": "fr"})
    r_query = client.post("/transcribe?language=fr", files=wav)
    report["defect1_upload_language"] = {
        "multipart_form_status": r_form.status_code,
        "query_string_status": r_query.status_code,
        "language_received_by_engine": {"via_multipart_form": seen[0], "via_query_string": seen[1]},
        "defect_present": seen[0] is None,
    }

    class Socket:
        def __init__(self, end_signal=None):
            self.n = 0
            self.end_signal = end_signal
            self.sent_json = []

        async def accept(self):
            pass

        async def receive_bytes(self):
            self.n += 1
            if self.n == 1:
                return (np.ones(16000, dtype=np.int16) * 1000).tobytes()   # 1 s speech
            raise WebSocketDisconnect()

        async def receive(self):
            self.n += 1
            if self.n == 1:
                return {"type": "websocket.receive",
                        "bytes": (np.ones(16000, dtype=np.int16) * 1000).tobytes()}
            if self.n == 2 and self.end_signal is not None:
                return {"type": "websocket.receive", "text": self.end_signal}
            return {"type": "websocket.disconnect"}

        async def send_json(self, obj):
            self.sent_json.append(obj)

        async def close(self, code=1000):
            pass

    async def disconnect_case():
        h = main.RealTimeSTTHandler(Socket())
        h._transcribe_and_diarize = AsyncMock()
        await h.process()
        return {"pending_bytes_after_disconnect": len(h.audio_buffer),
                "transcription_calls": h._transcribe_and_diarize.await_count,
                "defect_present": h._transcribe_and_diarize.await_count == 0}

    report["defect2_final_buffer_on_disconnect"] = asyncio.run(disconnect_case())

# ---------------------------------------------------------------- defect 3
CANON = ["results/stt_eval_pilot_results.csv", "results/stt_eval_lora_results.csv",
         "results/stt_eval_wav2vec_results.csv", "results/stt_eval_conformer_results.csv"]
rows = []
for rel in CANON:
    with open(ROOT / rel, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["_src"] = rel
            rows.append(r)
by_path = defaultdict(list)
for r in rows:
    if r.get("transcript_output_path"):
        by_path[r["transcript_output_path"]].append(r)
shared = {p: rs for p, rs in by_path.items() if len(rs) > 1}
shared_across_models = {p: sorted({(x["model"], x.get("condition_tag", "")) for x in rs})
                        for p, rs in shared.items()
                        if len({x["model"] for x in rs}) > 1 or len({x.get("condition_tag") for x in rs}) > 1}
mismatch = 0
checked = 0
for r in rows:
    p = r.get("transcript_output_path")
    if not p:
        continue
    fp = ROOT / p
    if not fp.exists():
        continue
    checked += 1
    if fp.read_text(encoding="utf-8").strip() != (r.get("hypothesis_text") or "").strip():
        mismatch += 1
report["defect3_transcript_path_collisions"] = {
    "rows_with_path": sum(len(v) for v in by_path.values()),
    "distinct_paths": len(by_path),
    "paths_shared_by_more_than_one_row": len(shared),
    "paths_shared_across_different_model_or_condition": len(shared_across_models),
    "rows_whose_stored_hypothesis_differs_from_file_on_disk": mismatch,
    "rows_checked_on_disk": checked,
    "example": next(iter(shared_across_models.items()), None),
    "note": "CSV columns reference_text/hypothesis_text remain authoritative; only the .txt side files collide.",
    "defect_present": len(shared_across_models) > 0,
}

out = OUT / f"01_repro_defects_{TAG}.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
