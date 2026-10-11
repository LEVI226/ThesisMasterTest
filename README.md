# Nestlé AI Accessibility Platform
**BIT / Nestlé — Master Thesis Research Project**

## Maintenance and AI Traceability

Before extending or repairing this project, read:

- [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) — how to run, verify, repair, and preserve the project.
- [CHANGELOG.md](CHANGELOG.md) — narrative history of major changes and lessons.
- [PROMPTS_JOURNAL.md](PROMPTS_JOURNAL.md) — reusable prompts and AI workflow memory.
- [AI_METHODOLOGY.md](AI_METHODOLOGY.md) — disclosed AI usage, rejected errors, and verification policy.

These files exist so the project remains maintainable without depending on an AI-only explanation.

| Topic | Student | Focus |
|---|---|---|
| Topic 1 — OCR Engine | Fadel ZONGO | Deep learning OCR for corporate documents |
| **Topic 2 — STT Engine** | **Yannick Ulrich Levi Ouedraogo** | **Advanced Speech-to-Text for multilingual meetings** |
| Topic 3 — Accessibility Layer | (joint) | Personalized, explainable accessibility interface |

---

## Overview

This platform combines Speech-to-Text (STT) and OCR into an accessible workplace
communication tool for Nestlé Ghana, designed for employees with hearing and visual
impairments. The backend is fully local (Phase 1) with a clear migration path to Azure
(Phase 2).

**Topic 2 focus:** Evaluate and optimize faster-whisper (OpenAI Whisper) for real-world
corporate audio — noisy meetings, multilingual speakers, domain-specific vocabulary —
and measure accuracy with WER/CER/RTF metrics.

---

## Quick Start

```powershell
# 1. Make sure Ollama is running
ollama run llama3.2

# 2. Install dependencies
uv sync

# 3. Run the platform (port 8001 to match the live STT frontend)
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

# 4. Open browser
#    Main platform:        http://localhost:8001
#    Live transcription:   http://localhost:8001/live
#    Research evidence:    http://localhost:8001/research
#    API docs:             http://localhost:8001/docs
```

---

## Architecture

```
Audio/Video  →  [Noise Reduction]  →  [Whisper STT]  →  ChromaDB  →  [Llama 3.2 RAG]  →  Q&A
PDF/Images   →  [Tesseract OCR]    →────────────────────ChromaDB  →  [Llama 3.2 RAG]  →  Q&A
Microphone   →  [Silero VAD]       →  [Whisper STT]  →  WebSocket →  Live Transcript
```

---

## Tech Stack (Phase 1 — Local / Private)

| Layer | Technology |
|---|---|
| STT | faster-whisper (INT8 CPU / float16 GPU) |
| Noise reduction | noisereduce + librosa |
| Speaker diarization | pyannote/speaker-diarization-3.1 |
| VAD (live STT) | Silero VAD |
| OCR | Tesseract + pdf2image |
| Vector DB | ChromaDB |
| Embeddings | intfloat/multilingual-e5-small (FR/EN/DE) |
| LLM | Ollama + Llama 3.2 (local) |
| API | FastAPI + uvicorn |
| UI | Vanilla HTML/CSS/JS |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Main platform UI |
| `GET` | `/live` | Live transcription UI |
| `GET` | `/research` | Topic 2 research evidence dashboard |
| `GET` | `/api/research/evidence` | Current traceable evaluation summaries |
| `GET` | `/health` | Platform health check |
| `POST` | `/transcribe` | Upload audio/video → Whisper → RAG |
| `POST` | `/ocr` | Upload PDF/image → Tesseract → RAG |
| `POST` | `/ask` | Question → ChromaDB → Llama 3.2 → answer |
| `WS` | `/ws/transcribe` | Real-time PCM stream → Whisper → JSON segments |

### `/transcribe` request

```
POST /transcribe
Content-Type: multipart/form-data

file:     audio file (mp3, mp4, wav, m4a, ogg, flac, webm…)
language: optional language code ("fr", "en", "de") — default: auto-detect
```

### `/ws/transcribe` protocol

- Client sends **binary frames**: raw PCM Int16, 16 kHz, mono
- Server returns **JSON lines**: `{"speaker": "SPEAKER_00", "text": "...", "start": 1.2, "end": 3.4}`

---

## STT Evaluation (Topic 2)

The evaluation module measures WER, CER, and RTF across different preprocessing
and domain-adaptation conditions, providing empirical results for the Master Thesis.

### Dataset structure

```
datasets/stt_eval/
  audio/          ← place .wav audio files here (see README inside)
  references/     ← matching .txt reference transcripts
  metadata.csv    ← maps audio → reference, language, noise_condition
```

See [datasets/stt_eval/README.md](datasets/stt_eval/README.md) for how to add audio files
and the required CSV format.

### Run evaluation

```bash
uv run python -m backend.evaluation.run_stt_eval \
    --metadata datasets/stt_eval/metadata.csv \
    --output   results/stt_eval_results.csv \
    --model    small \
    --report   results/stt_evaluation_report.md \
    --hardware-notes "Dell Latitude 3480 — i5-7200U, 8GB RAM, CUDA GPU"
```

**Output files:**

| File | Description |
|---|---|
| `results/stt_eval_results.csv` | Per-sample metrics (WER, CER, RTF, latency) |
| `results/transcripts/*.txt` | Generated transcripts for each condition |
| `results/stt_evaluation_report.md` | Thesis-ready Markdown report |

### Evaluation conditions (default)

| Condition | Preprocessing | Domain Prompt | Language |
|---|---|---|---|
| C1 — Baseline | No | No | Auto |
| C2 — Noise reduction | Yes | No | Auto |
| C3 — Full pipeline | Yes | Yes | Auto |
| C4 — Forced language | Yes | Yes | Forced |

### Metrics explained

| Metric | Formula | Good value |
|---|---|---|
| **WER** (Word Error Rate) | (substitutions + deletions + insertions) / reference words | < 10% for clean speech |
| **CER** (Character Error Rate) | Same at character level | Usually lower than WER |
| **RTF** (Real-Time Factor) | processing_time / audio_duration | < 1.0 (faster than real-time) |

---

## TranscribeConfig — Engine Options

The STT engine accepts a `TranscribeConfig` dataclass for fine-grained control:

```python
from backend.stt.engine import TranscribeConfig, transcribe_file

config = TranscribeConfig(
    model_size    = "small",          # tiny, base, small, medium, large-v3
    language      = None,             # None = auto-detect, "fr", "en", "de"
    task          = "transcribe",     # "transcribe" or "translate"
    preprocessing = True,             # noise reduction via noisereduce
    domain_prompt = True,             # inject Nestlé vocabulary prompt
    domain_prompt_text = "Nestlé, Nespresso, Maggi, KitKat, Nescafé",
    word_timestamps = True,
)
result = transcribe_file("meeting.mp3", config=config)
```

---

## Azure Migration (Phase 2)

Update `.env` to switch providers:

```env
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

| Component | Phase 1 (local) | Phase 2 (Azure) |
|---|---|---|
| STT | faster-whisper (local) | Azure Cognitive Services Speech |
| LLM | Ollama + Llama 3.2 | Azure OpenAI (GPT-4o) |
| Vector DB | ChromaDB | Azure AI Search |
| Compute | CPU / local GPU | NC6s_v3 (NVIDIA V100) |

---

## Project Structure

```
backend/
  main.py              ← FastAPI app (endpoints + WebSocket)
  models.py            ← Pydantic schemas
  stt/
    engine.py          ← faster-whisper + TranscribeConfig + noise reduction
  ocr/
    engine.py          ← Tesseract OCR
  rag/
    vectorstore.py     ← ChromaDB ingestion & retrieval
    chain.py           ← LangChain Q&A (Ollama / Azure OpenAI)
  evaluation/
    metrics.py         ← WER, CER, RTF (pure Python)
    dataset.py         ← metadata.csv loader
    runner.py          ← evaluation run loop
    report.py          ← Markdown report generator
    run_stt_eval.py    ← CLI entry point

frontend/
  index.html           ← Single-page UI (STT upload, OCR, Q&A, Live STT tabs)
  live_transcribe.html ← Standalone live STT page (served at /live)

datasets/
  stt_eval/
    audio/             ← evaluation audio files (not committed)
    references/        ← reference transcripts
    metadata.csv       ← evaluation manifest

results/
  transcripts/         ← generated transcripts from evaluation
  stt_eval_results.csv ← evaluation metrics (generated)
  stt_evaluation_report.md ← thesis report (generated)

tests/
  test_evaluation.py   ← 32 unit tests (WER/CER/RTF, dataset loading)
  sample.wav           ← test audio
  ocr_test.png         ← test image

STT_Demonstration_Report.md   ← PoC evaluation report (Topic 2)
```

---

## Run Tests

```bash
uv run pytest tests/test_evaluation.py -v
```

---

## Implemented vs Proposed

| Feature | Status |
|---|---|
| faster-whisper transcription (CPU + GPU) | ✅ Implemented |
| Noise reduction (noisereduce + librosa) | ✅ Implemented |
| Multilingual auto-detection (FR/EN/DE) | ✅ Implemented |
| Domain vocabulary prompt | ✅ Implemented |
| Speaker diarization (pyannote) | ✅ Implemented |
| Silero VAD for live streaming | ✅ Implemented |
| Real-time WebSocket transcription | ✅ Implemented |
| WER/CER/RTF evaluation framework | ✅ Implemented |
| Evaluation CLI (`run_stt_eval.py`) | ✅ Implemented |
| Thesis-ready Markdown report | ✅ Implemented |
| wav2vec 2.0 comparison | 🔲 Proposed (Phase 2) |
| Conformer / NVIDIA Riva comparison | 🔲 Proposed (Phase 2) |
| Fine-tuning on Nestlé vocabulary | 🔲 Proposed (Phase 2) |
| Azure Cognitive Services Speech migration | 🔲 Proposed (Phase 2) |
| User study / accessibility evaluation | 🔲 Proposed (Phase 2) |
