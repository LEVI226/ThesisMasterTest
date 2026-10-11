# Reproducible statistical audit

All confidence intervals use 10,000 bootstrap resamples with seed 42. System comparisons resample the 24 independent source utterances as clusters; clean/noisy derivatives remain together.

| Comparison | Source utterances | Files | Mean difference | 95% CI |
|---|---:|---:|---:|---:|
| Added noise (noisy - matched clean) | 12 | 24 | 35.3 WER points | [7.0, 60.0] |
| Model size (tiny - large-v3) | 24 | 36 | 37.6 WER points | [24.3, 50.7] |
| LoRA (vanilla - adapted) | 24 | 36 | 1.0 WER points | [-2.4, 5.3] |
| Architecture (MMS - Conformer) | 24 | 36 | 9.1 WER points | [3.0, 16.3] |

## Live latency

Cold starts are rows whose per-session utterance_id equals 1 (n=2; values: 3.612 s, 2.601 s).

Steady-state post-endpointing latency (n=20): median 0.555 s, p95 0.844 s, maximum 1.177 s.

The fixed 0.6 s VAD silence window is not included in these processing latencies.
