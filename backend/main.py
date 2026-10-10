"""
FastAPI Backend — Nestlé AI Accessibility Platform
Exposes STT, OCR, and RAG Q&A endpoints.
"""
import os
import uuid
import time
import logging
import asyncio
import csv as _csv
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
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
async def lifespan(_app: FastAPI):
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
        from backend.stt.engine import get_model_info
        info = get_model_info()
        logger.info("Whisper=%s on %s/%s | VAD %s | Diarization %s",
                    info["model"], info["device"], info["compute_type"],
                    "loaded" if info["vad_loaded"] else "UNAVAILABLE",
                    "loaded" if info["diarization_loaded"] else "UNAVAILABLE (speakers will be SPEAKER_UNKNOWN)")
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

    from backend.stt.engine import get_model_info
    info = get_model_info()          # what is actually loaded, not what was requested
    return {
        "status": "ok",
        "ollama_available": ollama_ok,
        "whisper_model": info["model"] or os.getenv("WHISPER_MODEL", "small"),
        "stt_device": info["device"],
        "stt_compute_type": info["compute_type"],
        "vad_available": info["vad_loaded"],
        "diarization_available": info["diarization_loaded"],
        "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
        "chroma_collection_count": count,
    }


# ─── STT Endpoint ────────────────────────────────────────────────────────────

@app.post("/transcribe", tags=["STT — Topic 2"], summary="Transcribe audio/video file")
async def transcribe(
    file: UploadFile = File(..., description="Audio or video file (mp3, mp4, wav, m4a…)"),
    language: str | None = Form(None, description="Force language (fr/en/de) as a form field"),
    language_query: str | None = Query(None, alias="language", include_in_schema=False),
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
    from backend.stt.engine import transcribe_file, get_model_info
    from backend.stt.session_log import SessionLog
    loop = asyncio.get_event_loop()
    # Per-request log (only when STT_SESSION_LOG_DIR is set), same format as the live path.
    slog = SessionLog("file", options={"filename": file.filename, "size_kb": round(len(content) / 1024, 1),
                                        "forced_language": language or language_query, "doc_id": doc_id})
    t0 = time.monotonic()

    try:
        result = await loop.run_in_executor(
            None,
            lambda: transcribe_file(str(save_path), forced_language=(language or language_query)),
        )
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        slog.close(status="error", error=repr(e), wall_s=round(time.monotonic() - t0, 3))
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    segs = result.get("segments", [])
    slog.event("transcribed", detected_language=result.get("language"), audio_s=result.get("duration"),
               engine_processing_s=result.get("processing_time"), wall_s=round(time.monotonic() - t0, 3),
               segments=len(segs), chars=len(result.get("text", "")),
               speakers=sorted({s.get("speaker") for s in segs if isinstance(s, dict) and s.get("speaker")}),
               model_loaded=get_model_info(), text=result.get("text", ""))
    slog.close(status="ok")

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
        "diarization_available": get_model_info()["diarization_loaded"],
        "ingested_to_rag": chunks_count > 0,
        "chunks_ingested": chunks_count,
    }


# ─── WebSocket STT (Real-time) ───────────────────────────────────────────────

class RealTimeSTTHandler:
    # Historical file by default; validation runs override with LIVE_LATENCY_CSV.
    LATENCY_CSV = Path(os.environ.get("LIVE_LATENCY_CSV", "results/live_latency.csv"))
    END_SIGNAL = "__end__"   # text frame the client sends to flush the last utterance

    def __init__(self, websocket: WebSocket, language: str | None = None):
        self.websocket = websocket
        self.language = language          # None = Whisper auto-detect
        # Read per session so validation runs can redirect with LIVE_LATENCY_CSV.
        self.latency_csv = Path(os.environ.get("LIVE_LATENCY_CSV", str(self.LATENCY_CSV)))
        self.sample_rate = 16000
        self.silence_threshold = int(0.6 * self.sample_rate) # 0.6s silence

        self.audio_buffer = bytearray()
        self.global_audio = bytearray()
        self.is_speaking = False
        self.silence_frames = 0
        self._utterance_id = 0
        self._t_silence_end: float = 0.0
        self._flush_reason = "silence"
        self._chunks = {"count": 0, "bytes": 0, "min": None, "max": 0}
        from backend.stt.session_log import SessionLog
        self.slog = SessionLog("live", options={
            "language": language, "sample_rate": self.sample_rate,
            "silence_threshold_s": 0.6, "vad_speech_prob": 0.5,
            "min_utterance_bytes": 1600, "min_rms": 0.01,
            "no_speech_threshold": 0.6, "log_prob_threshold": -1.0,
            "compression_ratio_threshold": 2.4,
            "latency_csv": str(self.latency_csv),
        })

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
                # 1. Accept raw 16kHz mono PCM (binary) or the text end-signal
                try:
                    msg = await self.websocket.receive()
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"WS receive error: {e}")
                    break

                if msg.get("type") == "websocket.disconnect":
                    break
                if msg.get("text") is not None:
                    if msg["text"].strip() == self.END_SIGNAL:
                        await self._flush_pending(_model, _diarization_pipeline, _vad_model, reason="end_signal")
                        try:
                            await self.websocket.send_json({"type": "flushed"})
                        except Exception:
                            pass
                    continue
                chunk = msg.get("bytes")
                if not chunk:
                    continue
                c = self._chunks
                c["count"] += 1; c["bytes"] += len(chunk)
                c["min"] = len(chunk) if c["min"] is None else min(c["min"], len(chunk))
                c["max"] = max(c["max"], len(chunk))

                audio_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0

                # 2. Silero VAD — model requires exactly 512-sample windows at 16 kHz.
                # The browser sends larger chunks (e.g. 16 000 samples / 1 s), so we
                # slice into 512-sample windows and keep the maximum speech probability.
                SILERO_WINDOW = 512
                speech_prob = 0.0
                for i in range(0, len(audio_np) - SILERO_WINDOW + 1, SILERO_WINDOW):
                    window = torch.from_numpy(audio_np[i : i + SILERO_WINDOW])
                    p = _vad_model(window, self.sample_rate).item()
                    if p > speech_prob:
                        speech_prob = p

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
                        self._t_silence_end = time.monotonic()
                        _vad_model.reset_states()
                        await self._transcribe_and_diarize(_model, _diarization_pipeline)
                        self.audio_buffer = bytearray()
                        self.silence_frames = 0
                        
        except Exception as e:
            logger.error(f"WebSocket loop error: {e}")
        finally:
            # Best effort: transcribe whatever was still buffered when the client
            # left. Delivery may fail (socket gone) but the text is still logged.
            await self._flush_pending(_model, _diarization_pipeline, _vad_model, reason="disconnect")
            self.slog.close(utterances=self._utterance_id, chunks=self._chunks)
            logger.info("WebSocket STT client disconnected.")

    async def _flush_pending(self, model, diarizer, vad_model, reason: str):
        """Transcribe the pending buffer without waiting for a silence window."""
        if not self.audio_buffer:
            return
        logger.info("Flushing pending audio (%d bytes, reason=%s)", len(self.audio_buffer), reason)
        self._flush_reason = reason
        self.is_speaking = False
        self._t_silence_end = time.monotonic()
        if vad_model is not None:
            try:
                vad_model.reset_states()
            except Exception:
                pass
        await self._transcribe_and_diarize(model, diarizer)
        self._flush_reason = "silence"
        self.audio_buffer = bytearray()
        self.silence_frames = 0

    async def _transcribe_and_diarize(self, model, diarizer):
        if len(self.audio_buffer) < 1600: # Ignore very short artifacts (<0.1s)
            self.slog.event("skipped", reason="too_short", buffer_bytes=len(self.audio_buffer),
                            trigger=self._flush_reason)
            return

        utterance_np = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0

        # Skip silent/near-silent utterances — avoids Whisper repeating the initial_prompt
        rms = float(np.sqrt(np.mean(utterance_np ** 2)))
        if rms < 0.01:
            logger.debug("Skipping utterance: RMS %.4f below threshold", rms)
            self.slog.event("skipped", reason="low_rms", rms=round(rms, 5),
                            buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)
            return

        try:
            # 3. faster-whisper transcription
            loop = asyncio.get_event_loop()
            segments_gen, _ = await loop.run_in_executor(
                None,
                lambda: model.transcribe(
                    utterance_np,
                    language=self.language,
                    # No initial_prompt in live mode: it causes Whisper to hallucinate
                    # the prompt text when audio is silent or noisy.
                    no_speech_threshold=0.6,
                    log_prob_threshold=-1.0,
                    compression_ratio_threshold=2.4,
                )
            )

            text = " ".join([s.text for s in segments_gen]).strip()
            if not text:
                self.slog.event("skipped", reason="empty_text",
                                buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)
                return

            # Reject hallucinated repetitions: split into words, check if any phrase
            # of 4+ words repeats more than twice in the output.
            words = text.split()
            if len(words) >= 8:
                chunk = " ".join(words[:4])
                if text.count(chunk) > 2:
                    logger.debug("Skipping hallucinated repetition: %r", text[:60])
                    self.slog.event("skipped", reason="repetition", text=text,
                                    buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)
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

                # pyannote.audio 4.x returns DiarizeOutput(speaker_diarization, exclusive_speaker_diarization, speaker_embeddings)
                # rather than a bare Annotation when called with a waveform dict.
                annotation = diarization.speaker_diarization if hasattr(diarization, "speaker_diarization") else diarization
                for _, _, spk in annotation.itertracks(yield_label=True):
                    speaker = spk # Last active speaker in context window

            # Timestamps
            end_sec = len(self.global_audio) / (self.sample_rate * 2)
            start_sec = end_sec - (len(self.audio_buffer) / (self.sample_rate * 2))

            # 5. Measure latency and log to CSV
            latency = round(time.monotonic() - self._t_silence_end, 3)
            duration_audio = round(len(self.audio_buffer) / (self.sample_rate * 2), 3)
            self._utterance_id += 1
            self.latency_csv.parent.mkdir(parents=True, exist_ok=True)
            new_file = not self.latency_csv.exists()
            with open(self.latency_csv, "a", newline="", encoding="utf-8") as f:
                w = _csv.DictWriter(f, fieldnames=["utterance_id", "duration_audio", "latency_seconds"])
                if new_file:
                    w.writeheader()
                w.writerow({"utterance_id": self._utterance_id,
                            "duration_audio": duration_audio,
                            "latency_seconds": latency})
            logger.info("Utterance %d | audio=%.1fs | latency=%.3fs | %s | %r",
                        self._utterance_id, duration_audio, latency, speaker, text)
            self.slog.event("utterance", utterance_id=self._utterance_id,
                            trigger=self._flush_reason, buffer_bytes=len(self.audio_buffer),
                            duration_audio_s=duration_audio, latency_seconds=latency,
                            speaker=speaker, text=text,
                            start_s=round(start_sec, 2), end_s=round(end_sec, 2))

            # 6. Return JSON
            await self.websocket.send_json({
                "speaker": speaker,
                "text": text,
                "start": round(start_sec, 2),
                "end": round(end_sec, 2)
            })
            
        except Exception as e:
            logger.error(f"WS Transcription/Diarization failed: {e}")
            self.slog.event("error", where="transcribe_and_diarize", error=repr(e),
                            buffer_bytes=len(self.audio_buffer), trigger=self._flush_reason)


@app.websocket("/ws/transcribe")
async def websocket_stt(websocket: WebSocket, lang: str = "auto"):
    language = lang if lang != "auto" else None
    handler = RealTimeSTTHandler(websocket, language=language)
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


@app.get("/research", response_class=HTMLResponse, include_in_schema=False)
async def serve_research_dashboard():
    """Serve the Topic 2 academic evidence dashboard."""
    frontend_path = Path("frontend/research.html")
    if not frontend_path.exists():
        return HTMLResponse("<h1>research.html not found</h1>", status_code=404)
    return FileResponse(str(frontend_path))


@app.get("/api/research/evidence", tags=["Evaluation — Topic 2"])
async def research_evidence():
    """Return current, provenance-rich summaries from canonical result files."""
    from backend.evaluation.research_dashboard import build_research_dashboard

    try:
        return build_research_dashboard(Path("results"))
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Research dashboard evidence unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc





