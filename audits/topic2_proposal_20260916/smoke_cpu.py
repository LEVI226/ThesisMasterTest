"""Small real CPU ASR check, isolated from diarization/RAG and historical results."""
import os
os.environ["HF_HUB_OFFLINE"]="1"
os.environ["HF_DATASETS_OFFLINE"]="1"
import sys
import json
import time
import platform
import importlib.metadata
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
OUT=Path(__file__).parent
from faster_whisper import WhisperModel
import backend.stt.engine as engine
from backend.evaluation.metrics import wer
report={"scope":"Real tiny CPU/int8 ASR via transcribe_file; model selection overridden to CPU; diarization explicitly disabled; no browser/RAG/Teams test", "python":platform.python_version(),"packages":{},"samples":[]}
for name in ["torch","faster-whisper","ctranslate2","pyannote.audio"]:
    report["packages"][name]=importlib.metadata.version(name)
t=time.perf_counter()
model=WhisperModel("tiny",device="cpu",compute_type="int8",local_files_only=True)
report["load_seconds"]=time.perf_counter()-t
with patch.object(engine,"load_model",return_value=model),patch.object(engine,"load_diarization_pipeline",return_value=None),patch.object(engine,"_model_name","tiny"):
    for name in ["minds14_en_clean_01","minds14_fr_clean_01","minds14_de_clean_01","minds14_fr_noisy_01"]:
        start=time.perf_counter()
        try:
            result=engine.transcribe_file(str(ROOT/"datasets/stt_eval/audio"/(name+".wav")),config=engine.TranscribeConfig(model_size="tiny",preprocessing=False,domain_prompt=False,word_timestamps=False))
            ref=(ROOT/"datasets/stt_eval/references"/(name.replace("_noisy_","_clean_")+".txt")).read_text(encoding="utf-8").strip()
            elapsed=time.perf_counter()-start
            report["samples"].append({"file":name,"reference":ref,"hypothesis":result["text"],"detected_language":result["language"],"wer":wer(ref,result["text"]),"wall_seconds_including_audio_duration_read":elapsed,"rtf":elapsed/result["duration"],"engine_processing_seconds":result["processing_time"]})
        except Exception as exc:
            report["samples"].append({"file":name,"error":str(exc)})
        (OUT/"smoke_cpu.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        print(name,report["samples"][-1].get("wer",report["samples"][-1].get("error")),flush=True)
