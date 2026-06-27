# Graph Report - .  (2026-06-14)

## Corpus Check
- 53 files · ~73,087 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 275 nodes · 399 edges · 21 communities detected
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 93 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_STT Research & Datasets|STT Research & Datasets]]
- [[_COMMUNITY_Evaluation Dataset Pipeline|Evaluation Dataset Pipeline]]
- [[_COMMUNITY_FastAPI Backend & RAG|FastAPI Backend & RAG]]
- [[_COMMUNITY_STT Metrics Engine|STT Metrics Engine]]
- [[_COMMUNITY_STT Engine & Audio Processing|STT Engine & Audio Processing]]
- [[_COMMUNITY_Azure Cloud Architecture|Azure Cloud Architecture]]
- [[_COMMUNITY_Physical Infrastructure Audit|Physical Infrastructure Audit]]
- [[_COMMUNITY_STT Model Comparison|STT Model Comparison]]
- [[_COMMUNITY_API Data Models|API Data Models]]
- [[_COMMUNITY_RAG Chain|RAG Chain]]
- [[_COMMUNITY_OCR Engine|OCR Engine]]
- [[_COMMUNITY_Eval Report Generator|Eval Report Generator]]
- [[_COMMUNITY_Text Normalization|Text Normalization]]
- [[_COMMUNITY_Platform Overview (Image)|Platform Overview (Image)]]
- [[_COMMUNITY_Project Scope|Project Scope]]
- [[_COMMUNITY_OCR+RAG Integration Tests|OCR+RAG Integration Tests]]
- [[_COMMUNITY_Eval Module|Eval Module]]
- [[_COMMUNITY_STT Module|STT Module]]
- [[_COMMUNITY_RAG Module|RAG Module]]
- [[_COMMUNITY_OCR Module|OCR Module]]
- [[_COMMUNITY_Backend Init|Backend Init]]

## God Nodes (most connected - your core abstractions)
1. `wer()` - 15 edges
2. `run_single()` - 12 edges
3. `Topic 2 — STT Engine (Ulric GOUET-ZONGO)` - 12 edges
4. `TestWER` - 11 edges
5. `load_metadata()` - 10 edges
6. `normalize_text()` - 10 edges
7. `cer()` - 10 edges
8. `TranscribeConfig` - 10 edges
9. `PoC Demo — Nestlé CEO Speech (Philippe Navratil Infant Formula Recall)` - 10 edges
10. `Recommended Azure Architecture for Nestlé Deployment` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Pyannote.audio (Speaker Diarization, Open Source)` --semantically_similar_to--> `pyannote Speaker Diarization 3.1`  [INFERRED] [semantically similar]
  detail.md → README.md
- `WebSocket Streaming Pipeline (Real-Time Audio Ingestion)` --semantically_similar_to--> `WebSocket Real-Time STT Endpoint (/ws/transcribe)`  [INFERRED] [semantically similar]
  detail.md → README.md
- `Azure AI Speech Service (Managed STT)` --semantically_similar_to--> `Azure Cognitive Services Speech (Proposed Migration)`  [INFERRED] [semantically similar]
  detail.md → STT_Demonstration_Report.md
- `DeepFilterNet (Noise Reduction)` --semantically_similar_to--> `noisereduce + librosa (Noise Reduction)`  [INFERRED] [semantically similar]
  detail.md → README.md
- `Benchmark Metrics: WER, RTF, Latency Comparison Table` --semantically_similar_to--> `WER / CER / RTF Evaluation Metrics`  [INFERRED] [semantically similar]
  detail.md → README.md

## Hyperedges (group relationships)
- **Core STT Pipeline: Noise Reduction → Faster-Whisper → Diarization → ChromaDB** — readme_noisereduce_librosa, readme_faster_whisper, readme_pyannote_diarization, readme_chromadb [EXTRACTED 0.95]
- **Live STT Pipeline: Silero VAD → Faster-Whisper → WebSocket → Frontend** — readme_silero_vad, readme_faster_whisper, readme_websocket_live_stt, frontend_live_transcribe_html [EXTRACTED 0.90]
- **Azure Production Stack: AI Speech + AI Search + OpenAI + Entra ID** — demo_azure_cognitive_speech, demo_azure_ai_search, final_report_azure_openai, final_report_entra_id [EXTRACTED 0.95]

## Communities

### Community 0 - "STT Research & Datasets"
Cohesion: 0.05
Nodes (50): Research Direction: Real-Time Multilingual ASR for Noisy Corporate Meetings, STT Research Questions (Domain-Aware Prompting, Noise Reduction, Real-Time Latency), Mozilla Common Voice Dataset (Open License), LibriSpeech Dataset (CC BY 4.0, Benchmark Reference), STT Evaluation Metadata CSV (metadata.csv), Accessibility for Hearing-Impaired Employees, Dell Latitude 3480 Hardware (i5-7200U, 8GB RAM, no GPU), Proper Noun Transcription Error (Navratil → Naruto) (+42 more)

### Community 1 - "Evaluation Dataset Pipeline"
Cohesion: 0.1
Nodes (17): EvalSample, load_metadata(), Dataset loader for STT evaluation. Reads metadata.csv mapping audio files to ref, Load evaluation samples from metadata.csv.      Args:         csv_path: Path to, Check that audio and reference files exist.     Returns list of warning messages, validate_samples(), Real-Time Factor = processing_time / audio_duration.     RTF < 1 means faster th, Compute mean WER, CER, RTF across a list of result dicts.     Each dict must hav (+9 more)

### Community 2 - "FastAPI Backend & RAG"
Cohesion: 0.09
Nodes (24): ask(), health(), lifespan(), ocr(), FastAPI Backend — Nestlé AI Accessibility Platform Exposes STT, OCR, and RAG Q&A, Upload an audio/video file → transcribe with Whisper → ingest to RAG.      - **f, Upload a PDF or image → OCR with Tesseract → ingest to RAG., Ask a question in FR, EN, or DE.     The system retrieves relevant chunks from a (+16 more)

### Community 3 - "STT Metrics Engine"
Cohesion: 0.14
Nodes (9): cer(), _levenshtein(), STT evaluation metrics: WER, CER, RTF. Pure Python implementation using dynamic, Compute Levenshtein edit distance between two sequences.     Returns (substituti, Word Error Rate = (S + D + I) / N     where N = number of words in reference., Character Error Rate = (S + D + I) / N at character level.     Spaces are remove, wer(), TestCER (+1 more)

### Community 4 - "STT Engine & Audio Processing"
Cohesion: 0.14
Nodes (21): get_audio_duration(), load_diarization_pipeline(), load_model(), preprocess_audio(), Load (or return cached) Whisper model., Reduce background noise and resample to 16 kHz mono.     Returns path to cleaned, Transcribe an audio/video file using faster-whisper.      Args:         file_pat, Return audio duration in seconds. (+13 more)

### Community 5 - "Azure Cloud Architecture"
Cohesion: 0.13
Nodes (18): Azure AI Search (Replaces ChromaDB in Phase 2), Azure Cognitive Services Speech (Proposed Migration), Azure NC6s_v3 (NVIDIA Tesla V100) — Proposed GPU, Azure AI Speech Service (Managed STT), Cost Rationale: Self-Hosted Whisper vs Azure API (~0.15€/hr vs ~1€/hr), Docker Containerization for Pipeline Portability, Rationale: Develop Locally First, Deploy to Azure for Load Testing Only, Recommended Azure Architecture for Nestlé Deployment (+10 more)

### Community 6 - "Physical Infrastructure Audit"
Cohesion: 0.27
Nodes (14): DNS Replacement Recommendation - Migrate to VM in FortiGate DMZ, EOSL Risk - End of Support Life (13 of 18 servers exceeded HPE EOSL), FortiGate DMZ - Target for DNS VM Migration, HP DL350 G9 - Test/Admin Server, HP DL360 G9 - Hyper-V Cluster Node, HP DL380 G5 - External DNS Server, HP DL380 G8 x2 - Hyper-V Cluster (Production Nodes), HP ML350 G10 x9 - Remote Site Servers (Hyper-V, AD, AIC, Kaspersky) (+6 more)

### Community 7 - "STT Model Comparison"
Cohesion: 0.21
Nodes (12): Azure VM NCas_T4_v3 (NVIDIA T4 GPU, ~0.75€/hr), Benchmark Metrics: WER, RTF, Latency Comparison Table, Conformer (NVIDIA/Google) — STT Model, Distil-Whisper (Lightweight Whisper Variant), Faster-Whisper (Optimized Whisper for Real-Time), NVIDIA Riva (Conformer-based STT SDK), wav2vec 2.0 (Meta) — STT Model, Whisper (OpenAI) — STT Model (+4 more)

### Community 8 - "API Data Models"
Cohesion: 0.31
Nodes (10): BaseModel, AskRequest, AskResponse, HealthResponse, OcrPage, OcrResponse, Pydantic models for request/response schemas. Topic 2 (STT) + Topic 1 (OCR) + To, SourceChunk (+2 more)

### Community 9 - "RAG Chain"
Cohesion: 0.27
Nodes (9): answer(), _ask_azure_openai(), _ask_ollama(), _build_prompt(), RAG Chain — LangChain + Ollama (Phase 1) / Azure OpenAI (Phase 2) Answers questi, Build a structured prompt for the RAG chain., Send prompt to local Ollama instance., Phase 2: Send prompt to Azure OpenAI.     Uncomment and use when AZURE_OPENAI_EN (+1 more)

### Community 10 - "OCR Engine"
Cohesion: 0.29
Nodes (9): extract_from_file(), extract_from_image(), extract_from_pdf(), _ocr_image(), STT Engine — Topic 2: Advanced Speech-to-Text Models Uses faster-whisper for mul, Run Tesseract OCR on a PIL Image., Convert PDF pages to images and OCR each page.     Uses pypdfium2 for robust cro, OCR a single image file (JPG, PNG, BMP, TIFF…) (+1 more)

### Community 11 - "Eval Report Generator"
Cohesion: 0.36
Nodes (8): _avg(), _fmt(), generate_report(), _load_csv(), _pct(), Generates a Markdown evaluation report from STT results CSV. Thesis-ready format, Generate a Markdown evaluation report from results CSV.      Args:         resul, _safe_float()

### Community 12 - "Text Normalization"
Cohesion: 0.36
Nodes (3): normalize_text(), Normalize text for fair WER/CER comparison.     - Lowercases     - Removes punct, TestNormalizeText

### Community 13 - "Platform Overview (Image)"
Cohesion: 0.53
Nodes (6): Audio Transcription to Text, Inclusive Workplace Communication for All Employees, Nestiti AI Accessibility Platform Project Report, OCR System (Topic 1), STT System (Topic 2), Text Extraction from Documents

### Community 14 - "Project Scope"
Cohesion: 0.9
Nodes (5): Inclusive Workplace Communication for All Employees, Nestlit AI Accessibility Platform Project Report, Nestlit AI Platform, OCR System (Text Extraction from Documents), STT System (Speech-to-Text / Audio Transcription)

### Community 15 - "OCR+RAG Integration Tests"
Cohesion: 0.67
Nodes (0): 

### Community 16 - "Eval Module"
Cohesion: 1.0
Nodes (1): STT Evaluation module — Topic 2 Master Thesis.

### Community 17 - "STT Module"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "RAG Module"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "OCR Module"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Backend Init"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **77 isolated node(s):** `FastAPI Backend — Nestlé AI Accessibility Platform Exposes STT, OCR, and RAG Q&A`, `Pre-load Whisper model and ChromaDB on startup.`, `Health check — returns platform status.`, `Upload an audio/video file → transcribe with Whisper → ingest to RAG.      - **f`, `Upload a PDF or image → OCR with Tesseract → ingest to RAG.` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Eval Module`** (2 nodes): `__init__.py`, `STT Evaluation module — Topic 2 Master Thesis.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `STT Module`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `RAG Module`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OCR Module`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Init`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_single()` connect `STT Engine & Audio Processing` to `Evaluation Dataset Pipeline`, `STT Metrics Engine`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `transcribe_file()` connect `STT Engine & Audio Processing` to `FastAPI Backend & RAG`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `transcribe()` connect `FastAPI Backend & RAG` to `STT Engine & Audio Processing`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `wer()` (e.g. with `run_single()` and `.test_perfect_match()`) actually correct?**
  _`wer()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `run_single()` (e.g. with `TranscribeConfig` and `get_audio_duration()`) actually correct?**
  _`run_single()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `load_metadata()` (e.g. with `main()` and `.test_loads_valid_csv()`) actually correct?**
  _`load_metadata()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `FastAPI Backend — Nestlé AI Accessibility Platform Exposes STT, OCR, and RAG Q&A`, `Pre-load Whisper model and ChromaDB on startup.`, `Health check — returns platform status.` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._