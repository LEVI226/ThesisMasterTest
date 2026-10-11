# AI_METHODOLOGY.md

Topic 2 — Advanced Speech-to-Text for Noisy, Multilingual Corporate Meetings
Author: OUEDRAOGO Yannick Ulrich Levi (BIT / Nestlé research challenge)

This document reports, honestly and specifically, how AI assistance was used in this
work, what was verified and corrected by hand, and where the tools failed. Following the
challenge's instruction, it privileges **intellectual honesty over technical
exhaustiveness**. Every quantitative result in the thesis is traceable to a CSV under
`results/`; nothing is reported that could not be re-scored from the raw hypothesis/
reference text.

---

## 1. AI tools used

| Tool | Role in this work |
|---|---|
| **Claude (Anthropic), via Cowork / claude.ai** | Research assistant, first-draft prose, concept tutoring, and — most importantly — a verification loop (re-scoring CSVs, checking citations, catching fabrications). |
| **Antigravity (agentic IDE)** | Code scaffolding and **running the experiments** on the author's local GPU machine (NVIDIA RTX 4060, Windows, torch 2.6.0+cu124). |
| **Firecrawl** | Scraping public Nestlé web pages to assemble a brand-vocabulary lexicon (Nespresso, Maggi, Purina, …) for the domain-prompting condition. |
| **SerpAPI** | Programmatic web search during literature discovery. |
| **Google Scholar** | Locating candidate references. |
| **Third-party chatbots (general assistants)** | Consulted for ideas and code. **Several outputs were rejected** (see §4–§5); they were not merged into the thesis. |

The division of labour was deliberate: the author designed the study, made the scoping
judgments, ran every experiment on their own hardware, and decided what counted as
evidence. The AI accelerated literature search, code scaffolding, drafting and
cross-checking. This heavy, disclosed use of AI for drafting is stated openly, as the
challenge requires and rewards.

---

## 2. Significant AI-assisted decisions (sequence)

1. **Scope discipline.** Repeated AI proposals to expand into OCR (Topic 1), a
   personalization UI (Topic 3) and a full Microsoft 365 / Azure deployment were
   declined by hand. The thesis stays bounded to Topic 2 (STT), which is what makes it
   defensible.
2. **Dataset pivot, documented not hidden.** The publicly recommended corpora
   (Common Voice, LibriSpeech, FLEURS, VoxPopuli) proved impractical in the sandboxed
   environment; **PolyAI/MInDS-14 (CC-BY-4.0)** was adopted instead, and the substitution
   is reported as a first-class limitation.
3. **Pre-registration.** Hypotheses H1–H4 and the five experimental conditions were
   fixed in writing *before* any evaluation run, so results are judged against a fixed
   target rather than reverse-engineered.
4. **Chained-conditions design** (A→B→D→E, plus F for model size), so each observed
   change is attributable to a single named intervention.
5. **Backend-constant comparison discipline.** INT8-CPU and float16-GPU are never mixed
   inside a single comparison (see §4).
6. **Experiments executed via Antigravity** on the GPU box: the size ladder
   (tiny→large-v3), the VAD condition (C), the paired LoRA study, the wav2vec 2.0 (MMS)
   benchmark, and the Conformer (NeMo) benchmark.
7. **Verification-before-writing.** No number entered the thesis until it was checked
   against the corresponding `results/` CSV.

---

## 3. Manual verifications performed on AI output

### Citations verified one by one
- The three references added late — **Marsja, Signoret & Stenbäck (2025)**
  `10.1177/10519815251398498`, **Gygi & Hall (2016)** `10.3109/14992027.2015.1072773`,
  **Graetzer & Hopkins (2021)** `10.1121/10.0003557` — were each confirmed to **exist and
  match their claim** via the CrossRef API before being cited.
- **Honest scoping of a citation:** Graetzer & Hopkins study SNRs of −26 to 0 dB, below
  this work's 8 dB. It is therefore cited **only** for the general statement that "white
  Gaussian noise at a controlled SNR is a standard, reproducible degradation" — not to
  imply the SNR matched.
- A full audit of the 41-reference bibliography found and fixed **six genuine errors**
  (e.g., a dead DOI replaced by the arXiv URL for WhisperX; author-list, page-number and
  DOI corrections on several others).

### Re-scoring of measured results
- The Conformer results CSV was **re-scored with an independent Levenshtein
  implementation**: mean WER 0.266 recomputed vs 0.263 stored (≤0.4 % on the mean, ≤9 %
  on any single row — normalization edge cases), 0 errors, 0 empty hypotheses. This
  confirms the stored scorer column has no bug.
- Every headline number (noise doubling 47.0→96.4 %, the monotone ladder 63.4→24.6 %,
  the 42 % French auto-detection failure, etc.) was cross-checked against its CSV.

### Contamination control (LoRA study)
- The 300-clip training split was checked so that **no training transcript overlaps the
  evaluation set** (exclusions: en=8, fr=12, de=8; fixed seed 42; a final assertion
  guards the invariant).

### Confound identification
- MMS and Conformer receive the language **by construction** (one adapter/checkpoint per
  language), which is architecturally equivalent to forced language identification. The
  thesis therefore does **not** claim encoder superiority over Whisper-auto from these
  numbers; it compares like-for-like (Conformer vs MMS, both CTC and language-given).

---

## 4. Corrections made to AI output (what was wrong, and why it was fixed)

### Fabricated results and code — **rejected, never used**
- A general chatbot produced a **fabricated results table** (e.g., WER 11.2 %) built on a
  **fictional dataset** ("NestléCorp-Audio, 50 h"). Refused: no such data exists.
- Several "production-ready" scripts from chatbots were **simulated stubs** — functions
  returning hard-coded strings, `time.sleep()`, and invented confidence numbers
  (e.g., "94.2 % confidence"). Identified as non-measurements and excluded.
- Marketing "targets" (WER < 5 %, CER < 1.5 %) were treated as aspirations, **not
  results**, and kept out of the report.
- A **stray parallel pipeline** (8 clips, 10 dB SNR, MLS→FLEURS→Common Voice) was
  recognised as inconsistent with the canonical MInDS-14 / 8 dB / 36-clip set and
  **excluded** to protect comparability. (It was a throwaway test prompt.)

### Wrong "citation fixes" — **refused after checking the primary source**
- An external agent tried to (a) swap Punjabi et al. (2021) for a different paper and
  (b) change Astudillo's co-author to "Kolossa" with a shortened title. Both were
  **refused**; the author's IEEE Xplore lookups confirmed the refusals: the real Punjabi
  paper is *"Joint ASR and Language Identification Using RNN-T"* and the real Astudillo
  co-author is **Orglmeister**.
- A factual slip in the draft was corrected: the text had claimed Punjabi et al. support
  *within-utterance* code-switching, whereas the paper addresses *between-interaction*
  switching. The sentence was rewritten to be accurate.

### LaTeX damage from a "humanizer/citation" tool — **caught and reverted**
An automated tool that claimed to lower an AI-detection score instead corrupted the
source. Caught and reverted:
- broke TikZ (`shapes. geometric`), broke a command (`\ texttt`), dropped closing braces
  on two `\textbf{...}`, and inserted citations **mid-word** ("wit(Bain…)h",
  "ad(…)apting");
- introduced terminology errors: "initial prompt" → "starting prompt", "large language
  model" → "big language model", "Whisper." → "Whisper.ai". All reverted to the clean
  version.

### Code bugs (Antigravity) — found and fixed during runs
- a misplaced `import torch`;
- **torchcodec** DLL failures on Windows → worked around by loading audio with
  librosa/soundfile and `decode=False`;
- **NeMo** missing the `hydra` dependency → installed;
- **NeMo 3.x** `transcribe()` returns `Hypothesis` objects, not strings → extract
  `.text`.

---

## 5. Limitations encountered with the tools

- **Hallucinated references and confidently-wrong "corrections"** (see §4) — the single
  biggest risk; every AI-suggested citation had to be checked against CrossRef / IEEE.
- **Confidently-wrong benchmark numbers** from general chatbots (fabricated tables).
- **Plausible-but-fake code** (simulated stubs presented as working pipelines).
- **Scope inflation** — assistants repeatedly pushed toward OCR + Azure + a full
  platform; kept in scope by hand.
- **Formatting damage** from an automated humanizer/citation tool (LaTeX breakage).
- **Non-determinism across backends** — greedy decoding is not bit-identical between
  INT8-CPU and float16-GPU; ~52 of 180 transcriptions differ slightly. Canonical numbers
  are pinned to a fixed (hardware, compute-type) pairing and reported as such.
- **Process / security lesson:** API keys (Firecrawl, SerpAPI, and others) were at times
  pasted in plaintext during the work. They should be **revoked and rotated**; secrets
  must not travel through chat. No key value is reproduced in this document.

---

## 6. Summary statement

AI was used extensively — for literature discovery, code scaffolding, first-draft prose,
and continuous cross-checking — and its use is disclosed here in full. The scientific
substance, however, is the author's: the study was designed and pre-registered by the
author, every experiment was run on the author's own GPU, and **every reported number is
reproducible from the CSVs in `results/` using the self-contained scorer in
`backend/evaluation/metrics.py`.** Where the tools produced fabricated data, wrong
citations, broken code, or scope creep, those outputs were identified and corrected
rather than propagated.
