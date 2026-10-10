# 03 Results recalculation (independent scorer)

## File inventory and hashes

| file | rows | sha256 (first 16) | role |
|---|---:|---|---|
| `results/stt_eval_pilot_results.csv` | 324 | `d180fb122347d1dc` | pilot+ladder+VAD |
| `results/stt_eval_lora_results.csv` | 72 | `3de7153f61e1b091` | LoRA paired |
| `results/stt_eval_wav2vec_results.csv` | 36 | `2ad082e6163c2e5c` | wav2vec/MMS |
| `results/stt_eval_conformer_results.csv` | 36 | `37cf3ed40f81ad65` | Conformer |

**Canonical total: 468 runs** (claimed 468: MATCH).

Excluded from the canonical total (present but out of campaign):

- `results/live_latency.csv` (38 rows)
- `results/lora_training_log.csv` (11 rows)
- `results/meeting_eval_results.csv` (7 rows)
- `results/stt_eval_fleurs_results.csv` (300 rows)
- `results/stt_eval_pilot_results_backup_avant_bloc5.csv` (288 rows)
- `results/stt_eval_pilot_results_CPU_baseline.csv` (180 rows)
- `results/stt_eval_pilot_results_GPU.csv` (180 rows)

## Duplicate / error / empty checks

- Duplicate (source, file, model, condition, flags) keys: **0**
- Rows carrying a non-empty `error` field: **0**
- Rows with EMPTY reference (WER undefined, must not score 0): **0**
- Rows with EMPTY hypothesis (real failure, must score 1.0): **0**

## Stored vs recomputed WER

- Rows recomputed: **468** (undefined refs skipped: 0)
- Max |stored - recomputed|: **4.62e-05**
- Rows disagreeing beyond 1e-6: **187**
  - results/stt_eval_pilot_results.csv minds14_en_clean_01.wav tiny A_baseline: stored=0.5833 recomputed=0.5833
  - results/stt_eval_pilot_results.csv minds14_en_noisy_01.wav tiny A_baseline: stored=0.8333 recomputed=0.8333
  - results/stt_eval_pilot_results.csv minds14_en_clean_02.wav tiny A_baseline: stored=0.9333 recomputed=0.9333
  - results/stt_eval_pilot_results.csv minds14_en_noisy_02.wav tiny A_baseline: stored=1.6667 recomputed=1.6667
  - results/stt_eval_pilot_results.csv minds14_en_clean_03.wav tiny A_baseline: stored=0.5556 recomputed=0.5556
  - results/stt_eval_pilot_results.csv minds14_en_noisy_03.wav tiny A_baseline: stored=0.7111 recomputed=0.7111
  - results/stt_eval_pilot_results.csv minds14_en_clean_04.wav tiny A_baseline: stored=0.7143 recomputed=0.7143
  - results/stt_eval_pilot_results.csv minds14_en_noisy_04.wav tiny A_baseline: stored=1.1429 recomputed=1.1429
  - results/stt_eval_pilot_results.csv minds14_en_clean_06.wav tiny A_baseline: stored=0.2857 recomputed=0.2857
  - results/stt_eval_pilot_results.csv minds14_en_clean_07.wav tiny A_baseline: stored=0.6364 recomputed=0.6364
  - results/stt_eval_pilot_results.csv minds14_fr_clean_03.wav tiny A_baseline: stored=1.0909 recomputed=1.0909
  - results/stt_eval_pilot_results.csv minds14_fr_noisy_03.wav tiny A_baseline: stored=1.3636 recomputed=1.3636
  - results/stt_eval_pilot_results.csv minds14_fr_clean_07.wav tiny A_baseline: stored=1.1429 recomputed=1.1429
  - results/stt_eval_pilot_results.csv minds14_de_clean_03.wav tiny A_baseline: stored=0.3571 recomputed=0.3571
  - results/stt_eval_pilot_results.csv minds14_de_clean_05.wav tiny A_baseline: stored=0.1538 recomputed=0.1538
- Rows with WER > 100%: **37**
