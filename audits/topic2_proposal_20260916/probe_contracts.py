"""Isolated contract probes. Fake ASR/VAD/RAG; never evidence of ASR quality."""
import asyncio
import json
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch, AsyncMock
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
import torch
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient
import backend.main as main

OUT = Path(__file__).parent
seen=[]
engine=ModuleType("backend.stt.engine")
def fake_transcribe(path, forced_language=None):
    seen.append(forced_language)
    return {"text":"contract probe", "language":forced_language or "auto"}
engine.transcribe_file=fake_transcribe
engine._model=object()
engine._diarization_pipeline=None
class Vad:
    def __call__(self,*args): return torch.tensor(1.0)
    def reset_states(self): pass
engine._vad_model=Vad()
vector=ModuleType("backend.rag.vectorstore")
vector.ingest=lambda *args: 1
upload=OUT / "contract_uploads"
upload.mkdir(exist_ok=True)
with patch.dict(sys.modules,{"backend.stt.engine":engine,"backend.rag.vectorstore":vector}), patch.object(main,"UPLOAD_DIR",upload):
    # No context manager: no lifespan/model loading.
    client=TestClient(main.app)
    form=client.post("/transcribe",files={"file":("probe.wav",b"fake-audio","audio/wav")},data={"language":"fr"})
    query=client.post("/transcribe?language=fr",files={"file":("probe.wav",b"fake-audio","audio/wav")})
    class Socket:
        def __init__(self): self.sent=False
        async def accept(self): pass
        async def receive_bytes(self):
            if self.sent: raise WebSocketDisconnect()
            self.sent=True
            return (np.ones(16000,dtype=np.int16)*1000).tobytes()
    async def disconnected():
        handler=main.RealTimeSTTHandler(Socket())
        handler._transcribe_and_diarize=AsyncMock()
        await handler.process()
        return {"pending_bytes":len(handler.audio_buffer),"transcription_calls":handler._transcribe_and_diarize.await_count}
    report={"scope":"Contract probes with fake dependencies; no model inference",
        "upload_language":{"multipart_status":form.status_code,"query_status":query.status_code,"forwarded_values":seen},
        "disconnect_without_silence":asyncio.run(disconnected())}
(OUT/"contract_checks.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
