# 06 Manuscript consistency

Audited entry point: `Memoire_LaTeX/main_revised.tex` with `bibitem_revised.bib`.
`topic2_completion.tex` IS part of that document (`\input{topic2_completion}`,
line 654). `main.tex` is the earlier version and was not audited as the entry.

## A1. CONFIRMED CONTRADICTION -- latency p95 in the abstract

Within one compiled document:

| location | claim |
|---|---|
| Abstract EN (l. 239) and FR (l. 230) | "p95 of 0.84 s", stated without qualification |
| Latency section (l. 616) | 22 obs, 20 steady-state, median 0.555 s, p95 0.84 s, max 1.18 s |
| `topic2_completion` (l. 13-30) | **38 observations**, 3 inferred sessions; session 3 alone p95 4.814 s, max **11.021 s**; pooled median 0.575 s, p95 **1.614 s**; "The historical p95 of 0.844 s is not a service guarantee" |

The completion section is scientifically the sounder of the two: it retains the
slow observations instead of discarding them. The abstract was not updated to
match. A reader who reaches page 654 finds an 11-second maximum behind an
abstract advertising a 0.84 s p95.

**Severity: A (contradiction to fix before presenting results).**

Suggested abstract wording, English:
> Excluding cold starts, server-side post-endpointing latency has a median of
> 0.56 s across 35 steady-state observations, with a p95 of 1.61 s and a
> maximum of 11.02 s; the slowest session is retained rather than discarded,
> and browser rendering is not included.

French explanation: l'ancien chiffre venait de 20 observations sur deux
sessions. Le journal en compte 38 sur trois sessions. Annoncer 0,84 s alors que
le document rapporte plus loin un maximum de 11 s est la contradiction la plus
facile a reperer pour un jury.

## C1. Estimator is never named

The thesis reports mean-of-per-file WER throughout. Recomputed on condition A:

- mean of per-file WER = **63.4%** (the figure used everywhere)
- corpus-aggregate WER (total edits / total reference words) = **66.8%**

A 3.4-point gap. The choice is legitimate; not naming it is the gap.
Add once, in the metrics definition: "All WER figures are the arithmetic mean
of per-file WER, not a corpus-aggregate rate."

**Severity: C.**

## C2. WER above 100% is never explained

37 canonical runs (7 in condition A alone) carry WER > 100%, up to 166.7%,
because insertions are unbounded when the hypothesis is longer than the
reference. The manuscript never states this. A jury member reading a WER of
166.7% will ask, and the unbounded values also inflate the mean-of-per-file
estimator relative to the aggregate.

**Severity: C.**

## Verified as sound (no action)

- **Ladder backend caveat is already disclosed.** The manuscript states that
  G/H/I are GPU-float16 while tiny/base canonical figures are CPU-INT8, calls
  the divergence small relative to model-size effects, and re-measures tiny/base
  RTF on GPU for the speed table. The audit measured that divergence precisely:
  tiny -1.1, base -3.5, mean -1.7 points across five conditions (GPU better).
  The disclosure is accurate.
- **Noise contrast is correctly paired.** 61.1% -> 96.4% on 12 matched pairs,
  penalty 35.3 points, paired bootstrap 95% CI [6.8, 60.1] (unit = pair,
  seed 42, B = 10000). The 47.0% figure is correctly retained as descriptive only.
- **VAD condition uses the right comparator.** C vs B re-measured on GPU:
  clean -3.8, noisy +6.0 points. Same backend, one variable. Reproduces exactly.
- **"pre-registered" has been replaced by "pre-specified"** throughout.

## Optional improvement (C3): a backend-consistent ladder already exists

`stt_eval_pilot_results_GPU.csv` contains GPU runs of conditions A and F.
A single-backend ladder can therefore be reported with no new inference:

| model | GPU float16 WER |
|---|---:|
| tiny | 62.3% |
| base | 44.9% |
| small | 33.3% |
| medium | 25.9% |
| large-v3 | 24.6% |

Monotone, one variable (model size), no backend change. This would remove the
caveat rather than merely disclose it. Range becomes 37.7 points instead of 38.8.
