# revision_v2 — rescoring with 16 revised references (clean + noisy twins), originals untouched

Revised clips: minds14_en_clean_01, minds14_en_clean_02, minds14_en_clean_03, minds14_en_clean_04, minds14_en_clean_05, minds14_en_clean_06, minds14_en_clean_07, minds14_en_clean_08, minds14_fr_clean_01, minds14_fr_clean_02, minds14_fr_clean_03, minds14_fr_clean_04, minds14_fr_clean_05, minds14_fr_clean_06, minds14_fr_clean_07, minds14_fr_clean_08. Unrevised clips keep their original reference.

| condition | n | WER old | WER new | 95% CI new (clustered by source clip) | CER old | CER new |
|---|---:|---:|---:|---|---:|---:|
| A_baseline | 36 | 63.4 | 50.6 | [35.0, 65.4] | 43.6 | 33.0 |
| B_noise_reduction | 36 | 62.2 | 50.8 | [36.0, 64.3] | 44.6 | 34.4 |
| C_vad | 36 | 62.2 | 50.5 | [36.0, 63.8] | 45.6 | 34.9 |
| D_domain_prompt | 36 | 61.3 | 51.3 | [36.2, 64.8] | 45.2 | 35.7 |
| E_forced_language | 36 | 59.6 | 48.9 | [34.5, 62.3] | 41.1 | 31.3 |
| F_model_base | 36 | 48.3 | 35.5 | [21.4, 50.0] | 33.6 | 22.1 |
| G_model_small | 36 | 33.3 | 19.4 | [9.1, 32.1] | 24.6 | 12.7 |
| H_model_medium | 36 | 25.9 | 13.2 | [6.2, 21.3] | 21.1 | 9.5 |
| I_model_large_v3 | 36 | 24.6 | 10.9 | [4.4, 19.2] | 20.5 | 8.3 |
| J0_small_hf_vanilla | 36 | 31.2 | 18.9 | [10.3, 28.3] | 24.2 | 12.9 |
| J_lora_small | 36 | 30.2 | 18.3 | [9.9, 27.1] | 23.0 | 12.1 |
| K_wav2vec | 36 | 35.4 | 23.9 | [15.1, 32.7] | 23.6 | 12.3 |
| L_conformer_de | 12 | 15.3 | 15.3 | [5.8, 27.6] | 8.4 | 8.4 |
| L_conformer_en | 12 | 39.8 | 16.1 | [3.6, 33.2] | 34.6 | 11.8 |
| L_conformer_fr | 12 | 23.6 | 15.1 | [2.7, 30.5] | 16.8 | 9.4 |

## Paired contrasts with clustered 95% bootstrap CI (new references)

- size B(tiny) − I(large-v3): +39.9 pts, CI [+26.3, +53.0]
- LoRA J0 − J: +0.6 pts, CI [-1.9, +3.0]
- prompt B − D: -0.5 pts, CI [-3.2, +2.1]
- forced language D − E: +2.4 pts, CI [-2.6, +7.0]
- MMS − whisper-small(J0): +5.0 pts, CI [-1.9, +13.0]
- noise penalty A, 12 matched pairs: +36.9 pts, CI [+7.6, +62.8]

## Status

- references revised so far: 16/24; pending: 8 (German rows need another annotator).
- Figures above are provisional until all 24 clips are re-annotated and, ideally, double-checked.
- Originals (datasets/stt_eval/references, results/*.csv) unchanged.
