# Topic 2 - Speech-to-Text Engine
## Technical Status Document for Collaboration

**Project:** AI-Driven Multimodal Accessibility Platform for Inclusive Workplace Communication  
**Topic:** Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings  
**Student:** Ulric GOUET-ZONGO  
**Framework:** Private-RAG (Retrieval-Augmented Generation)  
**Date:** 7 May 2026  
**Status:** Proof of Concept implemented and ready for academic evaluation

---

## 1. Objective

The objective of Topic 2 is to design and evaluate a Speech-to-Text (STT) engine capable of transcribing corporate audio and video content in noisy, multilingual, and multi-speaker meeting environments.

This topic supports accessibility for employees with hearing impairments by producing accurate, timestamped meeting transcripts. These transcripts can then be indexed into a private knowledge base and queried through the shared RAG layer.

The current implementation focuses on:

- local/private STT processing with no external data leakage;
- multilingual transcription using faster-whisper;
- noise reduction before transcription;
- timestamped transcript generation;
- optional speaker diarization;
- live transcription through WebSocket;
- ingestion of transcripts into ChromaDB for multilingual Q&A;
- academic evaluation using WER, CER, and Real-Time Factor.

---

## 2. Current Implementation

The STT engine has been implemented inside the existing multimodal platform.

### Backend

The FastAPI backend exposes the following relevant endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /transcribe` | Upload audio/video, transcribe with faster-whisper, then ingest into RAG |
| `WS /ws/transcribe` | Real-time microphone transcription through WebSocket |
| `POST /ask` | Ask questions over ingested STT/OCR content |
| `GET /health` | Check platform status |

### STT Engine

The STT engine is implemented in:

```text
backend/stt/engine.py
```

It includes:

- faster-whisper model loading;
- automatic CPU/GPU detection;
- INT8 inference on CPU and float16 on GPU;
- audio preprocessing with `librosa`, `soundfile`, and `noisereduce`;
- configurable transcription options through `TranscribeConfig`;
- optional domain vocabulary prompt;
- optional pyannote speaker diarization;
- timestamped segment output.

### Evaluation Module

A new evaluation workflow has been added under:

```text
backend/evaluation/
```

It supports:

- Word Error Rate (WER);
- Character Error Rate (CER);
- Real-Time Factor (RTF);
- processing time;
- CSV result export;
- Markdown report generation.

The intended command is:

```bash
uv run python -m backend.evaluation.run_stt_eval \
  --metadata datasets/stt_eval/metadata.csv \
  --output results/stt_eval_results.csv \
  --model small \
  --report results/stt_evaluation_report.md
```

---

## 3. STT Pipeline

The current Topic 2 pipeline is:

```text
Audio / Video
  -> Audio preprocessing and noise reduction
  -> faster-whisper transcription
  -> Timestamped transcript segments
  -> Optional speaker diarization
  -> ChromaDB ingestion
  -> Multilingual RAG question answering
```

For live transcription:

```text
Microphone
  -> Browser audio capture
  -> PCM stream through WebSocket
  -> Silero VAD
  -> faster-whisper
  -> Live transcript segments
```

---

## 4. Demonstration Result

A first proof-of-concept test was performed on a real corporate audio document:

**Test file:** Nestle CEO speech about infant formula recall  
**Audio duration:** 4 minutes 9 seconds  
**Processing time:** 62 seconds on CPU  
**Real-Time Factor:** approximately 0.25  
**Model:** faster-whisper `small`, INT8 CPU mode  
**Language detection:** English detected automatically  
**Output:** 20 timestamped segments and approximately 3,000 characters of transcript

This result shows that the current local implementation can process audio faster than real time, even on limited hardware.

---

## 5. Important Finding

The system correctly transcribed the general content of the speech and allowed the RAG layer to answer questions about the announcement.

However, one important limitation was observed:

```text
Reference: Philippe Navratil
Transcription: Philippe Naruto
```

This error is useful for the research work because it shows the need for domain adaptation. Corporate names, brand names, technical terms, acronyms, and rare proper nouns may not be handled well by a general-purpose ASR model.

This directly supports the research direction:

**Improving real-time multilingual ASR for noisy corporate meetings through domain-aware prompting and speaker-aware preprocessing.**

---

## 6. Relationship with Topic 1 OCR

Topic 1 and Topic 2 are complementary.

| Topic | Input | Engine | Output | Shared Layer |
|---|---|---|---|---|
| Topic 1 - OCR | PDFs, scans, screenshots, images | OCR engine | Extracted text | ChromaDB + RAG |
| Topic 2 - STT | Audio, video, meetings | STT engine | Transcripts | ChromaDB + RAG |

Both topics produce text that can be indexed into the same private RAG system. This means the final platform can answer questions across both written and spoken corporate content.

Example:

```text
OCR source: scanned delivery document
STT source: recorded meeting or executive announcement
RAG layer: unified question answering over both sources
```

---

## 7. Academic Evaluation Plan

To make Topic 2 defensible as a Master Thesis contribution, the next step is to evaluate the system scientifically.

The evaluation will compare:

- baseline transcription without preprocessing;
- transcription with noise reduction;
- transcription with domain vocabulary prompt;
- transcription with forced language versus automatic language detection;
- different Whisper model sizes if available.

The evaluation metrics are:

| Metric | Meaning |
|---|---|
| WER | Word Error Rate, main transcription accuracy metric |
| CER | Character Error Rate, useful for proper nouns and spelling errors |
| RTF | Real-Time Factor, measures whether the system is faster than real time |
| Processing time | Total transcription time |

The dataset structure is:

```text
datasets/stt_eval/
  audio/
  references/
  metadata.csv
```

The `metadata.csv` file maps each audio file to its reference transcript, language, noise condition, speaker count, and notes.

---

## 8. Implemented vs Proposed

| Feature | Status |
|---|---|
| faster-whisper transcription | Implemented |
| Noise reduction | Implemented |
| Timestamped transcript segments | Implemented |
| Multilingual language detection | Implemented |
| Domain vocabulary prompt | Implemented |
| RAG ingestion of transcripts | Implemented |
| Multilingual Q&A over transcripts | Implemented |
| WebSocket live transcription | Implemented |
| Silero VAD for live speech detection | Implemented |
| pyannote diarization | Integrated, requires HF_TOKEN |
| WER/CER/RTF evaluation module | Implemented |
| Full benchmark dataset | To be completed |
| wav2vec 2.0 comparison | Future work |
| Conformer comparison | Future work |
| Fine-tuning on corporate vocabulary | Future work |
| Azure deployment | Future work |
| User accessibility study | Future work |

---

## 9. Known Limitations

The current PoC is strong enough for demonstration, but several points remain to be improved:

- the evaluation dataset still needs approved audio files and reference transcripts;
- diarization is integrated but not yet quantitatively evaluated;
- rare proper nouns may be misrecognized;
- Whisper model comparison is not yet fully automated;
- live transcription depends on browser microphone permissions and local compute performance;
- Azure migration is proposed but not yet implemented.

---

## 10. Next Steps

The next technical steps for Topic 2 are:

1. Add a small approved evaluation dataset.
2. Run WER/CER/RTF experiments under multiple conditions.
3. Generate the Markdown evaluation report.
4. Fix remaining edge cases in the evaluation script.
5. Align STT and OCR outputs under the same RAG metadata format.
6. Prepare a combined demo showing OCR + STT + RAG working together.

---

## 11. Summary for Collaboration

Topic 2 currently provides a working STT proof of concept for the multimodal accessibility platform. It can transcribe corporate audio/video files, reduce noise, generate timestamped transcripts, optionally identify speakers, and ingest transcripts into the shared private RAG system.

For integration with Topic 1, the most important point is that both OCR and STT now produce textual outputs that can be indexed into ChromaDB and queried through the same Q&A interface. This makes the platform coherent: written documents and spoken meetings become searchable through one private accessibility layer.

