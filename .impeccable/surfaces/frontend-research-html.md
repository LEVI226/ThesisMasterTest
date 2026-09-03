---
version: 1
slug: "frontend-research-html"
primary_target: "frontend/research.html"
related_targets: []
---

Scope: `/research`, a standalone English-language evidence dashboard for Topic 2. Visitor mode: Operate.

Audience and job: the student researcher, supervisor, and thesis jury must determine what the experiments support, how each result was produced, and where the evidence is incomplete.

Primary task: move through RQ1 robustness, RQ2 adaptation, and RQ3 real-time feasibility; inspect a claim's metric, experiment, source file, and limitation without losing context.

Proof and content: canonical CSVs in `results/`, the reproducible clustered/paired bootstrap audit, live latency measurements, meeting diarization measurements, dataset scope, and explicit limitations. Missing evidence is labelled rather than inferred.

Chosen structure: RQ Evidence Spine. A sticky research-question rail accompanies repeated question, verdict, key comparison, confidence, provenance, and limitation sections. The memorable interaction is the Evidence Trail drawer: Claim -> Metric -> Experiment -> Source -> Limitation.

Constraints: inherit the existing dark Inter interface and blue-violet accent; English UI; WCAG-conscious keyboard and screen-reader behavior; charts require tabular equivalents; no production, clinical, or user-study claims; distinguish VAD-segmented inference from native streaming.

Unresolved: formal Nestlé brand permission; representative corporate meeting corpus; approved end-user study; validated persistent speaker identity.
