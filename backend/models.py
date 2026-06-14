"""
Pydantic models for request/response schemas.
Topic 2 (STT) + Topic 1 (OCR) + Topic 3 (RAG Q&A)
"""
from pydantic import BaseModel
from typing import Optional


# ─── STT Schemas ────────────────────────────────────────────────────────────

class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[str] = None  # populated by diarization if enabled
    confidence: Optional[float] = None

class TranscribeResponse(BaseModel):
    doc_id: str
    filename: str
    language: str
    full_text: str
    segments: list[TranscriptSegment]
    duration_seconds: float
    whisper_model: str
    ingested_to_rag: bool


# ─── OCR Schemas ────────────────────────────────────────────────────────────

class OcrPage(BaseModel):
    page: int
    text: str

class OcrResponse(BaseModel):
    doc_id: str
    filename: str
    detected_language: Optional[str]
    full_text: str
    pages: list[OcrPage]
    ingested_to_rag: bool


# ─── RAG Schemas ────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    language: Optional[str] = "auto"  # "fr", "en", "de", or "auto"

class SourceChunk(BaseModel):
    doc_id: str
    source_type: str  # "stt" or "ocr"
    filename: str
    excerpt: str

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]
    language_detected: Optional[str]


# ─── Health ─────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    ollama_available: bool
    whisper_model: str
    chroma_collection_count: int
