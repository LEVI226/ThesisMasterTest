# Headline contrasts, recomputed

## Noise effect, condition A_baseline (model tiny)

- clean rows: 24, noisy rows: 12
- **Descriptive split** (different utterances): clean mean WER = 47.0%, noisy = 96.4%
- **Matched pairs found: 12**
- **Paired** clean = 61.1%, noisy = 96.4%, penalty = **35.3 points**
- Paired bootstrap 95% CI on the penalty (unit = pair, seed=42, B=10000): **[6.8, 60.1] points**

## Estimator sensitivity (condition A, all 36 files)

- mean-of-per-file WER = **63.4%**
- corpus-aggregate WER (total edits / total ref words) = **66.8%**
- rows with WER > 100%: 7 (unbounded, inflates the mean)

## Model-size ladder (mean-of-per-file WER)
| condition | model | n | backend | WER |
|---|---|---:|---|---:|
| A_baseline | tiny | 36 | - | 63.4% |
| B_noise_reduction | tiny | 36 | - | 62.2% |
| C_vad | tiny | 36 | - | 62.2% |
| D_domain_prompt | tiny | 36 | - | 61.3% |
| E_forced_language | tiny | 36 | - | 59.6% |
| F_model_base | base | 36 | - | 48.3% |
| G_model_small | small | 36 | - | 33.3% |
| H_model_medium | medium | 36 | - | 25.9% |
| I_model_large_v3 | large-v3 | 36 | - | 24.6% |

## Cross-architecture and LoRA

- wav2vec/MMS / `K_wav2vec`: n=36, WER = **35.4%**
- Conformer / `L_conformer_de`: n=12, WER = **15.3%**
- Conformer / `L_conformer_en`: n=12, WER = **39.8%**
- Conformer / `L_conformer_fr`: n=12, WER = **23.6%**
- LoRA study / `J0_small_hf_vanilla`: n=36, WER = **31.2%**
- LoRA study / `J_lora_small`: n=36, WER = **30.2%**
