"""One interface for the four model families compared in the study.

CTC systems (MMS, Conformer) need the language: it is given "by construction",
exactly as in the canonical campaign. Whisper can run forced or auto.
"""
from __future__ import annotations

import gc
import json
import struct
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from study_real_meetings.audio import write_wav
from study_real_meetings.config import LORA_ADAPTER, SAMPLE_RATE

SYSTEMS = ("whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large",
           "hf-whisper-small", "hf-whisper-small-lora")
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


_ST_DTYPES = {"F32": torch.float32, "F16": torch.float16, "BF16": torch.bfloat16, "I64": torch.int64}


def _read_safetensors(path, dtype, device="cpu") -> dict:
    """Stream a .safetensors file tensor by tensor with plain file reads (no mmap).

    Windows workaround: transformers 5.3 / torch 2.6 load large checkpoints through
    torch.UntypedStorage.from_file, which access-violates on the 3.9 GB MMS file (and
    intermittently on repeated loads) when system commit memory is tight.
    """
    sd = {}
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
        base = 8 + n
        for key, meta in header.items():
            if key == "__metadata__":
                continue
            a, b = meta["data_offsets"]
            f.seek(base + a)
            buf = bytearray(b - a)
            f.readinto(buf)
            src = _ST_DTYPES[meta["dtype"]]
            t = torch.frombuffer(buf, dtype=src).reshape(meta["shape"]) if b > a else torch.empty(meta["shape"], dtype=src)
            sd[key] = (t.to(dtype) if t.is_floating_point() else t.clone()).to(device)  # device=cuda: no host copy of the model
    return sd


@dataclass(frozen=True)
class Transcript:
    text: str
    detected_language: str | None
    seconds: float


class FasterWhisperTranscriber:
    def __init__(self, size: str, compute_type: str = "float16"):
        from faster_whisper import WhisperModel
        self.model = WhisperModel(size, device=_DEVICE, compute_type=compute_type if _DEVICE == "cuda" else "int8")
        self.system, self.model_id, self.compute_type = f"whisper-{size}", size, compute_type

    def transcribe(self, audio, *, language, prompt):
        t0 = time.perf_counter()
        segments, info = self.model.transcribe(
            audio, language=language, initial_prompt=prompt, beam_size=5,
            temperature=[0.0], condition_on_previous_text=False, vad_filter=False,
        )
        text = " ".join(s.text.strip() for s in segments)  # consuming the generator runs decoding
        return Transcript(text.strip(), info.language, time.perf_counter() - t0)


class HFWhisperTranscriber:
    """transformers Whisper, optionally with the thesis LoRA adapter merged (same backend for J0/J)."""

    def __init__(self, adapter_dir: Path | None = None, base: str = "openai/whisper-small"):
        from transformers import WhisperForConditionalGeneration, WhisperProcessor
        self.dtype = torch.float16 if _DEVICE == "cuda" else torch.float32
        self.processor = WhisperProcessor.from_pretrained(str(adapter_dir) if adapter_dir else base)
        model = WhisperForConditionalGeneration.from_pretrained(base, torch_dtype=self.dtype)
        if adapter_dir:
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, str(adapter_dir)).merge_and_unload()
        self.model = model.to(_DEVICE).eval()
        self.system = "hf-whisper-small-lora" if adapter_dir else "hf-whisper-small"
        self.model_id = f"{base}+{adapter_dir.name}" if adapter_dir else base
        self.compute_type = str(self.dtype).replace("torch.", "")

    def transcribe(self, audio, *, language, prompt):
        if prompt:
            raise ValueError("Prompting is only evaluated with faster-whisper (H4b).")
        t0 = time.perf_counter()
        feats = self.processor.feature_extractor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").input_features
        with torch.no_grad():
            ids = self.model.generate(feats.to(_DEVICE, self.dtype), language=language, task="transcribe",
                                      num_beams=5, max_new_tokens=440)
        text = self.processor.tokenizer.batch_decode(ids, skip_special_tokens=True)[0].strip()
        return Transcript(text, language, time.perf_counter() - t0)


class MMSTranscriber:
    LANGS = {"en": "eng", "fr": "fra", "de": "deu"}

    def __init__(self, model_id: str = "facebook/mms-1b-all"):
        from transformers import AutoProcessor, Wav2Vec2ForCTC
        self.dtype = torch.float16 if _DEVICE == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(model_id)
        from huggingface_hub import hf_hub_download
        from transformers import AutoConfig
        # Tensors go straight to the GPU: a host-side copy of the 1B weights keeps ~4.5 GB of process
        # commit alive and, with Windows commit tight, CUDA's lazy cuDNN/cuBLAS init then fails with "out of memory".
        state = _read_safetensors(hf_hub_download(model_id, "model.safetensors"), self.dtype, _DEVICE)
        config = AutoConfig.from_pretrained(model_id)
        with torch.device("meta"):
            model = Wav2Vec2ForCTC(config).to(self.dtype)
        missing, unexpected = model.load_state_dict(state, strict=False, assign=True)
        if unexpected or [k for k in missing if "lm_head" not in k and "adapter" not in k]:
            raise RuntimeError(f"MMS state dict mismatch: missing={missing[:5]} unexpected={unexpected[:5]}")
        self.model = model.to(_DEVICE).eval()
        del state
        self.model.config._name_or_path = model_id  # load_adapter resolves adapter files from this
        self.current = None
        self.system, self.model_id, self.compute_type = "mms-1b-all", model_id, str(self.dtype).replace("torch.", "")

    def transcribe(self, audio, *, language, prompt):
        if language is None:
            raise ValueError("MMS needs the language (given by construction).")
        if self.current != language:
            self.processor.tokenizer.set_target_lang(self.LANGS[language])
            self.model.load_adapter(self.LANGS[language])
            self.current = language
        t0 = time.perf_counter()
        inputs = self.processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt")
        kwargs = {"input_values": inputs.input_values.to(_DEVICE, self.dtype)}
        if getattr(inputs, "attention_mask", None) is not None:
            kwargs["attention_mask"] = inputs.attention_mask.to(_DEVICE)
        with torch.no_grad():
            ids = torch.argmax(self.model(**kwargs).logits, dim=-1)[0]
        return Transcript(self.processor.decode(ids).strip(), language, time.perf_counter() - t0)


class NemoConformerTranscriber:
    MODELS = {"en": "nvidia/stt_en_conformer_ctc_large",
              "fr": "nvidia/stt_fr_conformer_ctc_large",
              "de": "nvidia/stt_de_conformer_ctc_large"}

    def __init__(self):
        self.models: dict = {}
        self.system, self.model_id, self.compute_type = "conformer-ctc-large", "nvidia/stt_{en,fr,de}_conformer_ctc_large", "float32"
        self.tmp = Path(tempfile.mkdtemp(prefix="rm_nemo_"))

    def _model(self, language):
        if language not in self.models:
            import nemo.collections.asr as nemo_asr
            for old in list(self.models):  # one checkpoint in VRAM at a time
                del self.models[old]
            gc.collect()
            torch.cuda.empty_cache()
            try:
                model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(self.MODELS[language])
            except Exception:
                model = nemo_asr.models.EncDecCTCModel.from_pretrained(self.MODELS[language])
            self.models[language] = model.to(_DEVICE).eval()
        return self.models[language]

    def transcribe(self, audio, *, language, prompt):
        if language is None:
            raise ValueError("Conformer checkpoints are monolingual (language given by construction).")
        model = self._model(language)
        wav = self.tmp / "segment.wav"
        write_wav(wav, audio)
        t0 = time.perf_counter()
        out = model.transcribe([str(wav)])  # same call as backend/training/eval_conformer.py
        hyp = out[0] if out else ""
        if isinstance(hyp, (list, tuple)):
            hyp = hyp[0]
        text = hyp.text if hasattr(hyp, "text") else str(hyp)
        return Transcript(text.strip(), language, time.perf_counter() - t0)


def make_transcriber(system: str):
    if system == "whisper-small":
        return FasterWhisperTranscriber("small")
    if system == "whisper-large-v3":
        return FasterWhisperTranscriber("large-v3")
    if system == "mms-1b-all":
        return MMSTranscriber()
    if system == "conformer-ctc-large":
        return NemoConformerTranscriber()
    if system == "hf-whisper-small":
        return HFWhisperTranscriber(None)
    if system == "hf-whisper-small-lora":
        return HFWhisperTranscriber(LORA_ADAPTER)
    raise ValueError(f"Unknown system {system!r}; expected one of {SYSTEMS}")


def release(transcriber) -> None:
    del transcriber
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
