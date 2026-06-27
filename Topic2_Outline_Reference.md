# Thesis Outline — Topic 2
# Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings
# BIT / Nestlé — OUEDRAOGO Yannick Ulrich Levi

---

## Chapter 1: Introduction (~1500 words)

### 1.1 Context and Motivation
- Corporate communication relies heavily on spoken content: meetings, video calls, training videos, executive announcements
- Employees with hearing impairments face systematic barriers in accessing spoken information
- Multinational organizations like Nestlé operate across multiple languages and time zones
- AI-driven Speech-to-Text systems can bridge this accessibility gap

### 1.2 Problem Statement
- Generic ASR models perform poorly in noisy corporate environments
- Multiple simultaneous speakers, background noise, and accented speech degrade transcription accuracy
- Domain-specific vocabulary (brand names, product names, acronyms) is frequently misrecognized
- Example: "Philippe Navratil" transcribed as "Philippe Naruto" — a real error observed during this project
- Real-time transcription latency must remain acceptable for live meeting use

### 1.3 Research Objectives
- Build and evaluate an STT engine optimized for noisy, multilingual corporate meetings
- Measure the impact of preprocessing, domain prompting, and model selection on transcription quality
- Integrate STT output into a shared private RAG knowledge base alongside OCR outputs (Topic 1)
- Propose an enterprise deployment path on Microsoft Azure

### 1.4 Research Questions
1. How do state-of-the-art transformer-based ASR models perform on noisy and multilingual corporate meeting audio?
2. How much do noise reduction and voice activity detection improve transcription quality (WER, CER)?
3. How can domain vocabulary prompts improve recognition of brand names, acronyms, and proper nouns?
4. Can the system process audio faster than real time on limited hardware (RTF < 1.0)?
5. How can STT outputs connect with OCR outputs in one private accessibility platform?

### 1.5 Contributions of This Work
- A working local STT pipeline (faster-whisper + noise reduction + VAD + diarization + RAG)
- An evaluation framework with WER, CER, and RTF on a corporate meeting dataset
- Empirical evidence on the impact of domain vocabulary prompting for corporate ASR
- An enterprise architecture proposal for Microsoft Azure deployment
- Integration design connecting Topic 1 (OCR) and Topic 2 (STT) through a shared RAG layer

### 1.6 Thesis Structure
- Overview of each chapter

---

## Chapter 2: Background and Foundational Concepts (~2000 words)

### 2.1 Automatic Speech Recognition — Core Concepts
- Definition and pipeline: audio → features → acoustic model → language model → transcript
- Key challenges: noise, accents, overlapping speech, out-of-vocabulary words

### 2.2 Evaluation Metrics
- Word Error Rate (WER): primary accuracy metric
- Character Error Rate (CER): useful for spelling and proper nouns
- Real-Time Factor (RTF): processing time divided by audio duration
- Latency: time from end of speech to final hypothesis

### 2.3 Corporate Meeting Characteristics
- Background noise types: HVAC, keyboard, room echo, side conversations
- Multi-speaker scenarios: overlapping speech, speaker turns
- Multilingual content: code-switching, accented speech
- Domain vocabulary: brand names, product codes, technical acronyms

### 2.4 Accessibility Context
- Hearing-impaired employees in the workplace
- Legal and ethical frameworks for workplace accessibility
- Role of ASR in inclusive corporate communication
- Impact of transcription errors on speaker perception (reference: Kadoma et al., 2026 — "Lost in Transcription")

---

## Chapter 3: Literature Review (~4000 words)

### 3.1 Evolution of ASR Architectures
- Traditional approaches: HMM, GMM-HMM, DNN-HMM
- End-to-end deep learning: CTC, attention encoder-decoder
- Transformer-based models: self-attention for long-range dependencies

### 3.2 Whisper — Large-Scale Multilingual ASR
- Architecture: encoder-decoder Transformer trained on 680,000 hours
- Multilingual support and automatic language detection
- Limitations: utterance-level timestamps, no native streaming
- WhisperX extension: forced alignment, word-level timestamps, speaker diarization (Bain et al., 2023)

### 3.3 wav2vec 2.0 and Self-Supervised Learning
- Pre-training on unlabeled audio with contrastive learning
- Fine-tuning with limited labeled data
- Use in forced phoneme alignment (WhisperX pipeline)

### 3.4 Conformer Architecture
- Combination of convolutional layers and self-attention
- Strong performance on speech benchmarks
- Comparison with Whisper in noisy conditions

### 3.5 Streaming and Low-Latency ASR
- RNN-Transducer (RNN-T) for frame-synchronous decoding
- Transformer Transducer for streaming with blockwise processing
- Sainath et al. (2020): on-device streaming model surpassing server-side quality
- Sklyar et al. (2021): streaming multi-speaker ASR with RNN-T
- Di Leo et al. (2025): real-time STT on edge with sub-second latency

### 3.6 Speaker Diarization
- Clustering-based approaches vs. end-to-end neural diarization
- pyannote-audio: speaker-diarization-community-1 model
- Integration with ASR for speaker-attributed transcripts
- Limitations: overlapping speech, variable speaker count

### 3.7 Noise Robustness Techniques
- Spectral subtraction and Wiener filtering
- Neural noise suppression (noisereduce library)
- Voice Activity Detection: Silero VAD
- Beamforming for multi-microphone arrays

### 3.8 Domain Adaptation for ASR
- Challenges of out-of-vocabulary corporate terms
- Initial prompt strategy in Whisper for domain vocabulary injection
- Transfer learning and fine-tuning on domain-specific data
- Ejigu et al. (2025): noise-robust ASR for low-resource languages — methodological parallel

### 3.9 Unified Audio Front-End Models
- UAF (Li et al., 2026): unified LLM combining VAD, turn-taking, speaker recognition, and ASR
- Full-duplex speech interaction as a future direction

### 3.10 Meeting Transcription Systems
- Raj et al. (2021): integration of speech separation, diarization, and recognition
- Yoshioka et al. (2019): online audio-visual meeting transcription
- Azure AI Speech: managed cloud transcription with speaker diarization

### 3.11 Research Gap
- No existing system addresses all three challenges simultaneously: noisy corporate audio, multilingual content, and domain-specific vocabulary in a private deployment
- This thesis targets this intersection

---

## Chapter 4: System Architecture and Design (~3000 words)

### 4.1 Overall Platform Architecture
- Three-topic integration: Topic 1 (OCR) + Topic 2 (STT) + Topic 3 (Accessibility Layer)
- Shared RAG layer: ChromaDB vector database + multilingual embeddings
- One unified question-answering interface over written and spoken content

### 4.2 STT Pipeline — File-Based Transcription
- Audio or video input
- Audio normalization (librosa, soundfile)
- Noise reduction (noisereduce)
- faster-whisper transcription with INT8 quantization
- Timestamped segment output (word-level and segment-level)
- Optional speaker diarization (pyannote)
- ChromaDB ingestion for RAG

### 4.3 STT Pipeline — Live Transcription
- Browser microphone capture
- WebSocket streaming (FastAPI WebSocket endpoint)
- Silero VAD for speech/silence detection
- faster-whisper transcription on speech segments
- Live transcript delivery to frontend

### 4.4 Domain Vocabulary Prompting
- Whisper initial_prompt parameter for injecting corporate vocabulary
- Strategy: brand names, product names, key acronyms, executive names
- Expected impact on WER for named entities

### 4.5 API Design
- POST /transcribe: file upload, transcription, RAG indexing
- WS /ws/transcribe: live WebSocket transcription
- POST /ocr: OCR input from Topic 1
- POST /ask: RAG question answering over all indexed content
- GET /health: service monitoring

### 4.6 Technology Stack
- Backend: FastAPI (Python)
- ASR engine: faster-whisper (CTranslate2 backend)
- Audio processing: librosa, soundfile, noisereduce
- VAD: Silero VAD
- Diarization: pyannote-audio
- Embeddings: intfloat/multilingual-e5-small
- Vector database: ChromaDB
- Local LLM: Ollama / Llama 3.2
- Frontend: HTML, CSS, JavaScript

### 4.7 Azure Enterprise Architecture
- Azure AI Speech for production STT
- Azure AI Search for transcript and document retrieval
- Azure OpenAI Service for Q&A and summaries
- Azure Blob Storage for audio and transcripts
- Microsoft Entra ID for authentication
- Azure Key Vault for secrets
- Microsoft Graph API for Teams, Outlook, SharePoint integration

---

## Chapter 5: Methodology and Experimental Setup (~3000 words)

### 5.1 Dataset Construction
- Requirements: corporate meeting audio, multiple noise conditions, multilingual content, domain vocabulary
- Audio sources: publicly available corporate speech, simulated meeting recordings
- Reference transcripts: manually verified ground truth
- Dataset structure: datasets/stt_eval/audio/ + references/ + metadata.csv
- Metadata fields: filename, reference, language, noise_condition, speaker_count, notes

### 5.2 Evaluation Framework
- WER computation: substitutions + deletions + insertions / total reference words
- CER computation: character-level equivalent of WER
- RTF computation: processing_time / audio_duration
- Tools: jiwer library for WER/CER

### 5.3 Experimental Conditions
- Condition A: Baseline — faster-whisper without any preprocessing
- Condition B: Noise reduction applied (noisereduce)
- Condition C: VAD preprocessing with Silero
- Condition D: Domain vocabulary prompt injected
- Condition E: Automatic language detection vs. forced language
- Condition F: Model size comparison (small / medium / large-v2)

### 5.4 Evaluation Hypotheses
- H1: Noise reduction will reduce WER on noisy recordings without impacting clean audio
- H2: Domain vocabulary prompts will reduce WER on named entities (brand names, executive names)
- H3: The system will achieve RTF < 1.0 on CPU hardware across all model sizes tested
- H4: Forced language detection will outperform automatic detection on short segments

### 5.5 Hardware and Runtime Environment
- CPU: [specify]
- RAM: [specify]
- Quantization: INT8 via CTranslate2
- Operating system: [specify]

---

## Chapter 6: Results and Analysis (~3500 words)

### 6.1 Baseline Transcription Results
- WER and CER on clean audio
- WER and CER on noisy audio
- RTF measurements across model sizes

### 6.2 Impact of Noise Reduction
- WER comparison: without vs. with noisereduce
- Impact on clean audio (regression check)
- Processing time overhead

### 6.3 Domain Vocabulary Prompting — The Corporate Name Problem
- Case study: "Philippe Navratil" → "Philippe Naruto" (observed during PoC)
- Systematic evaluation on a set of Nestlé executive names, brand names, and acronyms
- WER with empty prompt vs. domain-aware prompt
- Analysis: which entity types benefit most

### 6.4 Multilingual Transcription Performance
- WER per language: English, French, German
- Language detection accuracy (automatic vs. forced)
- Code-switching behavior

### 6.5 Real-Time Factor Analysis
- RTF = 0.25 achieved on CPU with small model + INT8 quantization
- RTF across model sizes
- Feasibility assessment for live meeting use

### 6.6 Speaker Diarization Results
- Diarization Error Rate (DER)
- Speaker label accuracy on simulated multi-speaker recordings
- Known limitation: overlapping speech

### 6.7 Comparison: faster-whisper vs. Azure AI Speech (Pilot)
- WER comparison on pilot dataset
- Latency comparison
- Cost and privacy trade-offs

### 6.8 Discussion
- Which research questions are answered by the results
- Unexpected findings
- Limitations of the current evaluation

---

## Chapter 7: Integration and Deployment (~2000 words)

### 7.1 Topic 1 and Topic 2 Integration
- Shared ChromaDB vector store for OCR and STT outputs
- Unified /ask endpoint combining written and spoken knowledge
- Example query spanning both sources

### 7.2 Live Transcription Prototype
- WebSocket latency measurements
- User experience observations

### 7.3 Azure Deployment Pilot
- Pilot scope: 5–10 files, English/French/German, clean and noisy audio
- Azure AI Speech configuration
- Security controls: Entra ID, Key Vault, encrypted storage
- Cost measurements vs. estimates

### 7.4 Security and Compliance
- Consent requirements for meeting recordings
- Transcript retention policy
- Role-based access control
- Audit logging

---

## Chapter 8: Conclusion and Future Work (~1500 words)

### 8.1 Summary of Contributions
- Functional STT pipeline for corporate accessibility
- Empirical evaluation of noise reduction and domain prompting on WER
- RTF validation on limited hardware
- Enterprise architecture design for Nestlé

### 8.2 Answers to Research Questions
- One paragraph per research question summarizing findings

### 8.3 Limitations
- Dataset size constraints
- Diarization quality on heavily overlapping speech
- Domain prompts require manual vocabulary curation
- No fine-tuning on Nestlé-specific data yet

### 8.4 Future Work
- Fine-tuning Whisper on Nestlé-specific audio data
- Conformer model evaluation and comparison
- Real-time Teams meeting plugin development
- Accessibility user study with hearing-impaired employees
- Reinforcement learning from user correction feedback (Topic 3 link)

---

## References

- Bain et al. (2023) — WhisperX: Time-Accurate Speech Transcription (INTERSPEECH 2023)
- Baevski et al. (2020) — wav2vec 2.0 (NeurIPS 2020)
- Radford et al. (2022) — Robust Speech Recognition via Large-Scale Weak Supervision (OpenAI Whisper)
- Gulati et al. (2020) — Conformer: Convolution-augmented Transformer for ASR (Interspeech 2020)
- Sainath et al. (2020) — Streaming On-Device E2E Model (ICASSP 2020)
- Sklyar et al. (2021) — Streaming Multi-Speaker ASR with RNN-T (ICASSP 2021)
- Raj et al. (2021) — Integration of Speech Separation, Diarization, and Recognition (SLT 2021)
- Di Leo et al. (2025) — Real-Time STT on Edge (Information 2025)
- Ejigu et al. (2025) — Noise-Robust End-to-End ASR for Amharic (2025)
- Li et al. (2026) — UAF: Unified Audio Front-end LLM (2026)
- Kadoma et al. (2026) — Lost in Transcription (CHI 2026)

---

## Appendices

### Appendix A: Dataset Metadata Structure
- metadata.csv column definitions and example rows

### Appendix B: API Documentation
- Full endpoint specifications with request/response examples

### Appendix C: Azure Architecture Diagram
- Full infrastructure diagram with service connections

### Appendix D: Full Experimental Results Tables
- Complete WER/CER/RTF tables for all experimental conditions

### Appendix E: Domain Vocabulary Prompt Examples
- Example prompts used for Nestlé brand names and executive names

### Appendix F: AI Usage Acknowledgment
- Declaration of AI tools used in writing and editing this thesis
