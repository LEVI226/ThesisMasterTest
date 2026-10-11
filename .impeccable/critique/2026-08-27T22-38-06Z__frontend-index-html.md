---
target: $impeccable critique frontend/index.html
total_score: 14
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 4
timestamp: 2026-08-27T22-38-06Z
slug: frontend-index-html
---
Method: dual-agent (A: critique_design_a · B: critique_evidence_b)

## Design Health Score

| # | Heuristic | Score | Key issue |
|---|---|---:|---|
| 1 | Visibility of System Status | 2/4 | Feedback exists, but progress is staged, errors are transient, and dynamic updates are not announced accessibly. |
| 2 | Match System / Real World | 1/4 | Users face WebSocket, RAG, chunks, VAD and diarization jargon; “real-time streaming” overstates the implementation. |
| 3 | User Control and Freedom | 2/4 | Stop, disconnect, copy and clear exist, but there is no cancel during inference, undo, recovery or persistence. |
| 4 | Consistency and Standards | 2/4 | Visual components are cohesive, but many controls use clickable div/span elements instead of native semantics. |
| 5 | Error Prevention | 1/4 | Little client-side validation, immediate destructive clearing, unconstrained endpoint input and no result recovery. |
| 6 | Recognition Rather Than Recall | 2/4 | Primary actions are visible, but the Q&A corpus, prior uploads and technical terms are not made explicit. |
| 7 | Flexibility and Efficiency | 1/4 | No shortcuts, caption preferences, session history, presets, batch processing or research export workflow. |
| 8 | Aesthetic and Minimalist Design | 2/4 | Calm and cohesive, but four equal products dilute Topic 2 and infrastructure controls occupy prime space. |
| 9 | Error Recovery | 1/4 | Errors are vague, transient and rarely explain how to recover without losing work. |
| 10 | Help and Documentation | 0/4 | No contextual help, terminology definitions, limitation disclosure, privacy explanation or research-method entry point. |
| **Total** |  | **14/40** | **Poor — major UX overhaul required** |

## Design Specificity Verdict

**LLM assessment.** Product specificity is low. The page is a polished generic dark AI toolbox that could support transcription, OCR or chat with minimal changes. For a hearing-impaired meeting participant, captions are subordinate to endpoint configuration and model terminology. For a thesis jury, the page omits experimental configuration, WER/CER, latency, uncertainty, dataset scope, limitations and reproducibility. Product-specificity currently lives mainly in labels such as “Topic 2,” “Whisper,” “VAD” and “diarization,” rather than in the interaction design.

The page also creates a trust mismatch: it appears to be an official Nestlé accessibility product, describes VAD-segmented batch inference as “real-time streaming,” and gives speaker labels visual authority even though persistent identity and diarization accuracy are not scientifically validated.

**Deterministic scan.** The detector emitted 9 warnings across 6 rules in `frontend/index.html`: three `side-tab` matches at lines 432–434, two duplicate Inter-font advisories at lines 10 and 32, a `bounce-easing` advisory at line 375, `transition: width` at line 218, a file-level em-dash advisory, and a `dark-glow` status treatment at line 86. It ran in degraded regex mode because its HTML parser modules were unavailable, so computed contrast and selector analysis were not performed and the result is an undercount.

The actionable deterministic finding is the width transition. Inter and the status glow reinforce the generic “dark AI dashboard” character. The toast side-border warnings, animation-name warning and em-dash warning are contextual advisories rather than meaningful UX defects.

**Visual overlays.** No reliable overlay is available. Both independent browser attempts returned “No browser is available,” and browser discovery returned an empty list. Mutable injection was therefore not attempted, no human-visible tab was presented, and the live-server helper was correctly not started.

## Overall Impression

The interface has a competent visual baseline and a clear file-upload flow, but its information architecture serves the implementation rather than the research participant or jury. The biggest opportunity is to split the experience into an access-first caption mode and an evidence-first research mode, while clearly labelling both as an academic prototype.

## What’s Working

- The file-transcription flow has a comprehensible local hierarchy: upload, language, action, progress, result, then optional timed segments.
- The restrained palette, consistent cards and centered measure create a calm foundation rather than visual chaos.
- Health, progress, disabled controls, connection state, typing indicator, segment count and empty states show awareness that operational tools need feedback.

## Priority Issues

### [P1] Product and scientific scope are misrepresented

**Why it matters:** The official-sounding identity and “real-time streaming” claim create more trust than the present evidence supports. This is risky in an accessibility and academic context.

**Fix:** Place “Academic research prototype — Topic 2” in the primary header; qualify the live implementation as VAD-segmented transcription; label diarization experimental; expose dataset and evaluation limitations close to the relevant results.

**Suggested command:** `$impeccable clarify frontend/index.html`

### [P1] Core interactions are not reliably keyboard or screen-reader operable

**Why it matters:** The product’s stated beneficiary includes accessibility-dependent users, yet tabs, upload areas, timed-segment toggle, Copy and Clear rely on non-semantic clickable elements. Dynamic transcription and status changes lack an ARIA live-region strategy.

**Fix:** Replace interaction divs/spans with buttons, labels and proper tab semantics; add keyboard behavior, visible `:focus-visible`, meaningful form labels, status/live regions, reduced-motion handling and WCAG contrast verification.

**Suggested command:** `$impeccable audit frontend/index.html`

### [P1] Live captions are designed around infrastructure rather than hearing access

**Why it matters:** A participant must manage a raw WebSocket address and connection lifecycle before receiving small captions. Language, caption size, contrast, density, uncertainty and safe speaker presentation are absent.

**Fix:** Move endpoint controls into advanced/debug settings; provide a single participant-facing Start Captions action, session language, readable caption sizing, uncertainty/failure state, latency state and non-authoritative speaker labels.

**Suggested command:** `$impeccable distill frontend/index.html`

### [P1] Scientific and jury-facing information architecture is absent

**Why it matters:** The application does not demonstrate the thesis contribution. OCR and Q&A receive equal status while WER/CER, paired comparisons, latency, confidence intervals, dataset caveats and research-question coverage are missing.

**Fix:** Create an explicit Research Evidence surface linked to RQ1–RQ3, backed by canonical CSVs, with model/condition comparisons, paired uncertainty, latency decomposition and limitations. Keep OCR/RAG secondary because they belong to Topics 1 and 3.

**Suggested command:** `$impeccable shape research-dashboard`

### [P2] Error prevention and recovery are fragile

**Why it matters:** Long transcription, microphone denial and WebSocket failure can leave users uncertain about whether content is safe, still processing or lost.

**Fix:** Add truthful progress, cancel/retry, inline recovery guidance, validation before upload, clear confirmation/undo, preserved transcript state and explicit offline/degraded modes.

**Suggested command:** `$impeccable harden frontend/index.html`

## Persona Red Flags

### Sam — keyboard and screen-reader dependent

- Core navigation and upload rely on non-native click targets without dependable keyboard semantics.
- Language and connection fields lack complete accessible labelling.
- Incoming captions, progress, errors and success states are not announced through appropriate live regions.
- Focus visibility is incomplete and motion has no reduced-motion alternative.
- Small muted text is close to or below WCAG AA contrast, but the degraded detector could not compute contrast reliably.

### Jordan — first-time user

- Four equal modes require an unexplained choice between STT, OCR, Q&A and Live STT.
- Topic numbers, OCR, RAG, chunks, WebSocket, Silero VAD and diarization are not defined.
- The raw endpoint and disabled controls do not clearly explain the next action.
- No help, privacy explanation, limitations or post-transcription guidance is available.

### Alex — research power user

- No experiment presets, saved sessions, batch input, shortcuts or research exports.
- Long transcription has no cancellation or meaningful ETA.
- Results cannot be traced from an interactive run to a reproducible experimental configuration.

### Hearing-impaired meeting participant

- Connection infrastructure becomes a prerequisite to access.
- Captions cannot be resized or adapted, and the default transcript size is small.
- Silence can mean no speech, missed speech, VAD delay or connection failure, but the interface does not distinguish them.
- Speaker labels appear definitive despite unvalidated persistent identity.
- There is no participant-facing recording/privacy notice or clear local-processing reassurance.

## Minor Observations

- The wheelchair symbol is an imprecise umbrella for a hearing-access use case.
- Inter, blue-purple accents, glow and repeated emoji reinforce a category-generic AI dashboard identity.
- Google Fonts adds an external dependency to an otherwise local/private prototype.
- “Ingested to RAG” discloses secondary data use only after processing and uses implementation language.
- Mobile behavior changes mainly outer padding; tab overflow, dense live controls, touch targets and caption reading are not meaningfully adapted.
- Source excerpts exposed only through hover titles are inaccessible to touch and keyboard users.
- The progress bar uses a width transition; a transform-based fill would avoid layout work.

## Questions to Consider

- Should the first screen serve the meeting participant, the thesis jury, or offer two explicit entry modes?
- What is the strongest honest claim today: “accessible platform” or “academic prototype exploring caption accessibility under noisy multilingual conditions”?
- Which evidence should create jury trust first: paired WER/CER, latency, reproducibility, or disclosed limitations?
- Should speaker labels remain generic and explicitly uncertain until persistent diarization is validated?
