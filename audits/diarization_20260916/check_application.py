"""Real file/live diarization integration check. No RAG or historical log writes."""
import asyncio
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
OUT = Path(__file__).parent
os.environ["STT_SESSION_LOG_DIR"] = str(OUT / "sessions")
os.environ["LIVE_LATENCY_CSV"] = str(OUT / "live_latency.csv")
os.environ["PYANNOTE_METRICS_ENABLED"] = "0"
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
import librosa
import soundfile as sf
import numpy as np
from backend.stt import engine

x, sr = librosa.load(ROOT / "datasets/meetings/audio/meeting_fr_clean_2spk.wav", sr=16000, mono=True, duration=25)
clip = OUT / "meeting_fr_25s.wav"
sf.write(clip, x, sr)
file_result = engine.transcribe_file(str(clip), config=engine.TranscribeConfig(model_size="tiny",language="fr",preprocessing=False,domain_prompt=False))
pipeline = engine.load_diarization_pipeline()
assert pipeline is not None, "Diarization did not load"
assert any(s["speaker"] not in (None,"SPEAKER_UNKNOWN") for s in file_result["segments"])

from backend.main import RealTimeSTTHandler
class Socket:
    def __init__(self): self.messages=[]
    async def send_json(self, message): self.messages.append(message)

async def check_live():
    socket = Socket()
    handler = RealTimeSTTHandler(socket,language="fr")
    pcm=(np.clip(x[:160000],-1,1)*32767).astype(np.int16).tobytes()
    handler.audio_buffer=bytearray(pcm)
    handler.global_audio=bytearray(pcm)
    handler._t_silence_end=time.monotonic()
    await handler._transcribe_and_diarize(engine._model,pipeline)
    return socket.messages

live_result=asyncio.run(check_live())
result={"scope":"Real ASR and pyannote on existing simulated meeting; file and live method, fake transport only. Not speaker accuracy validation.","model_info":engine.get_model_info(),"file":file_result,"live":live_result}
(OUT/"application_after.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
assert live_result and live_result[0]["speaker"] != "SPEAKER_UNKNOWN", "No live diarized text delivered"
print("File speakers:",sorted({s['speaker'] or 'None' for s in file_result['segments']}))
print("Live:",live_result)
