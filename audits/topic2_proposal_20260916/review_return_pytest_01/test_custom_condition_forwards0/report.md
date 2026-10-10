# STT Evaluation Report — Topic 2

**Generated:** 2026-09-16 09:07  
**Results file:** `C:\Users\ulric\Documents\ThesisMasterTest\audits\topic2_proposal_20260916\review_return_pytest_01\test_custom_condition_forwards0\results.csv`

## Experiment setup

| Condition | Model | Preprocessing | Prompt | VAD | Forced language |
|---|---|---|---|---|---|
| C1 | tiny | No | No | Yes | fr |

## Per-file results

| File | Language | Noise | Condition | WER | CER | RTF | Error |
|---|---|---|---|---:|---:|---:|---|
| fr.wav | fr | noisy | C1 | 0.00% | 0.00% | 0.100 |  |

## Descriptive aggregation

| Condition | Valid WER / rows | Mean WER | Mean CER | Mean RTF |
|---|---:|---:|---:|---:|
| C1 | 1/1 | 0.00% | 0.00% | 0.100 |

## Interpretation boundary

- Completeness: 1/1 rows have a finite WER.
- Throughput: 1/1 finite RTF measurements are below 1.
- Lowest descriptive mean WER: C1 at 0.00%.
- These aggregates are descriptive. Intervention claims require matched filenames and paired or clustered uncertainty estimates.
- RTF measures processing throughput, not complete user-perceived caption latency.
- The report does not establish performance on corporate meetings, overlapping speakers, organisation-specific vocabulary, or accessibility outcomes.

For the thesis inferential results, run `python -m backend.evaluation.run_statistical_audit` on the canonical CSVs.
