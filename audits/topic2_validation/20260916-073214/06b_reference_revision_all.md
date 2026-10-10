# 06b Sensitivity analysis to provisional alternative references — 5 confirmed defects (9 of 36 files, 117 of 468 rows)

Confirmed by the author listening (2026-09-16): en_01, en_02, en_03, en_07, fr_03 — each either truncated
(en_01, en_03, fr_03) or mis-transcribed (en_02 'henry county', en_07 'is like you open'). Noisy twins share the file;
en_clean_07 has no noisy twin (only _01.._04 exist), hence 9 files.
Rows affected: **117** of 468. Canonical CSVs and reference files untouched.

**Method limit**: corrected references are the large-v3 wording confirmed on salient phrases, not a full human
transcription. large-v3 therefore scores 0 on these clean files by construction; its corrected figures are optimistic.
Conclusions are checked for order below.

## Aggregates, mean-of-per-file (manuscript estimator)

| condition | n | WER old | WER new | Δ | CER old | CER new |
|---|---:|---:|---:|---:|---:|---:|
| L_conformer_de | 12 | 15.3 | 15.3 | +0.0 | 8.4 | 8.4 |
| L_conformer_en | 12 | 39.8 | 17.7 | -22.1 | 34.6 | 12.4 |
| L_conformer_fr | 12 | 23.6 | 15.8 | -7.8 | 16.8 | 9.8 |
| J0_small_hf_vanilla | 36 | 31.2 | 18.2 | -13.1 | 24.2 | 12.0 |
| J_lora_small | 36 | 30.2 | 18.3 | -11.9 | 23.0 | 12.2 |
| A_baseline | 36 | 63.4 | 51.8 | -11.7 | 43.6 | 33.4 |
| B_noise_reduction | 36 | 62.2 | 50.7 | -11.5 | 44.6 | 34.2 |
| C_vad | 36 | 62.2 | 50.7 | -11.5 | 45.6 | 34.8 |
| D_domain_prompt | 36 | 61.3 | 51.5 | -9.8 | 45.2 | 35.8 |
| E_forced_language | 36 | 59.6 | 49.4 | -10.2 | 41.1 | 31.5 |
| F_model_base | 36 | 48.3 | 36.0 | -12.4 | 33.6 | 21.9 |
| G_model_small | 36 | 33.3 | 18.6 | -14.7 | 24.6 | 11.8 |
| H_model_medium | 36 | 25.9 | 12.3 | -13.7 | 21.1 | 8.6 |
| I_model_large_v3 | 36 | 24.6 | 10.4 | -14.3 | 20.5 | 7.6 |
| K_wav2vec | 36 | 35.4 | 23.5 | -11.9 | 23.6 | 11.9 |

## Order checks

- Model-size ladder (A→F→G→H→I), old: 63.4 → 48.3 → 33.3 → 25.9 → 24.6 | new: 51.8 → 36.0 → 18.6 → 12.3 → 10.4 | monotone: old=True, new=True
- LoRA effect J0−J, old: +1.0 pts | new: -0.1 pts
- Prompt effect B−D, old: +0.9 | new: -0.8
- Forced language D−E, old: +1.7 | new: +2.1
- MMS (K) vs J0, old: 35.4 vs 31.2 | new: 23.5 vs 18.2
- Conformer global, old: 26.3 | new: 16.3
- Paired noise penalty (12 pairs), old: clean 61.1 → noisy 96.4, +35.3 pts
- Paired noise penalty (12 pairs), new: clean 44.1 → noisy 80.4, +36.3 pts

## Provenance (verified 2026-09-16)

All 24 local clean references are identical, after normalisation, to the `transcription` field of the published
PolyAI/minds14 (en-US, fr-FR, de-DE; HF cache of 2026-07-26). The local extraction did not truncate anything: the
confirmed defects are in the published transcriptions of these 5 sampled clips. No claim is made about the rest of the corpus.

## Reading

- Absolute WER levels in the manuscript are affected by reference defects in 5/24 clean files (21 %). The size of the
  effect depends on the provisional references and on language: de Conformer unchanged, fr −7.8, en −22.1; the exact
  correction is not established until the references are re-annotated independently.
- Under these provisional references the order checks hold, but two small effects change sign (LoRA +1.0 → −0.1,
  prompt +0.9 → −0.8): the earlier non-demonstration of a benefit did not prove equivalence, and the intervals must be
  recomputed after independent re-annotation. The ladder's monotonicity is exposed to the large-v3 bias described above.
- Because the corrected wording comes from large-v3, its own advantage at the top of the ladder is overstated here; the honest
  statement is that the ladder is monotone under both the original and the corrected references, not that the corrected gap is exact.
- Recommended: (1) declare MInDS-14 transcript quality as a limitation; (2) keep canonical files; (3) commission a word-by-word
  human transcription of the 5 clips before republishing any corrected figure; (4) rescore in a separate revision then.
