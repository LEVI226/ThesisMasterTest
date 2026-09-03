# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary beneficiary is an employee with hearing impairment who needs readable captions during multilingual workplace meetings and video calls. This is inferred from the official Topic 2 proposal and remains to be confirmed through user evaluation.

The secondary audience is the student researcher, academic supervisor, and thesis jury. They need to inspect experimental configurations, measured results, limitations, and the relationship between the prototype and the three Topic 2 research questions.

## Product Purpose

This is an academic research prototype for Topic 2, "Advanced Speech-to-Text Models for Noisy, Multilingual Meetings." It demonstrates and evaluates speech-to-text approaches for noisy, multilingual, and multi-speaker workplace communication.

Success means that the prototype can reproduce the thesis experiments, expose accuracy and latency trade-offs honestly, and demonstrate accessible live or file-based captions. It is not intended to establish production readiness.

## Positioning

The prototype connects an accessible transcription demonstration with the evidence needed to evaluate it scientifically: model and decoding configuration, language and acoustic condition, WER/CER, throughput, latency, uncertainty, and disclosed limitations.

## Operating Context

- Local web application served by FastAPI.
- File-based transcription for audio and video.
- VAD-segmented WebSocket transcription for a simulated live-meeting workflow.
- English, French, and German speech, with automatic or forced language selection.
- Offline experimental results stored in canonical CSV files and interpreted in the Topic 2 thesis.
- Demonstrations may simulate a Teams-style meeting, but the current application is not integrated into Microsoft Teams.

## Capabilities and Constraints

- Whisper/faster-whisper is the primary interactive STT engine.
- Whisper model sizes, MMS/wav2vec 2.0, and Conformer have been evaluated offline with a common scorer.
- Noise reduction, VAD, contextual prompting, LoRA, and diarization are experimental conditions rather than universally beneficial product features.
- Live transcription is VAD-segmented batch inference, not native frame-synchronous streaming.
- Diarization integration exists, but persistent speaker identity and diarization accuracy are not yet validated on a representative meeting corpus.
- The current MInDS-14 evaluation set contains telephone banking speech and synthetic-noise derivatives; it is not a corporate meeting benchmark.
- OCR and RAG belong to the shared multimodal platform but are not the scientific priority of Topic 2.
- The prototype must not imply clinical validation, production deployment, or demonstrated accessibility outcomes without supporting evidence.

## Brand Commitments

The existing working name is "Nestlé Accessibility Platform" in the context of a BIT/Nestlé Master Thesis. Every public-facing surface must identify it as an academic prototype, not an official production product.

Open decision: confirm the formal permission and exact rules for using Nestlé's name, logo, and corporate identity in public demonstrations and thesis artifacts.

## Evidence on Hand

- Official research brief: `C:/Users/ulric/Downloads/Research Proposal.pdf`.
- Revised thesis source: `Memoire_LaTeX/main_revised.tex`.
- Reproducible statistical audit: `results/statistical_audit_revised.md`.
- Canonical per-file experimental CSVs under `results/`.
- Evaluation audio, references, and metadata under `datasets/stt_eval/`.
- Working file-transcription and live WebSocket demonstrations under `frontend/` and `backend/`.
- No completed end-user study with hearing-impaired participants is currently available and none may be fabricated.

## Product Principles

1. Scientific evidence before demonstration spectacle.
2. Make uncertainty, failure modes, and experimental scope visible.
3. Keep model comparisons reproducible and methodologically comparable.
4. Design captions around access to meeting content, not around generic AI novelty.
5. Preserve local processing and data minimisation unless a deployment decision explicitly changes the architecture.

## Accessibility & Inclusion

The interface should support readable live captions, keyboard operation, semantic structure, adjustable text presentation, sufficient contrast, reduced motion, clear focus states, and non-colour-only status communication. Speaker labels and confidence indicators must not imply greater accuracy than the underlying measurements support.

Accessibility conformance and end-user usability remain evaluation targets, not established outcomes. A future study with hearing-impaired participants requires an approved protocol, consent, and appropriate privacy safeguards.
