"""
STT Engine — Topic 2: Advanced Speech-to-Text Models
Uses faster-whisper for multilingual transcription (FR/EN/DE + West African accent support).

Phase 2 migration: swap load_model() and transcribe_file() to Azure Cognitive Services Speech.
"""
import os
import time
import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel
import torch

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

import noisereduce as nr
import librosa
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_DOMAIN_PROMPT = (
    "Nestlé, Nespresso, Maggi, Purina, KitKat, Nescafé, "
    "supply chain, plant-based portfolio, Nestlé Ghana"
)

# ─── Configuration dataclass ─────────────────────────────────────────────────

@dataclass
class TranscribeConfig:
    """
    All transcription options in one place.
    Replaces scattered keyword arguments — pass to transcribe_file(config=...).
    """
    model_size: str = field(
        default_factory=lambda: os.getenv("WHISPER_MODEL", "small")
    )
    language: Optional[str] = None           # None = auto-detect
    task: str = "transcribe"                 # "transcribe" or "translate"
    preprocessing: bool = True               # noise reduction via noisereduce
    domain_prompt: bool = True               # inject Nestlé vocabulary
    domain_prompt_text: str = DEFAULT_DOMAIN_PROMPT
    word_timestamps: bool = True
    condition_on_previous_text: bool = True
    # faster-whisper native VAD (Silero) — more tightly integrated than
    # load_vad_model(): operates segment-by-segment and handles any audio length.
    vad: bool = False


# ─── Model cache ─────────────────────────────────────────────────────────────

_model = None
_model_name: str = ""
_diarization_pipeline = None
_vad_model = None


def load_vad_model():
    global _vad_model
    if _vad_model is None:
        logger.info("Loading Silero VAD model...")
        model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            trust_repo=True,
        )
        _vad_model = model
        logger.info("Silero VAD loaded successfully.")
    return _vad_model


def load_diarization_pipeline():
    global _diarization_pipeline
    if not PYANNOTE_AVAILABLE:
        return None

    if _diarization_pipeline is None:
        token = os.getenv("HF_TOKEN")
        if not token:
            logger.warning("No HF_TOKEN found. Diarization will be disabled.")
            return None

        logger.info("Loading pyannote diarization pipeline")
        try:
            _diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=token,
            )
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            _diarization_pipeline.to(device)
            logger.info("pyannote diarization loaded on %s.", device)
        except Exception as e:
            logger.error("Failed to load pyannote pipeline: %s", e)
            _diarization_pipeline = None

    return _diarization_pipeline


def load_model(model_size: Optional[str] = None) -> WhisperModel:
    """Load (or return cached) Whisper model."""
    global _model, _model_name
    name = model_size or os.getenv("WHISPER_MODEL", "small")
    if _model is None or _model_name != name:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        logger.info("Loading faster-whisper model: %s on %s (%s)", name, device.upper(), compute_type)
        _model = WhisperModel(name, device=device, compute_type=compute_type)
        _model_name = name
        logger.info("faster-whisper model '%s' loaded successfully.", name)
    return _model


# ─── Audio preprocessing ─────────────────────────────────────────────────────

def preprocess_audio(input_path: str, output_path: str) -> str:
    """
    Reduce background noise and resample to 16 kHz mono.
    Returns path to cleaned file (or original if preprocessing fails).
    """
    try:
        audio, sr = librosa.load(input_path, sr=16000, mono=True)
        reduced = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.75)
        sf.write(output_path, reduced, sr)
        logger.info("Audio preprocessed: %s → %s", input_path, output_path)
        return output_path
    except Exception as e:
        logger.warning("Noise reduction failed (%s), using original audio.", e)
        return input_path


# ─── Core transcription ──────────────────────────────────────────────────────

def transcribe_file(
    file_path: str,
    config: Optional[TranscribeConfig] = None,
    # Legacy params — kept for backwards compatibility with /transcribe endpoint
    forced_language: Optional[str] = None,
    task: str = "transcribe",
) -> dict:
    """
    Transcribe an audio/video file using faster-whisper.

    Args:
        file_path: Path to the audio/video file.
        config: TranscribeConfig instance. If None, a default config is built
                from legacy params and environment variables.
        forced_language: (legacy) Force a specific language code. Prefer config.language.
        task: (legacy) "transcribe" or "translate". Prefer config.task.

    Returns:
        dict with keys: text, segments, language, duration, processing_time, model
    """
    if config is None:
        config = TranscribeConfig(
            language=forced_language,
            task=task,
        )

    model = load_model(config.model_size)
    start_time = time.time()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        cleaned_path = tmp.name

    try:
        if config.preprocessing:
            cleaned_path = preprocess_audio(file_path, cleaned_path)
        else:
            cleaned_path = file_path

        transcribe_options: dict = {
            "task": config.task,
            "word_timestamps": config.word_timestamps,
            "condition_on_previous_text": config.condition_on_previous_text,
        }
        if config.language:
            transcribe_options["language"] = config.language
        if config.domain_prompt:
            transcribe_options["initial_prompt"] = config.domain_prompt_text
        if config.vad:
            transcribe_options["vad_filter"] = True

        logger.info("Starting transcription: %s", Path(file_path).name)
        segments_gen, info = model.transcribe(cleaned_path, **transcribe_options)

        segments = []
        full_text = ""
        for seg in segments_gen:
            text = seg.text.strip()
            full_text += text + " "
            segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": text,
                "speaker": None,
                "confidence": None,
            })

        full_text = full_text.strip()
        processing_time = time.time() - start_time
        audio_duration = get_audio_duration(file_path)
        logger.info(
            "Transcription done in %.1fs | audio=%.1fs | language=%s | chars=%d",
            processing_time, audio_duration, info.language, len(full_text),
        )

        # Diarization post-processing (independent of noise-reduction preprocessing)
        diarizer = load_diarization_pipeline()
        if diarizer:
            logger.info("Starting speaker diarization...")
            try:
                diarize_start = time.time()
                diarization_result = diarizer(cleaned_path)
                for w_seg in segments:
                    best_speaker = None
                    max_overlap = 0.0
                    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
                        overlap = max(0, min(w_seg["end"], turn.end) - max(w_seg["start"], turn.start))
                        if overlap > max_overlap:
                            max_overlap = overlap
                            best_speaker = speaker
                    w_seg["speaker"] = best_speaker or "SPEAKER_UNKNOWN"
                logger.info("Diarization done in %.1fs", time.time() - diarize_start)
            except Exception as e:
                logger.error("Diarization failed: %s", e)

        return {
            "text": full_text,
            "segments": segments,
            "language": info.language,
            "duration": audio_duration,        # length of the audio, in seconds
            "processing_time": processing_time, # wall-clock transcription time, in seconds
            "model": _model_name,
        }

    finally:
        try:
            if os.path.exists(cleaned_path) and cleaned_path != file_path:
                os.remove(cleaned_path)
        except Exception:
            pass


def get_audio_duration(file_path: str) -> float:
    """Return audio duration in seconds."""
    try:
        audio, sr = librosa.load(file_path, sr=None, mono=True)
        return float(len(audio) / sr)
    except Exception:
        return 0.0
