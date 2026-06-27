# Topic 2 - Speech-to-Text Engine
## Enterprise Deployment, Microsoft Architecture, and Cost Estimate

**Project:** AI-Driven Multimodal Accessibility Platform for Inclusive Workplace Communication  
**Topic:** Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings  
**Student:** Ulric GOUET-ZONGO  
**Target organization:** Nestle / BIT  
**Date:** 7 May 2026  
**Status:** Proof of Concept completed; enterprise deployment plan proposed

---

## 1. Executive Summary

This document describes how the current local Speech-to-Text (STT) proof of concept can be transformed into a secure enterprise-grade Microsoft Azure solution for Nestle.

The current PoC demonstrates that corporate audio and video content can be transcribed locally using faster-whisper, enriched with timestamps, indexed into a private RAG knowledge base, and queried through a multilingual Q&A interface.

For enterprise deployment, the recommended target architecture uses Microsoft Azure services, especially:

- Azure AI Speech for production-grade speech-to-text;
- Azure OpenAI Service for summarization, Q&A, and accessibility assistance;
- Azure AI Search for vector search and RAG retrieval;
- Azure Blob Storage for audio, transcript, and document storage;
- Microsoft Entra ID for authentication and access control;
- Azure Key Vault for secrets and encryption keys;
- Azure App Service, Azure Container Apps, or Azure Kubernetes Service for hosting;
- Microsoft Graph API for future Teams, Outlook, and SharePoint integration.

The deployment should be done progressively: local PoC, Azure pilot, controlled enterprise pilot, then production rollout.

---

## 2. Current PoC Status

The current implementation already includes:

| Component | Current Implementation |
|---|---|
| STT engine | faster-whisper |
| Noise reduction | noisereduce + librosa |
| Timestamped segments | Implemented |
| Speaker diarization | pyannote, requires HF_TOKEN |
| Real-time transcription | WebSocket + browser microphone |
| Vector database | ChromaDB |
| RAG assistant | Local Llama 3.2 through Ollama |
| API | FastAPI |
| Frontend | HTML/CSS/JavaScript |
| Evaluation framework | WER, CER, RTF |

The PoC is useful for research validation and local experimentation. However, enterprise deployment requires stronger security, identity management, scalability, monitoring, and integration with Microsoft 365 tools.

---

## 3. Recommended Microsoft Architecture

### 3.1 Production Architecture

```text
Microsoft Teams / Outlook / SharePoint
        |
        | Microsoft Graph API
        v
Azure API Management
        |
        v
FastAPI STT/RAG backend
        |
        |------------------------|
        |                        |
        v                        v
Azure AI Speech          Azure Blob Storage
Speech-to-Text           Audio, transcripts, documents
        |
        v
Transcript post-processing
Noise handling, timestamps, speaker labels
        |
        v
Azure AI Search
Vector index + hybrid search
        |
        v
Azure OpenAI Service
Q&A, summarization, accessibility assistant
        |
        v
Accessible UI / Teams App / Web Portal
```

### 3.2 Microsoft Services to Use

| Need | Recommended Microsoft Service | Purpose |
|---|---|---|
| Speech-to-text | Azure AI Speech | Batch and real-time transcription |
| Meeting intelligence | Azure AI Speech + speaker diarization | Speaker-attributed transcripts |
| RAG search | Azure AI Search | Vector, keyword, and hybrid retrieval |
| LLM reasoning | Azure OpenAI Service | Q&A, summarization, transcript explanation |
| File storage | Azure Blob Storage | Audio/video files, transcripts, metadata |
| Authentication | Microsoft Entra ID | Secure employee login and role-based access |
| Secret management | Azure Key Vault | API keys, tokens, certificates |
| Backend hosting | Azure App Service or Azure Container Apps | Host the FastAPI application |
| Enterprise APIs | Azure API Management | Secure and monitor API access |
| Monitoring | Azure Monitor + Application Insights | Logs, traces, latency, failures |
| Governance | Microsoft Purview | Data governance, retention, compliance |
| Microsoft 365 integration | Microsoft Graph API | Teams, Outlook, SharePoint integration |

---

## 4. Deployment Strategy

### Phase 1 - Local Research PoC

**Goal:** Validate the technical feasibility without cloud cost.

Current state:

- faster-whisper runs locally;
- ChromaDB stores embeddings locally;
- Ollama/Llama is used locally;
- uploaded audio and generated transcripts stay on the local machine.

This phase is suitable for:

- prototype validation;
- thesis experimentation;
- WER/CER/RTF benchmarking;
- early demonstrations.

### Phase 2 - Azure Pilot

**Goal:** Move the PoC to Azure while keeping the scope controlled.

Recommended services:

- Azure App Service or Azure Container Apps for the backend;
- Azure Blob Storage for audio/transcript storage;
- Azure AI Speech for transcription;
- Azure AI Search for vector indexing;
- Azure OpenAI Service for Q&A and summarization;
- Microsoft Entra ID for login;
- Azure Key Vault for secrets.

This phase should test:

- transcription accuracy;
- latency;
- cost per audio hour;
- data privacy;
- access control;
- integration with a small set of approved users.

### Phase 3 - Microsoft 365 Integration

**Goal:** Integrate the solution with Nestle collaboration tools.

Possible integrations:

- Teams meeting recordings;
- Teams live captions or post-meeting transcripts;
- Outlook attachments and meeting summaries;
- SharePoint document libraries;
- internal accessibility web portal.

Integration should be done through:

- Microsoft Graph API;
- Entra ID permissions;
- controlled enterprise app registration;
- role-based access policies.

### Phase 4 - Production Rollout

**Goal:** Deploy a reliable enterprise service.

Production requirements:

- private networking where required;
- secure storage and encryption;
- monitoring and cost alerts;
- backup and retention rules;
- audit logs;
- user access governance;
- documented support process;
- SLA expectations.

---

## 5. Cost Model

The final monthly cost depends mainly on:

- number of audio/video hours transcribed per month;
- real-time versus batch transcription;
- number of users;
- amount of indexed content;
- number of RAG queries;
- selected Azure region;
- whether GPU infrastructure is used;
- whether Azure AI Speech or self-hosted Whisper is selected.

The prices below are planning estimates and must be validated with the official Azure Pricing Calculator before procurement.

### 5.1 Cost Drivers

| Component | Billing Logic |
|---|---|
| Azure AI Speech | Usually billed by audio hours processed |
| Azure OpenAI | Billed by input/output tokens |
| Azure AI Search | Billed by provisioned search units per hour |
| Azure Blob Storage | Billed by stored GB, operations, and data transfer |
| App Service / Container Apps | Billed by compute size and runtime |
| API Management | Billed by tier and usage |
| Monitoring | Billed by logs/telemetry ingestion |
| GPU VM, if used | Billed by VM size and running hours |

### 5.2 Scenario A - Low-Cost Research Pilot

This scenario is suitable for thesis validation and internal demonstration.

| Component | Suggested Choice |
|---|---|
| STT | Local faster-whisper or limited Azure AI Speech |
| LLM | Local Ollama or low-volume Azure OpenAI |
| Search | ChromaDB or Azure AI Search Free/Basic |
| Hosting | Local machine or small Azure App Service |
| Storage | Azure Blob Storage small account |

**Estimated monthly range:** approximately 50 to 300 USD/month, depending on transcription volume and whether Azure OpenAI is used.

Best for:

- student research;
- small demo;
- low number of files;
- no production SLA.

### 5.3 Scenario B - Azure Pilot for Nestle Team

This scenario is suitable for a small business pilot with controlled users.

| Component | Suggested Choice |
|---|---|
| STT | Azure AI Speech |
| LLM | Azure OpenAI, GPT-4o mini or equivalent |
| Search | Azure AI Search Basic or S1 |
| Backend | Azure App Service or Azure Container Apps |
| Storage | Azure Blob Storage |
| Security | Entra ID + Key Vault |
| Monitoring | Application Insights |

**Estimated monthly range:** approximately 300 to 1,500 USD/month.

Best for:

- 10 to 50 pilot users;
- limited meeting transcription;
- internal feedback;
- realistic Azure security model.

### 5.4 Scenario C - Enterprise Production

This scenario is suitable for wider deployment across teams or departments.

| Component | Suggested Choice |
|---|---|
| STT | Azure AI Speech at scale, or self-hosted Whisper on GPU for high volume |
| LLM | Azure OpenAI with monitored token budgets |
| Search | Azure AI Search S1/S2 or higher |
| Backend | Azure Container Apps or AKS |
| Storage | Blob Storage with lifecycle policies |
| Security | Entra ID, Key Vault, private endpoints if required |
| Monitoring | Azure Monitor, Application Insights, cost alerts |
| Governance | Microsoft Purview |

**Estimated monthly range:** approximately 1,500 to 5,000+ USD/month.

Best for:

- higher audio volume;
- multiple departments;
- production security requirements;
- Microsoft 365 integration;
- operational monitoring and support.

---

## 6. Azure AI Speech vs Self-Hosted Whisper

Two deployment options are possible for speech-to-text.

### Option 1 - Azure AI Speech

Advantages:

- managed Microsoft service;
- easier production deployment;
- real-time and batch transcription support;
- enterprise support;
- easier integration with Microsoft ecosystem;
- no GPU management.

Limitations:

- cost grows with audio hours;
- less control over model internals;
- customization options depend on Azure Speech capabilities.

Recommended for:

- Nestle pilot;
- production deployment;
- enterprise governance.

### Option 2 - Self-Hosted Whisper on Azure GPU

Advantages:

- more control over model choice and preprocessing;
- potentially cost-effective for very high audio volume;
- useful for research experiments;
- can test faster-whisper, Whisper variants, and custom pipelines.

Limitations:

- requires GPU VM management;
- requires scaling, monitoring, patching, and deployment work;
- may require more engineering effort;
- real-time performance depends on VM size and workload.

Recommended for:

- research benchmarking;
- high-volume transcription if cost analysis supports it;
- experiments with domain adaptation and custom preprocessing.

### Recommended Decision

For Nestle-facing deployment, the safer recommendation is:

```text
Use Azure AI Speech for the enterprise pilot and production path.
Keep faster-whisper as the research baseline and fallback experimental engine.
```

This keeps the project aligned with Microsoft enterprise tools while preserving the academic research value of the local PoC.

---

## 7. Security and Compliance Considerations

Because the platform handles corporate meetings, speech content, and possibly sensitive documents, the deployment must include:

- Microsoft Entra ID authentication;
- role-based access control;
- encryption at rest and in transit;
- Azure Key Vault for secrets;
- restricted storage access;
- audit logging;
- data retention policy;
- optional private endpoints;
- no hardcoded API keys;
- no unmanaged sharing of meeting audio;
- clear separation between test data and production data.

For production, the platform should also define:

- who can upload audio;
- who can view transcripts;
- who can query the RAG knowledge base;
- how long transcripts are retained;
- whether meeting participants must consent to transcription;
- whether transcripts are stored permanently or deleted after processing.

---

## 8. Recommended Pilot Plan

### Pilot Scope

- 5 to 10 approved audio/video files;
- 2 to 3 languages, for example English, French, and German;
- clean and noisy meeting conditions;
- 5 to 10 internal testers;
- limited retention period;
- no confidential production data at first.

### Pilot Success Metrics

| Metric | Target |
|---|---|
| WER on clean speech | Below 10-15% |
| WER on noisy speech | Measured and improved through preprocessing |
| RTF | Below 1.0 for faster-than-real-time processing |
| User usefulness | Positive feedback from accessibility/user testers |
| Security | Entra ID access and no public data exposure |
| Cost | Monthly cost within approved pilot budget |

---

## 9. Final Recommendation

The current local PoC should be presented as the research and technical validation layer. For Nestle-facing deployment, the recommended Microsoft path is:

1. Keep the current faster-whisper pipeline for research benchmarking.
2. Deploy a controlled Azure pilot using Azure AI Speech, Azure AI Search, Azure OpenAI, Blob Storage, Entra ID, and Key Vault.
3. Integrate with Microsoft Teams, Outlook, and SharePoint through Microsoft Graph API after the pilot is validated.
4. Use Azure Monitor and Cost Management to track performance and spending.
5. Decide later whether production STT should remain on Azure AI Speech or move to self-hosted Whisper on GPU based on monthly audio volume and cost analysis.

This approach provides a realistic bridge between the thesis PoC and an enterprise-grade Microsoft solution for Nestle.

