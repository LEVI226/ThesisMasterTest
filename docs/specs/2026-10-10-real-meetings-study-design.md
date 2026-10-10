# Design: Real-Meetings Validation Study + Learning Track + Defense Preparation

- **Date:** 2026-10-10
- **Branch:** `study/real-meetings` (baseline frozen at tag `defense-baseline`, commit `9054422`)
- **Author:** OUEDRAOGO Yannick Ulrich Levi, with Claude Code (AI assistance is logged in `PROMPTS_JOURNAL.md` and `AI_METHODOLOGY.md`)
- **Status:** awaiting author review

---

## 1. Why this study exists

The thesis answers the BIT/Nestlé proposal's Topic 2 ("Advanced Speech-to-Text Models for Noisy,
Multilingual Meetings"). Its canonical campaign (468 runs, audited 10/09 and 16/09) has four
validity gaps that a jury is likely to raise:

| # | Gap | Where it comes from |
|---|-----|---------------------|
| G1 | **Domain mismatch.** The topic is *meetings*, but the canonical data (MInDS-14) is single-speaker telephone banking at 8 kHz. | `ETAT_ACTUEL.md` §2 |
| G2 | **Unrealistic noise.** Only synthetic white noise at one SNR (8 dB). | `ETAT_ACTUEL.md` §2 |
| G3 | **Low statistical power.** n = 36 clips, so effects of about 1 point (prompting, LoRA) can't be established. | `ETAT_ACTUEL.md` §3.4 |
| G4 | **Latency not properly measured.** Session parameters weren't logged, and the 11 s maximum is unexplained. | `ETAT_ACTUEL.md` §3.3 |

This study **adds** evidence on real, public meeting and corporate audio. It **does not replace**
the canonical campaign: MInDS-14 remains the thesis's controlled benchmark, and this study is
declared as a separate, labelled *external validation* dataset (to be recorded in `ETAT_ACTUEL.md`
so it is not mistaken for a "stray pipeline").

## 2. Scope and timeline (defense in about 1 month)

| Week | Study | Learning track |
|------|-------|----------------|
| 1 | Supervisor message (day 1); freeze `PROTOCOL.md`; build data manifests; spot-check AGM captions | Notes 01–04 |
| 2 | Run all experiments | Notes 05–08 |
| 3 | Analysis; write `real_meetings.tex`; send to supervisor | Note 09 |
| 4 | Defense preparation (§8) | Note 10 + mock defenses |

**Stop rule:** at the end of week 2, whatever has been run is analysed and written up as a
*preliminary* validation; everything not run becomes "future work". Week 4 is reserved for the
defense, whatever happens.

**Out of scope until after the defense:** new fine-tuning or LoRA training, new model families,
a full redesign, the paper submission.

**Dependency:** the supervisor agrees to the added section. If they refuse, the study continues as
the first step of the post-defense paper; the learning track and defense preparation are unaffected.

## 3. Data

All sources are public, licensed or official. **The author's private meeting recordings
(`audioReunionréel/`: DHIS2, Avenue de l'Indépendance, July 2026 recordings) are excluded:**
participants did not consent to research use. They stay local, are never committed (see
`.gitignore`), and are never quoted.

| ID | Source | Language | Speech type | Reference (ground truth) | Planned amount |
|----|--------|----------|-------------|-------------------------|----------------|
| AGM | Nestlé Chair & CEO, AGM 2026 (YouTube, 3 language versions, 22 min 13 s each) | DE, EN, FR | Prepared corporate speech, studio-clean; DE/FR are probably interpreted or dubbed | Captions uploaded by Nestlé (the track named "English" in DownSub, whose content is in each video's own language; *not* the auto-generated track) | 3 × 22 min → ~90 segments per language |
| AMI | AMI Meeting Corpus, official test split | EN (many non-native speakers) | Spontaneous multi-speaker meetings; close-talk (IHM) and far-field (SDM) microphones | Human gold transcripts + speaker labels | ~1 h |
| SUMM-RE | SUMM-RE (Linagora; HF `linagora/SUMM-RE`, gold transcripts in `datasets-CNRS/summ-re-asru`), CC BY-SA 4.0 | FR | Spontaneous multi-speaker meetings | Human gold transcripts (manually corrected, aligned) | ~1 h |
| SEN *(optional)* | Senate commission of inquiry hearing of Nestlé executives (2025) | FR | Public institutional Q&A | Official Senate record, if it can be found (lightly edited, so secondary) | ≤ 30 min |
| INV *(optional)* | Nestlé HY2025 investor & analyst call | EN | Corporate Q&A, accented | Official transcript PDF (edited, so secondary) | ≤ 30 min |

**Segmentation:** consecutive caption or transcript units are merged into segments of about
10–20 s, cut only at unit boundaries, so every segment has an exact reference.

**Dev / test split:** the first 3 minutes of each source (AGM per language, AMI per meeting,
SUMM-RE per meeting) form the **dev** set. Dev is the *only* audio used to choose settings (for
example chunk length for RQ3). Everything else is **test** and is never used for tuning.

**Reference quality checks** (reported in the thesis):
- **AGM FR + EN:** the author listens to 20 randomly drawn segments per language (seed fixed in
  `PROTOCOL.md`) and records verbatim / minor difference / major difference. Takes about 30 min.
- **AGM DE:** no German annotator is available. Automatic checks only (cue timing coverage, words
  per second against EN/FR). Labelled "publisher captions, partially verified", the same honest
  treatment as MInDS-14 German.
- **AMI, SUMM-RE:** published gold transcripts, cited as such.

**Noise (gap G2):** real noise, not white noise. Babble and office/ambient noise from a public,
licensed noise corpus (MUSAN; DEMAND as a fallback) is mixed into **AGM** at SNR = 20, 10 and 5 dB.
The noise segment and SNR are drawn with a fixed seed, and the mixing script is committed. AMI SDM
supplies *natural* far-field noise and reverberation.

## 4. Systems

All systems already have evaluation code in `backend/training/`:

| System | Family | Code |
|--------|--------|------|
| Whisper small | Encoder-decoder transformer | faster-whisper, fp16 on RTX 4060 |
| Whisper large-v3 | Encoder-decoder transformer | faster-whisper, fp16 |
| MMS-1B (wav2vec 2.0) | Self-supervised encoder + CTC | `eval_wav2vec.py` |
| Conformer CTC large (NeMo; en/fr/de checkpoints) | Conformer + CTC | `eval_conformer.py` |
| *(optional)* YouTube auto-captions | Commercial ASR (external reference) | AGM only, downloaded tracks |

Decoding is deterministic: beam 5, temperature 0. Whisper's temperature fallback is either disabled
or logged; the choice is recorded in `PROTOCOL.md`.

## 5. Hypotheses and conditions (pre-registered)

| ID | RQ | Hypothesis | Conditions | Data |
|----|----|------------|------------|------|
| H1 | RQ1 | On the *same* speech, WER differs by language; Whisper large-v3 has the lowest WER in each language. | 4 systems × 3 languages, clean | AGM |
| H2 | RQ1 | WER increases as SNR decreases, and far-field is worse than close-talk. | clean / 20 / 10 / 5 dB; IHM vs SDM | AGM, AMI |
| H3 | RQ1 | Spontaneous meeting speech has higher WER than prepared speech, in the same language. | AMI vs AGM-EN; SUMM-RE vs AGM-FR | all |
| H4a | RQ2 | Forcing the language lowers WER versus automatic language detection on long or noisy audio. | Whisper: forced vs auto | AGM (noisy), AMI SDM, SUMM-RE |
| H4b | RQ2 | A Nestlé vocabulary prompt raises Nestlé-term recall but also the hallucination rate. | Whisper large-v3: prompt vs none | AGM |
| H4c | RQ2 | Denoising (spectral gating, chunked) helps only at low SNR. | denoise on/off × SNR | AGM noisy |
| H4d | RQ2 | The existing LoRA adapter (`whisper-small`, trained on MInDS-14) does not transfer to meetings. | small vs small+LoRA | AMI, SUMM-RE |
| H5 | RQ3 | Beyond some chunk length, WER plateaus while latency keeps rising. There is a recommended operating point. | chunk length (choices fixed on dev) × model size, streaming replay | AGM, AMI |
| D1 | RQ1 (diarization) | pyannote achieves a DER on real meetings that we report with a confidence interval (descriptive). | pyannote 4 | AMI (true speaker labels) |

**Primary comparisons** (the only ones tested for significance, with Holm correction across them):
H1 (Whisper large-v3 vs Conformer CTC, per language; Conformer was the closest competitor in the
canonical campaign, 26.3 % vs 24.6 %, so the pair is fixed in advance, not chosen after seeing results), H2 (clean vs 10 dB, large-v3), H3 (meeting vs
prepared, large-v3), H4a, H4d. **Everything else is labelled exploratory.**

## 6. Metrics and statistics

- **Primary metric:** WER. **Secondary metrics:** CER, Nestlé-term recall (a fixed term list in
  `PROTOCOL.md`), hallucination rate (insertions in silent or non-speech regions, plus repeated
  n-grams of 4 or more tokens), DER (AMI), RTF, latency p50/p95 (streaming replay).
- **Scorer:** the canonical `backend/evaluation/metrics.py` (same normalisation as the thesis),
  plus **one** documented extra rule for numbers (digits ↔ words), applied identically to every
  system. Results are reported both with and without this rule.
- **Unit of analysis:** the segment. Corpus-level WER = total errors / total reference words.
- **Uncertainty:** 95 % confidence intervals by *clustered* bootstrap (cluster = meeting or speech
  file), because segments from the same meeting are not independent. Uses the existing
  `backend/evaluation/statistics.py` (`clustered_paired_bootstrap_difference`, `latency_summary`).
- **Comparisons:** paired (same segments, different system or condition). Holm correction across
  the primary comparisons. Effect sizes are reported in WER points, not only p-values.

## 7. Reproducibility and traceability

- **One CSV row per (segment × system × condition):** ids, reference, hypothesis, S/D/I/N, timings,
  model, precision, every option, package versions, GPU, git commit hash. Files go in
  `results/real_meetings/`.
- **Generated outputs:** thesis tables and figures are produced by scripts from the CSVs and never
  typed by hand.
- **`PROTOCOL.md` is frozen** (committed and dated) before the first test-set run. Any later
  deviation is logged in a "Deviations" section with its date and reason.
- **Living documentation** (no duplicates): `CHANGELOG.md`, `PROMPTS_JOURNAL.md`,
  `AI_METHODOLOGY.md`, `ETAT_ACTUEL.md`.

### Repository layout

```
study_real_meetings/
├── PROTOCOL.md          # frozen before test runs
├── manifests/           # JSONL: segment id, audio path, start/end, reference, language, split
├── references/          # AGM caption-derived references + spot-check sheet
└── scripts/             # prepare → mix noise → transcribe → score → analyse
results/real_meetings/   # CSVs: the source of truth
Memoire_LaTeX/real_meetings.tex   # \input into main_revised.tex
learning/                # §8
```

Large audio (AMI, SUMM-RE, MUSAN, AGM) is downloaded by script into a git-ignored `datasets/`
sub-folder. Only manifests and scripts are committed.

## 8. Learning track

The principle is to learn on the author's own project. Each note covers: the concept explained
simply; where it appears in *this* thesis (file, table, number); the likely jury question; and 3
self-check questions.

- `learning/PATHWAY.md`: the research pathway on one page (problem → literature → RQs → hypotheses →
  protocol → data → experiments → analysis → writing → defense → publication), with the standard
  for each step and the current position.
- `learning/GLOSSARY.md`: about 80 terms (English term + French explanation, because the defense
  is in English).
- `learning/notes/01…10`: released when the study reaches each topic (schedule in §2):
  1. audio → text (sampling, spectrograms, 8 vs 16 kHz)
  2. CTC vs encoder-decoder (wav2vec2/MMS/Conformer vs Whisper)
  3. metrics (WER, CER, DER, RTF, latency)
  4. ground truth and reference quality
  5. noise, SNR, denoising
  6. adaptation (prompting, transfer learning, fine-tuning, LoRA)
  7. statistics (CI, bootstrap, paired tests, multiple testing, effect size)
  8. real-time (chunking, VAD, streaming, the latency/accuracy trade-off)
  9. writing results, discussion and threats to validity
  10. publishing (venues, paper structure, reproducibility checklists)
- **Weekly teach-back:** the author explains 3 concepts in English as if to the jury, and gets
  precise feedback.

## 9. Defense preparation

- **Day 1:** draft of the supervisor message (Claude drafts, the author edits and sends).
- **Week 4:**
  - Traceability check: every number in the thesis and slides → its CSV → the script that
    produced it (the method of `METHODE_AUDIT.md`).
  - Update the *existing* `Soutenance_Deck_Contenu.md`, `Reponses_Jury.md` and
    `GUIDE_SOUTENANCE_ANGLAIS_FR_EN.md`.
  - Two timed mock defenses in English.
  - Question drills, including data ethics, reference reliability, the MInDS-14 choice and the
    LoRA result.

## 10. Risks

| Risk | Mitigation |
|------|------------|
| Supervisor declines the new section | The study becomes the paper's first step; learning and defense prep continue |
| NeMo / pyannote / torchaudio version conflicts on Windows | Reuse the 16/09 repaired environment; run a short environment check before week 2 |
| AMI or SUMM-RE downloads too slow or too large | Subset only (~1 h each), via HF streaming; keep the AGM-only results as a fallback |
| AGM captions turn out to be non-verbatim | Report the spot-check rate; restrict the AGM claims to relative comparisons (same reference for every system) |
| Week 2 overrun | Stop rule (§2) |
| Long-file out-of-memory (seen 16/09) | Chunked processing only; no full-file STFT |

## 11. Security note (outside the study, urgent)

The `origin` remote URL embeds a GitHub personal access token in plain text. The author must
revoke it on GitHub. Afterwards the remote is reset to
`https://github.com/LEVI226/ThesisMasterTest.git` and Git Credential Manager handles login.
