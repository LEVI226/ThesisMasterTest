"""
FastAPI Backend — Nestlé AI Accessibility Platform
Exposes STT, OCR, and RAG Q&A endpoints.
"""
import os
import uuid
import logging
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import aiofiles
import numpy as np
import torch
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("nestle-platform")

# Storage directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "storage/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(os.getenv("CHROMA_DIR", "storage/chroma_db")).mkdir(parents=True, exist_ok=True)

# Supported file types
AUDIO_VIDEO_EXTENSIONS = {".mp3", ".mp4", ".wav", ".ogg", ".m4a", ".flac", ".webm", ".mkv", ".avi"}
DOCUMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load Whisper model and ChromaDB on startup."""
    logger.info("🚀 Starting Nestlé Accessibility Platform...")
    loop = asyncio.get_event_loop()

    # Pre-load Whisper
    try:
        from backend.stt.engine import load_model
        await loop.run_in_executor(None, load_model)
        logger.info("✅ Whisper model loaded.")
    except Exception as e:
        logger.warning(f"⚠️ Whisper preload failed (will load on first request): {e}")

    # Pre-initialize ChromaDB + sentence-transformers embedding model
    try:
        from backend.rag.vectorstore import collection_count
        await loop.run_in_executor(None, collection_count)
        logger.info("✅ ChromaDB initialized.")
    except Exception as e:
        logger.warning(f"⚠️ ChromaDB preload failed: {e}")

    # Pre-load VAD and Diarization
    try:
        from backend.stt.engine import load_vad_model, load_diarization_pipeline
        await loop.run_in_executor(None, load_vad_model)
        await loop.run_in_executor(None, load_diarization_pipeline)
        logger.info("✅ VAD and Diarization models loaded.")
    except Exception as e:
        logger.warning(f"⚠️ VAD/Diarization preload failed: {e}")

    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Nestlé AI Accessibility Platform",
    description="STT + OCR + RAG for inclusive workplace communication — BIT/Nestlé Master Thesis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """Health check — returns platform status."""
    from backend.rag.vectorstore import collection_count
    import httpx

    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(
                f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags"
            )
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    loop = asyncio.get_event_loop()
    count = await loop.run_in_executor(None, collection_count)

    return {
        "status": "ok",
        "ollama_available": ollama_ok,
        "whisper_model": os.getenv("WHISPER_MODEL", "base"),
        "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
        "chroma_collection_count": count,
    }


# ─── STT Endpoint ────────────────────────────────────────────────────────────

@app.post("/transcribe", tags=["STT — Topic 2"], summary="Transcribe audio/video file")
async def transcribe(
    file: UploadFile = File(..., description="Audio or video file (mp3, mp4, wav, m4a…)"),
    language: str | None = None,
):
    """
    Upload an audio/video file → transcribe with Whisper → ingest to RAG.

    - **file**: Audio/video file
    - **language**: Force language ("fr", "en", "de"). Leave empty for auto-detect.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in AUDIO_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(AUDIO_VIDEO_EXTENSIONS)}",
        )

    doc_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{doc_id}{ext}"

    # Save uploaded file
    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    logger.info(f"STT request: {file.filename} ({len(content)/1024:.1f} KB) → {doc_id}")

    # Transcribe (CPU/GPU blocking call → run in executor)
    from backend.stt.engine import transcribe_file
    loop = asyncio.get_event_loop()

    try:
        result = await loop.run_in_executor(
            None,
            lambda: transcribe_file(str(save_path), forced_language=language),
        )
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

    # Ingest to RAG
    from backend.rag.vectorstore import ingest
    full_text = result["text"]
    chunks_count = ingest(doc_id, "stt", file.filename, full_text)

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "language": result.get("language", "unknown"),
        "full_text": full_text,
        "segments": result.get("segments", []),
        "duration_seconds": result.get("duration", 0),
        "processing_time_seconds": result.get("processing_time", 0),
        "whisper_model": result.get("model", ""),
        "ingested_to_rag": chunks_count > 0,
        "chunks_ingested": chunks_count,
    }


# ─── WebSocket STT (Real-time) ───────────────────────────────────────────────

class RealTimeSTTHandler:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.sample_rate = 16000
        self.silence_threshold = int(0.6 * self.sample_rate) # 0.6s silence
        
        self.audio_buffer = bytearray()
        self.global_audio = bytearray()
        self.is_speaking = False
        self.silence_frames = 0

    async def process(self):
        from backend.stt.engine import _model, _vad_model, _diarization_pipeline
        
        if not _model or not _vad_model:
            logger.error("Models not loaded. Closing WebSocket.")
            await self.websocket.close(code=1001)
            return

        await self.websocket.accept()
        logger.info("WebSocket STT client connected.")
        
        try:
            while True:
                # 1. Accept raw 16kHz mono PCM (binary)
                try:
                    chunk = await self.websocket.receive_bytes()
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"WS receive error: {e}")
                    break

                if not chunk:
                    continue

                audio_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
                
                # 2. Silero VAD detection
                tensor_chunk = torch.from_numpy(audio_np)
                speech_prob = _vad_model(tensor_chunk, self.sample_rate).item()
                
                if speech_prob > 0.5:
                    if not self.is_speaking:
                        logger.debug("Speech start detected.")
                    self.is_speaking = True
                    self.silence_frames = 0
                    self.audio_buffer.extend(chunk)
                    self.global_audio.extend(chunk)
                elif self.is_speaking:
                    self.silence_frames += len(audio_np)
                    self.audio_buffer.extend(chunk)
                    self.global_audio.extend(chunk)
                    
                    # End of speech detected (silence > 0.6s)
                    if self.silence_frames >= self.silence_threshold:
                        logger.debug("Speech end detected.")
                        self.is_speaking = False
                        await self._transcribe_and_diarize(_model, _diarization_pipeline)
                        self.audio_buffer = bytearray()
                        self.silence_frames = 0
                        
        except Exception as e:
            logger.error(f"WebSocket loop error: {e}")
        finally:
            logger.info("WebSocket STT client disconnected.")

    async def _transcribe_and_diarize(self, model, diarizer):
        if len(self.audio_buffer) < 1600: # Ignore very short artifacts (<0.1s)
            return

        utterance_np = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
        
        try:
            # 3. faster-whisper transcription
            loop = asyncio.get_event_loop()
            segments_gen, _ = await loop.run_in_executor(
                None,
                lambda: model.transcribe(
                    utterance_np,
                    language="fr",
                    initial_prompt="Nestlé, Nespresso, Maggi, Purina, KitKat, Nescafé, supply chain, plant-based portfolio"
                )
            )
            
            text = " ".join([s.text for s in segments_gen]).strip()
            if not text:
                return
                
            # 4. Pyannote on last 10s context to identify speaker
            speaker = "SPEAKER_UNKNOWN"
            if diarizer:
                context_bytes = 10 * self.sample_rate * 2 # 10s * 16kHz * 2 bytes
                recent_global = self.global_audio[-context_bytes:]
                context_np = np.frombuffer(recent_global, dtype=np.int16).astype(np.float32) / 32768.0
                
                waveform = torch.from_numpy(context_np).unsqueeze(0)
                if torch.cuda.is_available():
                    waveform = waveform.to("cuda")

                diarization = await loop.run_in_executor(
                    None,
                    lambda: diarizer({"waveform": waveform, "sample_rate": self.sample_rate})
                )
                
                for _, _, spk in diarization.itertracks(yield_label=True):
                    speaker = spk # Last active speaker in context window

            # Timestamps
            end_sec = len(self.global_audio) / (self.sample_rate * 2)
            start_sec = end_sec - (len(self.audio_buffer) / (self.sample_rate * 2))

            # 5. Return JSON
            await self.websocket.send_json({
                "speaker": speaker,
                "text": text,
                "start": round(start_sec, 2),
                "end": round(end_sec, 2)
            })
            
        except Exception as e:
            logger.error(f"WS Transcription/Diarization failed: {e}")


@app.websocket("/ws/transcribe")
async def websocket_stt(websocket: WebSocket):
    handler = RealTimeSTTHandler(websocket)
    await handler.process()


# ─── OCR Endpoint ────────────────────────────────────────────────────────────

@app.post("/ocr", tags=["OCR — Topic 1"], summary="Extract text from PDF or image")
async def ocr(
    file: UploadFile = File(..., description="PDF or image file"),
):
    """
    Upload a PDF or image → OCR with Tesseract → ingest to RAG.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(DOCUMENT_EXTENSIONS)}",
        )

    doc_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{doc_id}{ext}"

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    logger.info(f"OCR request: {file.filename} ({len(content)/1024:.1f} KB) → {doc_id}")

    from backend.ocr.engine import extract_from_file
    loop = asyncio.get_event_loop()

    try:
        result = await loop.run_in_executor(
            None,
            lambda: extract_from_file(str(save_path)),
        )
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")

    from backend.rag.vectorstore import ingest
    chunks_count = ingest(doc_id, "ocr", file.filename, result["full_text"])

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "detected_language": result.get("detected_language"),
        "full_text": result["full_text"],
        "pages": result["pages"],
        "ingested_to_rag": chunks_count > 0,
        "chunks_ingested": chunks_count,
    }


# ─── RAG Q&A Endpoint ────────────────────────────────────────────────────────

@app.post("/ask", tags=["RAG — Topic 3"], summary="Ask a question over ingested content")
async def ask(body: dict):
    """
    Ask a question in FR, EN, or DE.
    The system retrieves relevant chunks from all ingested STT + OCR content
    and generates a contextual answer using the local LLM (Ollama / Llama3.2).
    """
    question: str = body.get("question", "").strip()
    language: str = body.get("language", "auto")

    if not question:
        raise HTTPException(status_code=400, detail="'question' field is required.")

    from backend.rag.vectorstore import query
    from backend.rag.chain import answer

    loop = asyncio.get_event_loop()

    # Retrieve relevant chunks
    chunks = query(question, n_results=5)

    # Generate answer
    try:
        rag_answer = await loop.run_in_executor(
            None,
            lambda: answer(question, chunks, language),
        )
    except Exception as e:
        logger.error(f"RAG answer generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    return {
        "question": question,
        "answer": rag_answer,
        "sources": [
            {
                "doc_id": c["doc_id"],
                "source_type": c["source_type"],
                "filename": c["filename"],
                "excerpt": c["excerpt"],
            }
            for c in chunks
        ],
        "language": language,
    }


# ─── Serve Frontend ──────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_ui():
    frontend_path = Path("frontend/index.html")
    if not frontend_path.exists():
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
    return FileResponse(str(frontend_path))

@app.get("/live", response_class=HTMLResponse, include_in_schema=False)
async def serve_live():
    frontend_path = Path("frontend/live_transcribe.html")
    if not frontend_path.exists():
        return HTMLResponse("<h1>live_transcribe.html not found</h1>", status_code=404)
    return FileResponse(str(frontend_path))
