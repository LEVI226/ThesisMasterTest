**EXECUTIVE & TECHNICAL EVALUATION: MULTIMODAL AI DOCUMENT**

**INTELLIGENCE**

---

**Topic:** Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings

**Student:** Ulric GOUET-ZONGO

**Framework:** Private-RAG (Retrieval-Augmented Generation)

**Status:** Proof of Concept (PoC) Verified

---

**1. PROJECT SCOPE & OBJECTIVES**

The objective was to evaluate the feasibility of an automated Speech-to-Text (STT) system
capable of transcribing corporate audio and video content — including real speeches, meetings,
and multimedia files — with multilingual support and zero data leakage, in a fully local
environment. This directly addresses the optimization of STT for noisy, multilingual
corporate communications at Nestlé.

The system is designed to serve employees with hearing impairments by automatically
generating accurate, timestamped transcriptions of spoken content, which are then
integrated into a shared knowledge base queryable in natural language.

---

**2. TECHNICAL AUDIT OF THE DEMO (THE "STRESS TEST")**

To establish a baseline, the system was evaluated on a real-world corporate audio
document — a CEO speech — on constrained consumer hardware, to test both transcription
accuracy and pipeline efficiency in a low-resource environment.

---

**A. Hardware Constraints & Resource Allocation**

- **Host Machine:** Dell Latitude 3480 (Legacy Business Hardware)
- **Processor:** Intel® Core™ i5-7200U (7th Generation, 2 Cores, 4 Threads)
- **Memory:** 8GB DDR4 RAM
- **Storage:** Local SSD

**Observation:** The absence of a dedicated GPU forced the STT engine to operate in
full CPU mode with INT8 quantization (via faster-whisper/GGUF), representing the
most resource-constrained scenario for AI inference. Despite this, the system
delivered well below real-time latency.

---

**B. The Multimodal STT Pipeline**

**Stage 1: Audio Preprocessing & Noise Reduction**

- **Library:** noisereduce + librosa
- **Method:** Mono resampling at 16 kHz + spectral noise reduction (prop_decrease = 0.75)
- **Purpose:** Eliminates background meeting noise before transcription, improving
  accuracy on recordings made in corporate meeting environments.
- **Format support:** MP3, MP4, WAV, OGG, M4A, FLAC, WEBM, MKV, AVI

---

**Stage 2: Transcription & Language Understanding (faster-whisper)**

- **Model:** faster-whisper — `small` (INT8 quantized, CPU mode)
- **Test Document:** *"Philipp Navratil, Nestlé's CEO, addresses infant formula recall.mp3"*
  — a real Nestlé executive speech (2.1 MB)
- **Audio Duration:** 4 minutes 9 seconds
- **Processing Time:** **62 seconds** (Real-Time Factor: **0.25×** — 4× faster than
  real-time on CPU only)
- **Language Auto-Detection:** ✅ English (EN) correctly identified with zero
  manual configuration
- **Word Timestamps:** Enabled — 20 precise timestamped segments generated,
  from `00:00.0` to `04:09.4`
- **Domain Prompt:** The engine was initialized with a Nestlé-specific vocabulary
  prompt: *"Nestlé, Nespresso, Maggi, Purina, KitKat, Nescafé, supply chain,
  plant-based portfolio"* — enabling accurate transcription of brand names and
  technical terminology.
- **Output Volume:** 3,000 characters of structured transcript

**Critical Finding — Proper Noun Handling:**
The system transcribed the CEO name *"Philippe Navratil"* as *"Philippe Naruto"*,
exposing a known limitation of the `small` model on rare proper nouns. This directly
motivates fine-tuning on Nestlé-specific vocabulary (research question 2 of Topic 2)
and serves as a quantifiable benchmark for domain adaptation improvement.

---

**Stage 3: Speaker Diarization (Advanced Capability)**

- **Model:** pyannote/speaker-diarization-3.1
- **Function:** Assigns a `SPEAKER_XX` label to each timestamped segment, enabling
  distinction of multiple speakers in meeting recordings.
- **Status:** Integrated and functional when `HF_TOKEN` is configured; CPU fallback
  available when no GPU is detected.
- **Corporate Value:** Enables hearing-impaired employees to follow who said what
  during multilingual team meetings and video calls.

---

**Stage 4: Semantic Vectorization & Embedding**

- **Model:** `intfloat/multilingual-e5-small` (Sentence-Transformers)
- **Multilingual Native Support:** French, English, German (FR/EN/DE) without
  additional configuration.
- **Indexing:** Transcribed text is fragmented into 500-word semantic chunks
  with 50-word overlap and stored in **ChromaDB**.
- **Current Collection:** **90 semantic chunks** indexed from ingested audio content.
- **Vector Dimension:** 384-dimensional cosine similarity space.

---

**Stage 5: Cognitive Reasoning & Multilingual Q&A (Accessibility Layer)**

- **LLM:** Llama 3.2 (local, via Ollama)
- **Verification:** The system was tested on its ability to answer questions
  derived from the transcribed CEO speech.
- **Cognitive Accuracy:**
  - The system correctly identified the subject as a **product recall announcement**
    for infant formula.
  - It accurately retrieved that the quality concern originated at a **factory in the
    Netherlands** and involved a **specific raw material from a supplier**.
  - It correctly cited the source file (filename + document type: `stt`) in its answer.
- **Multilingual Response:** The engine responds in the same language as the question
  (FR/EN/DE automatic detection), or in a forced language via API parameter.
- **Critical Finding:** The system demonstrates accurate document-grounded reasoning
  from transcribed audio content. Latency is hardware-bound and will be resolved
  via GPU migration.

---

**3. SCALABILITY & CLOUD ARCHITECTURE (PROPOSED)**

| Component | Technical Specification | Estimated Cost |
|---|---|---|
| **Compute (GPU)** | Azure NC6s_v3 (NVIDIA Tesla V100) — instant STT inference with full float16 Whisper | $250 / mo |
| **STT Service** | Azure Cognitive Services Speech — real-time streaming transcription, 100+ languages | $100 / mo |
| **Security** | AES-256 Encryption + Azure Key Vault | $50 / mo |
| **Vector Store** | Azure AI Search (replaces ChromaDB) — enterprise-scale semantic retrieval | $150 / mo |
| **Integration** | API connection to Nestlé Teams / Outlook / SharePoint environment | $3,500 one-time |

**GPU Impact on Transcription:** Migrating from CPU (INT8) to NVIDIA V100 (float16)
is projected to reduce the current 62-second processing time for a 4-minute audio
to under **4 seconds**, enabling near-real-time transcription for live meetings.

---

**4. CONCLUSION**

This PoC successfully demonstrates that corporate spoken content is no longer a barrier
for hearing-impaired employees. On consumer-grade legacy hardware — with no GPU — the
system transcribed a **real Nestlé executive speech** (4 min 9 sec) in **62 seconds**,
auto-detected the language, generated **20 timestamped segments**, and ingested the
content into a searchable knowledge base in a single automated pipeline.

The identified limitation in proper noun recognition (e.g., *"Navratil" → "Naruto"*)
is a quantifiable research anchor for fine-tuning experiments using Nestlé-specific
vocabulary — directly addressing Research Question 2 of Topic 2.

By upgrading to the proposed Azure GPU infrastructure and integrating Azure Cognitive
Services Speech, we will transform this local PoC into a **real-time transcription engine**
capable of serving Nestlé Ghana's multilingual workforce — turning every meeting, call,
and announcement into a fully accessible, searchable, and inclusive communication asset.
