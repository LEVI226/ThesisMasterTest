# Topic 2 Report
## Speech-to-Text Engine for Noisy, Multilingual Corporate Meetings

**Project:** AI-Driven Multimodal Accessibility Platform  
**Organization:** BIT / Nestle  
**Student:** Ulric GOUET-ZONGO  
**Framework:** Private Retrieval-Augmented Generation  
**Date:** 7 May 2026  
**Status:** Proof of Concept completed. Azure pilot proposed.

## 1. Executive Summary

This report presents the Speech-to-Text work for Topic 2 of the multimodal accessibility platform.

The goal is to help employees access spoken corporate content. The system transcribes meetings, announcements, training videos, and audio files. It then stores the transcript in a private knowledge base so users can search it or ask questions in natural language.

The local Proof of Concept already transcribes audio and video files with faster-whisper. It reduces background noise, generates timestamps, supports multilingual transcription, and sends the transcript to the shared RAG layer. The same platform also receives OCR output from Topic 1, so written and spoken content can use one knowledge base.

For Nestle, the recommended enterprise path uses Microsoft Azure:

- Azure AI Speech for production speech-to-text.
- Azure AI Search for transcript and document retrieval.
- Azure OpenAI Service for Q&A, summaries, and accessibility assistance.
- Azure Blob Storage for audio, documents, and transcripts.
- Microsoft Entra ID for authentication.
- Azure Key Vault for secrets.
- Microsoft Graph API for Teams, Outlook, and SharePoint integration.

The local faster-whisper engine should remain the research baseline. Azure AI Speech should support the enterprise pilot and production deployment.

## 2. Research Context

Corporate communication depends on meetings, calls, recorded speeches, presentations, and training videos. Employees with hearing impairments can miss important information when these formats do not include accurate captions or transcripts.

Speech-to-text systems work well with clean audio. Corporate meetings create harder conditions. Speakers may talk over each other. Microphones may capture room noise. Participants may use different accents or switch languages. Company names, product names, acronyms, and technical terms may not appear in common ASR training data.

Topic 2 focuses on this research direction:

**Improving real-time multilingual ASR for noisy corporate meetings through domain-aware prompting and speaker-aware preprocessing.**

## 3. Research Objective

The objective is to build and evaluate an STT engine that supports corporate meeting accessibility.

The system must:

- transcribe audio and video files;
- handle noisy recordings;
- support multilingual speech;
- produce timestamped transcript segments;
- support speaker labels where possible;
- index transcripts into a private RAG layer;
- support evaluation with WER, CER, and Real-Time Factor.

## 4. Research Questions

1. How do modern ASR models perform on noisy and multilingual corporate meeting audio?
2. How much do noise reduction and voice activity detection improve transcription quality?
3. How can domain vocabulary prompts improve recognition of brand names, acronyms, and proper nouns?
4. Can the system process audio faster than real time on limited hardware?
5. How can STT outputs connect with OCR outputs in one private accessibility platform?

## 5. Current Proof of Concept

The PoC runs as part of the existing FastAPI platform.

| Component | Implementation |
|---|---|
| Backend | FastAPI |
| STT engine | faster-whisper |
| Audio preprocessing | librosa, soundfile, noisereduce |
| Language detection | Whisper automatic detection |
| Timestamping | Whisper segment and word timestamps |
| Speaker diarization | pyannote, with Hugging Face token |
| Live transcription | WebSocket and browser microphone stream |
| Voice activity detection | Silero VAD |
| Vector database | ChromaDB |
| Embeddings | intfloat/multilingual-e5-small |
| Local LLM | Ollama with Llama 3.2 |
| Evaluation | WER, CER, RTF |
| Frontend | HTML, CSS, JavaScript |

Main API endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /transcribe` | Upload audio or video, transcribe it, and index the transcript |
| `WS /ws/transcribe` | Stream microphone audio for live transcription |
| `POST /ocr` | Extract text from PDF or image files |
| `POST /ask` | Ask questions over indexed OCR and STT content |
| `GET /health` | Check service status |

## 6. STT Pipeline

The file-based STT pipeline follows this flow:

```text
Audio or video file
  -> audio normalization
  -> noise reduction
  -> faster-whisper transcription
  -> timestamped transcript segments
  -> optional speaker diarization
  -> ChromaDB indexing
  -> RAG question answering
```

The live transcription flow follows this flow:

```text
Microphone
  -> browser audio capture
  -> WebSocket stream
  -> Silero voice activity detection
  -> faster-whisper transcription
  -> live transcript segments
```

## 7. Demonstration Result

The PoC processed a real corporate audio file: a Nestle executive speech about an infant formula recall.

| Item | Result |
|---|---|
| Audio duration | 4 minutes 9 seconds |
| Processing time | 62 seconds |
| Real-Time Factor | about 0.25 |
| Model | faster-whisper `small` |
| Runtime | CPU with INT8 quantization |
| Language detection | English detected |
| Transcript output | 20 timestamped segments |
| Transcript size | about 3,000 characters |
| RAG ingestion | Successful |

The result shows that the local system can process audio faster than real time on limited hardware.

One limitation appeared during the test:

```text
Expected: Philippe Navratil
Generated: Philippe Naruto
```

This error matters for the thesis. It shows that the model can miss rare names and corporate vocabulary. Topic 2 can use this case to evaluate domain prompts, custom vocabulary, and future fine-tuning.

## 8. Link with Topic 1 OCR

Topic 1 and Topic 2 use different inputs but feed the same platform.

| Topic | Input | Engine | Output | Shared Layer |
|---|---|---|---|---|
| Topic 1 | PDFs, scans, screenshots, images | OCR | Extracted text | ChromaDB and RAG |
| Topic 2 | Audio, video, meetings | STT | Transcripts | ChromaDB and RAG |
| Topic 3 | OCR and STT outputs | Accessibility layer | Personalized answers | Web or Teams interface |

This design lets Nestle users search both written and spoken content through one private assistant.

Example:

```text
OCR source: scanned delivery document
STT source: recorded meeting
Shared RAG layer: one answer interface for both sources
```

## 9. Evaluation Plan

The thesis evaluation will compare transcription quality and processing speed across several conditions.

Metrics:

| Metric | Meaning |
|---|---|
| WER | Word Error Rate. Main accuracy metric. |
| CER | Character Error Rate. Useful for spelling and proper nouns. |
| RTF | Real-Time Factor. Processing time divided by audio duration. |
| Processing time | Total time needed to transcribe one file. |

Evaluation conditions:

- baseline transcription without preprocessing;
- transcription with noise reduction;
- transcription with domain vocabulary prompt;
- automatic language detection compared with forced language;
- different Whisper model sizes when hardware allows it.

Dataset structure:

```text
datasets/stt_eval/
  audio/
  references/
  metadata.csv
```

The metadata file should include the audio filename, reference transcript, language, noise condition, speaker count, and notes.

## 10. Microsoft Azure Deployment

Nestle should deploy the enterprise version on Microsoft Azure. This keeps the platform close to the Microsoft 365 environment and supports security, governance, monitoring, and scale.

Target architecture:

```text
Teams / Outlook / SharePoint
        |
        | Microsoft Graph API
        v
Azure API Management
        |
        v
Application backend
        |
        |--------------------------|
        |                          |
        v                          v
Azure AI Speech              Azure Blob Storage
        |                    audio, documents, transcripts
        v
Transcript processing
        |
        v
Azure AI Search
        |
        v
Azure OpenAI Service
        |
        v
Accessible web portal or Teams app
```

Recommended Microsoft services:

| Requirement | Microsoft Service | Role |
|---|---|---|
| Speech-to-text | Azure AI Speech | Batch and live transcription |
| Q&A and summaries | Azure OpenAI Service | RAG answers and transcript summaries |
| Search | Azure AI Search | Vector and keyword retrieval |
| Storage | Azure Blob Storage | Audio, documents, transcripts |
| Login | Microsoft Entra ID | Employee authentication |
| Secrets | Azure Key Vault | Keys, tokens, certificates |
| Hosting | Azure App Service or Azure Container Apps | Backend deployment |
| API governance | Azure API Management | Access control and monitoring |
| Logs | Azure Monitor and Application Insights | Performance and errors |
| Governance | Microsoft Purview | Retention and compliance |
| Microsoft 365 integration | Microsoft Graph API | Teams, Outlook, SharePoint |

## 11. Deployment Plan

### Phase 1: Local PoC

Use the current local system to validate the research work.

This phase supports:

- thesis experiments;
- WER, CER, and RTF measurement;
- testing of noise reduction and domain prompts;
- demonstrations without cloud cost.

### Phase 2: Azure Pilot

Deploy a controlled pilot with approved users and approved data.

Recommended pilot scope:

- 5 to 10 audio or video files;
- English, French, and German samples;
- clean and noisy audio;
- 5 to 10 internal users;
- limited transcript retention;
- Entra ID authentication.

The pilot should measure accuracy, latency, user usefulness, security, and monthly cost.

### Phase 3: Microsoft 365 Integration

Connect the platform to workplace tools after the pilot.

Possible integrations:

- Teams meeting recordings;
- Teams transcript workflows;
- Outlook meeting summaries;
- SharePoint document libraries;
- internal accessibility portal.

### Phase 4: Production

Move to production after Nestle validates security, cost, performance, and user value.

Production must include:

- access control;
- audit logs;
- encryption;
- monitoring;
- cost alerts;
- retention rules;
- support process;
- security review.

## 12. Cost Estimate

These figures give planning ranges. Nestle should confirm final costs with the Azure Pricing Calculator, selected region, enterprise agreement, and expected monthly usage.

Main cost drivers:

| Cost Driver | Impact |
|---|---|
| Audio hours | Increases Azure AI Speech cost |
| Live transcription | Can increase compute and STT cost |
| LLM usage | Increases Azure OpenAI token cost |
| Search index size | Increases Azure AI Search cost |
| Storage volume | Increases Blob Storage cost |
| Backend compute | Increases hosting cost |
| Monitoring | Increases log ingestion cost |
| Security controls | May add Key Vault, private endpoints, or governance cost |

### Scenario A: Research or Small PoC

| Component | Choice |
|---|---|
| STT | Local faster-whisper or limited Azure AI Speech |
| LLM | Local Ollama or low-volume Azure OpenAI |
| Search | ChromaDB or Azure AI Search Free/Basic |
| Hosting | Local machine or small App Service |
| Storage | Small Blob Storage account |

Estimated monthly cost: **50 to 300 USD**.

### Scenario B: Azure Pilot

| Component | Choice |
|---|---|
| STT | Azure AI Speech |
| LLM | Azure OpenAI, cost-efficient model |
| Search | Azure AI Search Basic or S1 |
| Backend | Azure App Service or Container Apps |
| Storage | Azure Blob Storage |
| Security | Entra ID and Key Vault |
| Monitoring | Application Insights |

Estimated monthly cost: **300 to 1,500 USD**.

### Scenario C: Enterprise Production

| Component | Choice |
|---|---|
| STT | Azure AI Speech at scale, or self-hosted Whisper on GPU for high volume |
| LLM | Azure OpenAI with token budgets |
| Search | Azure AI Search S1/S2 or higher |
| Backend | Container Apps or AKS |
| Storage | Blob Storage with lifecycle policies |
| Security | Entra ID, Key Vault, private endpoints if required |
| Governance | Microsoft Purview |
| Monitoring | Azure Monitor and cost alerts |

Estimated monthly cost: **1,500 to 5,000+ USD**.

## 13. Azure AI Speech or Self-Hosted Whisper

Nestle has two realistic options for STT.

| Option | Strengths | Limits | Best Use |
|---|---|---|---|
| Azure AI Speech | Managed service, Microsoft support, simple deployment, Microsoft 365 fit | Cost depends on audio volume, less model control | Pilot and production |
| Self-hosted Whisper on Azure GPU | More control, useful for research, may reduce cost at high volume | Requires GPU management, scaling, patching, monitoring | Research and high-volume analysis |

Recommendation:

```text
Use Azure AI Speech for the Nestle pilot and production path.
Keep faster-whisper for research, benchmarking, and custom experiments.
```

## 14. Security and Compliance

The platform may process confidential meetings and internal documents. Nestle should define security rules before the pilot.

Required controls:

- Microsoft Entra ID login;
- role-based access control;
- Azure Key Vault for secrets;
- encryption at rest and in transit;
- restricted Blob Storage permissions;
- audit logging;
- transcript retention policy;
- separation between test and production data;
- no hardcoded API keys;
- consent rules for recorded meetings.

Questions for Nestle:

- Which users can upload recordings?
- Which users can view transcripts?
- How long should transcripts stay available?
- Should the system delete audio after transcription?
- Which departments can query indexed content?
- Which meetings can use live transcription?

## 15. Implemented and Proposed Features

| Feature | Status |
|---|---|
| faster-whisper transcription | Implemented |
| Noise reduction | Implemented |
| Timestamped transcripts | Implemented |
| Multilingual detection | Implemented |
| Domain vocabulary prompt | Implemented |
| Transcript ingestion into RAG | Implemented |
| Multilingual Q&A | Implemented |
| WebSocket live transcription | Implemented |
| Silero VAD | Implemented |
| pyannote diarization | Integrated, requires token |
| WER, CER, RTF evaluation | Implemented |
| Benchmark dataset | To complete |
| Azure AI Speech deployment | Proposed |
| Azure AI Search migration | Proposed |
| Azure OpenAI migration | Proposed |
| Teams, Outlook, SharePoint integration | Proposed |
| Accessibility user study | Future work |

## 16. Final Recommendation

The current PoC proves that the platform can turn spoken corporate content into searchable text. It also shows a clear research problem: generic ASR models can miss corporate names and domain vocabulary.

Nestle should run a controlled Azure pilot before any production rollout. The pilot should use Azure AI Speech, Azure AI Search, Azure OpenAI, Blob Storage, Entra ID, and Key Vault. The local faster-whisper system should remain available for thesis experiments and model comparison.

The next step is to add an approved evaluation dataset, run WER/CER/RTF experiments, and compare local faster-whisper results with Azure AI Speech results during the pilot.

