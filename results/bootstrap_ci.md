# Bootstrap 95% confidence intervals (n=36 per group, 10 000 resamples, seed 42)

Computed from the canonical per-clip WER values in `results/` (same scorer). Answers the "n=36, is it statistically fragile?" question.

## Model-size ladder (condition B config)

| Model | mean WER | 95% CI |
|---|---|---|
| tiny | 62.2% | [50.5, 74.1] |
| base | 48.3% | [34.3, 63.8] |
| small | 33.3% | [20.3, 48.3] |
| medium | 25.9% | [15.8, 38.1] |
| large-v3 | 24.6% | [14.0, 36.8] |

**Gap tiny − large-v3:** 37.6 pts, 95% CI [20.9, 53.6] → strictly positive, well beyond sampling noise.

## Noise effect (baseline A)

| Split | n | mean WER | 95% CI |
|---|---|---|---|
| clean | 24 | 47.0% | [32.4, 63.6] |
| noisy | 12 | 96.4% | [74.6, 118.2] |

**Noise penalty (noisy − clean):** 49.4 pts, 95% CI [23.4, 75.8].

## Architectures at whisper-small scale

| System | mean WER | 95% CI |
|---|---|---|
| Whisper-small (J0, auto-detect) | 31.2% | [20.1, 43.9] |
| Whisper-small + LoRA (J) | 30.2% | [19.8, 42.2] |
| MMS (language given) | 35.4% | [24.7, 46.7] |
| Conformer (language given) | 26.3% | [16.5, 37.4] |

**LoRA effect (J0 − J):** 1.0 pts, 95% CI [-15.3, 17.8] → CI spans 0: **not significant**, consistent with the thesis.
