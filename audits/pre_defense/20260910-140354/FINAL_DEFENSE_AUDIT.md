# FINAL DEFENSE AUDIT -- Topic 2

Commit `f62705a`, branch `main`, dirty working tree. Manuscript entry audited:
`Memoire_LaTeX/main_revised.tex` + `bibitem_revised.bib` + `topic2_completion.tex`.
No canonical artefact was modified.

## Verdict

The numbers in this thesis reproduce. Every headline figure was recomputed from
the stored transcripts with an independently reimplemented scorer, and every one
matched to within CSV rounding. The campaign is what it claims to be: 468 runs,
no duplicates, no silent failures, no empty references. That is the part most
theses fail, and this one passes it.

One contradiction must be fixed before the defense, and it is in the abstract.

## Evidence table

| check | result |
|---|---|
| Canonical run count | **468** = 324 + 72 + 36 + 36. Claim MATCHES. |
| Duplicate (file, model, condition, flags) keys | 0 |
| Rows with non-empty `error` | 0 |
| Empty references (would silently score 0) | 0 |
| Empty hypotheses | 0 |
| Stored vs independently recomputed WER, 468 rows | max abs diff **4.62e-05** (CSV rounded to 4 dp) |
| Rows with WER > 100% | 37 (real, unbounded insertions) |
| Backup/parallel CSVs correctly excluded | 7 files, incl. FLEURS (300) and a 288-row pre-BLOC5 backup |
| Unit tests | **51 passed**, 0 failed (8 initial errors were a non-writable temp dir) |

File hashes (sha256, first 16):
`stt_eval_pilot_results.csv` d180fb122347d1dc ·
`stt_eval_lora_results.csv` 3de7153f61e1b091 ·
`stt_eval_wav2vec_results.csv` 2ad082e6163c2e5c ·
`stt_eval_conformer_results.csv` 37cf3ed40f81ad65

## Recomputed headline figures

| claim | recomputed | status |
|---|---|---|
| Ladder tiny->large-v3 63.4 / 48.3 / 33.3 / 25.9 / 24.6 | identical | OK |
| Noise, paired, 61.1 -> 96.4, +35.3 pts | identical, CI [6.8, 60.1] | OK |
| Noise, descriptive 47.0 -> 96.4 | identical, correctly labelled descriptive | OK |
| VAD: clean -3.8, noisy +6.0 vs B on GPU | identical | OK |
| LoRA 31.2 -> 30.2 | identical | OK |
| wav2vec/MMS 35.4 | identical | OK |
| Conformer de 15.3 / fr 23.6 / en 39.8 | identical | OK |
| Cross-backend divergence "small" | measured: tiny -1.1, base -3.5, mean -1.7 pts | OK, now quantified |

## Issues by category

**A -- fix before presenting results**

1. Abstract claims "p95 of 0.84 s" while `topic2_completion`, inside the same
   document, reports 38 observations with pooled p95 1.614 s and max 11.021 s.
   See `06_manuscript_consistency.md` for replacement wording.

**B -- declared limitations, supervisor's call**

2. MInDS-14 is 8 kHz telephone banking speech, not multi-speaker meeting audio
   and not Nestlé speech. Already stated in abstract and conclusion.
3. Diarization (DER 0.585) validates integration, not accuracy. Already stated.
4. No end-user accessibility evaluation in Topic 2. Already stated.
5. 24 distinct utterances behind 36 files; noise effect estimable only on
   12 pairs. Already stated and correctly handled.

**C -- optional improvements**

6. Name the estimator (mean-of-per-file, 63.4%, vs aggregate 66.8%).
7. Explain WER > 100% once.
8. Report the backend-consistent GPU ladder (62.3 / 44.9 / 33.3 / 25.9 / 24.6)
   using data that already exists; removes the caveat instead of disclosing it.
9. Canonical CSVs have no `device`/`compute_type` column. Backend is recoverable
   only from prose and RTF. Add the column for any future run.

## Blocking, outside the audit

- **No compiled PDF of the thesis exists.** Not produced here: no local TeX with
  babel-french/biblatex. Build on Overleaf/TeXPage from `main_revised.tex` with
  `bibitem_revised.bib` and `topic2_completion.tex` in the same project.
- `main_FR.tex` is frozen at 23 August, missing the whole revision pass.
- Defense date and jury composition still "To be confirmed".

## Five defensible English claims

1. "Across 468 runs on a fixed evaluation set with a single scorer, model size
   is the dominant accuracy lever: mean WER falls from 63.4% to 24.6%."
2. "On the twelve matched clean/noisy pairs, 8 dB white noise costs 35.3 WER
   points, 95% bootstrap CI [6.8, 60.1]."
3. "Forcing the decoding language repairs wrong-script output at no measurable
   computational cost."
4. "Prompting and LoRA each move WER by about one point; the LoRA effect is not
   statistically established at this sample size."
5. "The diarization experiment validates integration, not speaker accuracy."

## Five formulations to avoid

1. "Validated on real corporate meetings" -- the corpus is telephone banking speech.
2. "Real-time guaranteed" / "sub-second guaranteed" -- the log contains an 11 s maximum.
3. "Domain adaptation validated" -- no entity-level metric was computed.
4. "Multilingual" as evidence of code-switching -- each clip is single-language.
5. "Pre-registered" -- there is no public registration; the manuscript now says
   "pre-specified", keep it that way in speech too.
