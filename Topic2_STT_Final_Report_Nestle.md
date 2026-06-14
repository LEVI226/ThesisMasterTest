# Executive and Technical Report
## Topic 2 - Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings

**Project:** AI-Driven Multimodal Accessibility Platform for Inclusive Workplace Communication  
**Organization:** BIT / Nestle  
**Student:** Ulric GOUET-ZONGO  
**Framework:** Private Retrieval-Augmented Generation (Private-RAG)  
**Document purpose:** Technical, business, and deployment summary for collaboration and Nestle review  
**Date:** 7 May 2026  
**Status:** Proof of Concept completed; enterprise pilot proposed

---

## 1. Executive Summary

This document presents the current status and deployment plan for **Topic 2: Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings**.

The objective of this topic is to develop and evaluate a Speech-to-Text (STT) engine capable of transcribing corporate audio and video content, including meetings, executive announcements, and multimedia files, in noisy, multilingual, and multi-speaker environments.

The work supports the global accessibility objective of the project: making workplace communication more inclusive for employees with hearing impairments by providing accurate live captions, timestamped transcripts, searchable meeting content, and multilingual question answering.

The current proof of concept demonstrates that a private local STT pipeline can:

- transcribe corporate audio/video files;
- support multilingual speech recognition;
- reduce background noise before transcription;
- generate timestamped transcript segments;
- optionally assign speaker labels through diarization;
- ingest transcripts into a private vector database;
- enable multilingual Q&A over transcribed content;
- provide a basis for academic evaluation using WER, CER, and Real-Time Factor.

For an enterprise deployment at Nestle, the recommended path is to migrate the validated PoC to a Microsoft Azure architecture using **Azure AI Speech**, **Azure OpenAI Service**, **Azure AI Search**, **Azure Blob Storage**, **Microsoft Entra ID**, **Azure Key Vault**, and **Microsoft Graph API** for future integration with Teams, Outlook, and SharePoint.

---

## 2. Research Context

Modern multinational companies rely heavily on audio and video communication: online meetings, presentations, recorded announcements, training videos, and collaborative discussions. However, these communication formats can create accessibility barriers for employees with hearing impairments when accurate captions or transcripts are not available.

Current automatic speech recognition systems perform well in controlled conditions, but corporate meeting environments remain challenging because they often include:

- background noise;
- multiple speakers;
- overlapping speech;
- different accents;
- multilingual content;
- domain-specific vocabulary;
- company names, product names, acronyms, and technical terms;
- real-time latency constraints.

This topic therefore focuses on the following research direction:

**Improving real-time multilingual ASR for noisy corporate meetings through domain-aware prompting and speaker-aware preprocessing.**

This framing is aligned with the original research proposal, which defines Topic 2 as the STT engine of the multimodal accessibility platform.

---

## 3. Research Objective and Questions

### 3.1 Objective

The objective is to design, implement, and evaluate a robust STT system for corporate meetings and video communications. The system must support noisy environments, multilingual speech, speaker-aware transcription, and accessibility use cases.

### 3.2 Research Questions

1. How do modern ASR models perform in noisy and multilingual corporate meeting scenarios?
2. To what extent can preprocessing techniques such as noise reduction and voice activity detection improve transcription quality?
3. How can domain-aware prompting or domain adaptation improve the recognition of corporate vocabulary, brand names, acronyms, and proper nouns?
4. How can real-time transcription latency be minimized while maintaining acceptable accuracy?
5. How can STT outputs be integrated into a private RAG platform for accessibility and information retrieval?

---

## 4. Current Proof of Concept

The current PoC has been implemented as part of a multimodal AI accessibility platform.

### 4.1 Implemented Components

| Component | Current Implementation |
|---|---|
| API backend | FastAPI |
| STT engine | faster-whisper |
| Audio preprocessing | librosa, soundfile, noisereduce |
| Language detection | Whisper automatic language detection |
| Timestamped transcription | Word/segment timestamps |
| Speaker diarization | pyannote, enabled when HF_TOKEN is configured |
| Live transcription | WebSocket + browser microphone stream |
| Voice activity detection | Silero VAD |
| Vector database | ChromaDB |
| Embedding model | intfloat/multilingual-e5-small |
| Local LLM | Ollama + Llama 3.2 |
| Evaluation module | WER, CER, RTF |
| Frontend | HTML/CSS/JavaScript |

### 4.2 Main API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /transcribe` | Upload audio/video, transcribe with STT, ingest transcript into RAG |
| `WS /ws/transcribe` | Real-time speech-to-text through WebSocket |
| `POST /ocr` | Upload PDF/image, extract text, ingest into RAG |
| `POST /ask` | Ask questions over indexed STT/OCR content |
| `GET /health` | Check platform status |

---

## 5. STT Pipeline

The current Topic 2 pipeline is:

```text
Audio / Video Input
  -> Audio normalization and noise reduction
  -> faster-whisper transcription
  -> Timestamped transcript segments
  -> Optional speaker diarization
  -> Transcript ingestion into ChromaDB
  -> RAG-based multilingual Q&A
  -> Accessible output for users
```

For live transcription:

```text
Microphone Input
  -> Browser audio capture
  -> PCM stream through WebSocket
  -> Silero Voice Activity Detection
  -> faster-whisper transcription
  -> Live transcript segments with timestamps
```

---

## 6. Demonstration Result

A first demonstration was performed using a real corporate audio document: a Nestle executive speech related to an infant formula recall.

| Item | Result |
|---|---|
| Audio duration | 4 minutes 9 seconds |
| Processing time | 62 seconds |
| Real-Time Factor | approximately 0.25 |
| Model | faster-whisper `small` |
| Runtime mode | CPU, INT8 quantization |
| Language detection | English detected automatically |
| Output | 20 timestamped transcript segments |
| Transcript size | approximately 3,000 characters |
| RAG ingestion | Successful |

The result demonstrates that the current local pipeline can process audio faster than real time even on limited hardware.

### Important Finding

The system successfully captured the general meaning of the speech, but one proper noun was incorrectly transcribed:

```text
Expected: Philippe Navratil
Generated: Philippe Naruto
```

This is an important research finding. It shows that generic ASR models can struggle with rare corporate names and domain-specific vocabulary. This directly motivates the use of domain-aware prompting, custom vocabulary strategies, and future fine-tuning.

---

## 7. Relationship with Topic 1 OCR

Topic 1 and Topic 2 are complementary parts of the same multimodal accessibility platform.

| Topic | Input | Processing Engine | Output | Shared Layer |
|---|---|---|---|---|
| Topic 1 - OCR | PDFs, scans, screenshots, images | OCR engine | Extracted text | ChromaDB + RAG |
| Topic 2 - STT | Audio, video, meetings | STT engine | Transcripts | ChromaDB + RAG |
| Topic 3 - Accessibility layer | OCR + STT outputs | Personalization/RAG | Accessible answers | UI / assistant |

The final system should allow Nestle employees to query both written and spoken corporate content through the same private accessibility interface.

Example:

```text
OCR source: scanned delivery document
STT source: recorded meeting
RAG layer: unified Q&A over both document and meeting content
```

---

## 8. Academic Evaluation Plan

To make the STT topic academically defensible, the PoC must be evaluated with measurable metrics.

### 8.1 Evaluation Metrics

| Metric | Meaning | Purpose |
|---|---|---|
| WER | Word Error Rate | Measures word-level transcription accuracy |
| CER | Character Error Rate | Measures spelling and proper noun accuracy |
| RTF | Real-Time Factor | Measures processing speed versus audio duration |
| Processing time | Total inference time | Measures system latency |

### 8.2 Evaluation Conditions

The evaluation will compare:

- baseline transcription without preprocessing;
- transcription with noise reduction;
- transcription with domain vocabulary prompt;
- automatic language detection versus forced language;
- different Whisper model sizes when available.

### 8.3 Dataset Structure

```text
datasets/stt_eval/
  audio/
  references/
  metadata.csv
```

The metadata file maps each audio file to:

- reference transcript;
- language;
- noise condition;
- speaker count;
- notes.

---

## 9. Recommended Microsoft Azure Architecture

For Nestle-facing deployment, the recommended production architecture is based on Microsoft Azure and Microsoft 365.

```text
Microsoft Teams / Outlook / SharePoint
        |
        | Microsoft Graph API
        v
Azure API Management
        |
        v
FastAPI Backend / Application Layer
        |
        |-----------------------------|
        |                             |
        v                             v
Azure AI Speech                Azure Blob Storage
Speech-to-Text                 Audio, documents, transcripts
        |
        v
Transcript processing
Noise handling, timestamps, speaker labels
        |
        v
Azure AI Search
Vector and hybrid search index
        |
        v
Azure OpenAI Service
Q&A, summarization, accessibility assistant
        |
        v
Accessible Web Portal / Teams App
```

### 9.1 Recommended Microsoft Services

| Requirement | Microsoft Service | Role |
|---|---|---|
| Speech-to-text | Azure AI Speech | Real-time and batch transcription |
| LLM reasoning | Azure OpenAI Service | Q&A, summarization, explanation |
| Vector search | Azure AI Search | RAG retrieval |
| Storage | Azure Blob Storage | Store audio, documents, transcripts |
| Authentication | Microsoft Entra ID | Employee login and access control |
| Secret management | Azure Key Vault | Secure keys and tokens |
| Hosting | Azure App Service or Azure Container Apps | Host backend services |
| API governance | Azure API Management | Secure and monitor APIs |
| Monitoring | Azure Monitor + Application Insights | Logs, metrics, errors, latency |
| Compliance | Microsoft Purview | Data governance and retention |
| Microsoft 365 integration | Microsoft Graph API | Teams, Outlook, SharePoint integration |

---

## 10. Deployment Plan

### Phase 1 - Local Research PoC

Current state.

Purpose:

- validate feasibility;
- run early experiments;
- avoid cloud cost;
- keep data local;
- prepare academic evaluation.

### Phase 2 - Azure Pilot

Purpose:

- test enterprise services on a small controlled scope;
- validate Azure AI Speech quality;
- evaluate Azure OpenAI + Azure AI Search for RAG;
- test authentication through Entra ID;
- monitor cost and latency.

Recommended pilot scope:

- 5 to 10 approved audio/video files;
- 2 to 3 languages;
- clean and noisy samples;
- 5 to 10 internal users;
- limited retention policy.

### Phase 3 - Microsoft 365 Integration

Purpose:

- connect the platform to existing workplace tools.

Possible integrations:

- Teams meeting recordings;
- Teams transcript/caption workflows;
- Outlook meeting summaries;
- SharePoint document libraries;
- internal accessibility portal.

Integration should use Microsoft Graph API and Entra ID permissions.

### Phase 4 - Production Deployment

Purpose:

- deploy a secure and scalable service for broader use.

Production requirements:

- access control;
- audit logs;
- encryption;
- cost monitoring;
- backup and retention policy;
- support process;
- security review;
- compliance validation.

---

## 11. Cost Estimate

The following estimates are planning ranges. Final costs must be validated using the official Azure Pricing Calculator and Nestle's selected Azure region, enterprise agreement, and security requirements.

### 11.1 Main Cost Drivers

| Cost Driver | Description |
|---|---|
| Audio hours | More meeting hours increase STT cost |
| Real-time usage | Live transcription can cost more than batch workflows |
| LLM tokens | Q&A and summaries consume Azure OpenAI tokens |
| Search index size | More documents/transcripts require more search capacity |
| Storage | Audio/video files require Blob Storage |
| Compute | Backend hosting and optional GPU instances |
| Monitoring | Logs and telemetry volume |
| Security/governance | Key Vault, private networking, compliance tools |

### 11.2 Scenario A - Research / Small PoC

| Component | Suggested Choice |
|---|---|
| STT | Local faster-whisper or limited Azure AI Speech |
| LLM | Local Ollama or low-volume Azure OpenAI |
| Search | ChromaDB or Azure AI Search Free/Basic |
| Hosting | Local or small App Service |
| Storage | Small Azure Blob Storage account |

**Estimated monthly range:** 50 to 300 USD/month.

Best for:

- thesis validation;
- small demos;
- limited data;
- no production SLA.

### 11.3 Scenario B - Azure Pilot for Nestle Team

| Component | Suggested Choice |
|---|---|
| STT | Azure AI Speech |
| LLM | Azure OpenAI, preferably cost-efficient model such as GPT-4o mini |
| Search | Azure AI Search Basic or S1 |
| Backend | Azure App Service or Azure Container Apps |
| Storage | Azure Blob Storage |
| Security | Entra ID + Key Vault |
| Monitoring | Application Insights |

**Estimated monthly range:** 300 to 1,500 USD/month.

Best for:

- small internal pilot;
- controlled group of users;
- realistic Microsoft security model;
- validation before production.

### 11.4 Scenario C - Enterprise Production

| Component | Suggested Choice |
|---|---|
| STT | Azure AI Speech at scale, or self-hosted Whisper on GPU for high volume |
| LLM | Azure OpenAI with token budgets |
| Search | Azure AI Search S1/S2 or higher |
| Backend | Azure Container Apps or AKS |
| Storage | Blob Storage with lifecycle policies |
| Security | Entra ID, Key Vault, private endpoints if required |
| Governance | Microsoft Purview |
| Monitoring | Azure Monitor + cost alerts |

**Estimated monthly range:** 1,500 to 5,000+ USD/month.

Best for:

- multiple departments;
- higher audio volume;
- production monitoring;
- stronger governance and compliance.

---

## 12. Azure AI Speech vs Self-Hosted Whisper

### Option 1 - Azure AI Speech

Advantages:

- managed Microsoft enterprise service;
- easier deployment and support;
- real-time and batch transcription;
- native fit with Azure and Microsoft 365;
- no GPU management;
- better enterprise governance.

Limitations:

- cost depends on audio volume;
- less control over model internals;
- customization depends on Azure capabilities.

Recommended for:

- Nestle pilot;
- production deployment;
- Microsoft ecosystem alignment.

### Option 2 - Self-Hosted Whisper on Azure GPU

Advantages:

- more control over model and preprocessing;
- useful for research benchmarking;
- can be cost-effective for high-volume workloads;
- supports custom experimentation.

Limitations:

- requires GPU VM management;
- requires scaling, monitoring, and patching;
- more engineering work;
- production support is more complex.

Recommended for:

- research experiments;
- comparing model sizes;
- future domain adaptation tests;
- high-volume scenario if cost analysis supports it.

### Recommended Choice

For Nestle-facing deployment:

```text
Use Azure AI Speech for the enterprise pilot and production path.
Keep faster-whisper as the research baseline and experimental engine.
```

This approach balances enterprise reliability with academic research flexibility.

---

## 13. Security and Compliance

Because the platform may process corporate meetings and confidential content, security must be designed from the beginning.

Recommended controls:

- Microsoft Entra ID authentication;
- role-based access control;
- Azure Key Vault for secrets;
- encryption in transit and at rest;
- restricted Blob Storage permissions;
- audit logging;
- data retention policy;
- private endpoints if required;
- no hardcoded API keys;
- separation between test data and production data;
- clear consent policy for meeting transcription.

Questions to clarify with Nestle:

- Who can upload recordings?
- Who can view transcripts?
- How long should transcripts be stored?
- Should audio be deleted after transcription?
- Which departments can query indexed content?
- Is live transcription allowed for all meetings or only selected ones?

---

## 14. Implemented vs Proposed

| Feature | Status |
|---|---|
| faster-whisper transcription | Implemented |
| Noise reduction | Implemented |
| Timestamped transcripts | Implemented |
| Multilingual detection | Implemented |
| Domain vocabulary prompt | Implemented |
| RAG ingestion of transcripts | Implemented |
| Multilingual Q&A | Implemented |
| WebSocket live transcription | Implemented |
| Silero VAD | Implemented |
| pyannote diarization | Integrated, requires HF_TOKEN |
| WER/CER/RTF evaluation module | Implemented |
| Full benchmark dataset | To be completed |
| Azure AI Speech deployment | Proposed |
| Azure AI Search migration | Proposed |
| Azure OpenAI migration | Proposed |
| Teams/Outlook/SharePoint integration | Proposed |
| User accessibility study | Future work |

---

## 15. Final Recommendation

The current PoC is a strong technical foundation for Topic 2. It demonstrates that corporate spoken content can be converted into accessible, searchable, and queryable text through a private STT and RAG pipeline.

For Nestle, the recommended next step is a controlled Azure pilot:

1. Keep the local faster-whisper pipeline for thesis evaluation and benchmarking.
2. Deploy a small Azure pilot using Azure AI Speech, Azure OpenAI, Azure AI Search, Blob Storage, Entra ID, and Key Vault.
3. Evaluate the system using WER, CER, RTF, latency, and user usefulness.
4. Validate security, cost, and governance requirements.
5. Integrate with Teams, Outlook, and SharePoint only after the pilot is validated.

This strategy provides a realistic path from academic proof of concept to enterprise-grade Microsoft deployment.

