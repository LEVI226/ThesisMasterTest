# 06 Reference revision — minds14_en_clean_01 (and its noisy twin)

Original reference : `I would like to set up a joint account with my partner`
Corrected reference: `I would like to set up a joint account with my partner how do I proceed with doing that`  (phrase confirmed by listening; punctuation irrelevant under normalisation)
Affected canonical rows: **26** of 468 (two files across every condition).
Canonical files untouched; this is a separate revision.

## Per-row impact

| source | file | condition | model | WER old | WER new | CER old | CER new |
|---|---|---|---|---:|---:|---:|---:|
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | A_baseline | tiny | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | A_baseline | tiny | 0.8333 | 0.1579 | 0.6744 | 0.0435 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | B_noise_reduction | tiny | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | B_noise_reduction | tiny | 0.9167 | 0.2105 | 0.7209 | 0.0725 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | D_domain_prompt | tiny | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | D_domain_prompt | tiny | 0.5833 | 0.0526 | 0.5581 | 0.0435 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | E_forced_language | tiny | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | E_forced_language | tiny | 0.5833 | 0.0526 | 0.5581 | 0.0435 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | F_model_base | base | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | F_model_base | base | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | G_model_small | small | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | G_model_small | small | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | H_model_medium | medium | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | H_model_medium | medium | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | I_model_large_v3 | large-v3 | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | I_model_large_v3 | large-v3 | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_clean_01.wav | C_vad | tiny | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_pilot_results.csv | minds14_en_noisy_01.wav | C_vad | tiny | 0.9167 | 0.2105 | 0.7209 | 0.0725 |
| stt_eval_lora_results.csv | minds14_en_clean_01.wav | J0_small_hf_vanilla | whisper-small-hf-vanilla | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_lora_results.csv | minds14_en_noisy_01.wav | J0_small_hf_vanilla | whisper-small-hf-vanilla | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_lora_results.csv | minds14_en_clean_01.wav | J_lora_small | whisper-small+lora | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_lora_results.csv | minds14_en_noisy_01.wav | J_lora_small | whisper-small+lora | 0.5833 | 0.0000 | 0.6047 | 0.0000 |
| stt_eval_wav2vec_results.csv | minds14_en_clean_01.wav | K_wav2vec | mms-1b-all | 0.6667 | 0.0526 | 0.6512 | 0.0290 |
| stt_eval_wav2vec_results.csv | minds14_en_noisy_01.wav | K_wav2vec | mms-1b-all | 0.8333 | 0.2632 | 0.7442 | 0.1594 |
| stt_eval_conformer_results.csv | minds14_en_clean_01.wav | L_conformer_en | nvidia/stt_en_conformer_ctc_large | 0.4167 | 0.1053 | 0.3953 | 0.1304 |
| stt_eval_conformer_results.csv | minds14_en_noisy_01.wav | L_conformer_en | nvidia/stt_en_conformer_ctc_large | 0.5833 | 0.0000 | 0.6047 | 0.0000 |

## Aggregate impact (mean-of-per-file WER, the manuscript's estimator)

| condition | n | WER old | WER new | Δ pts | CER old | CER new |
|---|---:|---:|---:|---:|---:|---:|
| L_conformer_de | 12 | 15.3 % | 15.3 % | +0.0 | 8.4 % | 8.4 % |
| L_conformer_en | 12 | 39.8 % | 32.4 % | -7.5 | 34.6 % | 27.4 % |
| L_conformer_fr | 12 | 23.6 % | 23.6 % | +0.0 | 16.8 % | 16.8 % |
| J0_small_hf_vanilla | 36 | 31.2 % | 28.0 % | -3.2 | 24.2 % | 20.8 % |
| J_lora_small | 36 | 30.2 % | 27.0 % | -3.2 | 23.0 % | 19.7 % |
| A_baseline | 36 | 63.4 % | 60.0 % | -3.5 | 43.6 % | 40.1 % |
| B_noise_reduction | 36 | 62.2 % | 58.6 % | -3.6 | 44.6 % | 41.1 % |
| C_vad | 36 | 62.2 % | 58.6 % | -3.6 | 45.6 % | 42.1 % |
| D_domain_prompt | 36 | 61.3 % | 58.2 % | -3.1 | 45.2 % | 42.1 % |
| E_forced_language | 36 | 59.6 % | 56.5 % | -3.1 | 41.1 % | 37.9 % |
| F_model_base | 36 | 48.3 % | 45.1 % | -3.2 | 33.6 % | 30.3 % |
| G_model_small | 36 | 33.3 % | 30.1 % | -3.2 | 24.6 % | 21.2 % |
| H_model_medium | 36 | 25.9 % | 22.7 % | -3.2 | 21.1 % | 17.7 % |
| I_model_large_v3 | 36 | 24.6 % | 21.4 % | -3.2 | 20.5 % | 17.2 % |
| K_wav2vec | 36 | 35.4 % | 32.1 % | -3.3 | 23.6 % | 20.2 % |

## Headline figures in the manuscript, before → after

- A tiny baseline 63.4: 63.4 % → **60.0 %** (-3.5 pts)
- B 62.2: 62.2 % → **58.6 %** (-3.6 pts)
- F base 48.3: 48.3 % → **45.1 %** (-3.2 pts)
- G small 33.3: 33.3 % → **30.1 %** (-3.2 pts)
- H medium 25.9: 25.9 % → **22.7 %** (-3.2 pts)
- I large-v3 24.6: 24.6 % → **21.4 %** (-3.2 pts)
- J0 whisper-small HF 31.2: 31.2 % → **28.0 %** (-3.2 pts)
- J LoRA 30.2: 30.2 % → **27.0 %** (-3.2 pts)
- K MMS 35.4: 35.4 % → **32.1 %** (-3.3 pts)
- L Conformer global 26.3: 26.3 % → **23.8 %**
- Paired noise effect (old): clean 61.1 % → noisy 96.4 %, penalty +35.3 pts
- Paired noise effect (new): clean 56.3 % → noisy 90.8 %, penalty +34.5 pts

## Reading

- Every affected hypothesis that was actually correct was charged 7 insertions (7/12 = 0.5833). The correction lowers WER for those rows and raises nothing.
- The direction of every conclusion in the manuscript is unchanged; the magnitudes move by the amounts above.
- Recommended handling: keep the canonical CSVs and reference file as the record of what was scored; add this revision as an erratum note with the corrected aggregates, and re-listen to the other 23 references before the defense (same risk class).
