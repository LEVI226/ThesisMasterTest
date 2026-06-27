# STT Evaluation Report — Topic 2

**Generated:** 2026-06-26 22:52  
**Results file:** `results/stt_eval_pilot_results.csv`

---

## 1. Experiment Setup

### Objective
Evaluate faster-whisper STT accuracy and efficiency across different preprocessing configurations, domain adaptation strategies, and noise conditions — in support of Master Thesis Topic 2: *Advanced Speech-to-Text Models for Noisy, Multilingual Corporate Meetings*.

### Evaluation Conditions

This pilot run implements 5 of the 6 conditions defined in `Topic2_Outline_Reference.md` §5.3 (A, B, D, E, F). **Condition C (VAD preprocessing) is not implemented** in the current codebase — see §6 Limitations.

| Tag | Outline Cond. | Model | Preprocessing | Domain Prompt | Language |
|---|---|---|---|---|---|
| A_baseline | A | tiny | No | No | Auto |
| B_noise_reduction | B | tiny | Yes (noisereduce) | No | Auto |
| D_domain_prompt | D | tiny | Yes | Yes (Nestlé vocab) | Auto |
| E_forced_language | E | tiny | Yes | Yes | Forced (true language per sample) |
| F_model_base | F | **base** | Yes | No | Auto |

180 transcription runs total (36 samples × 5 conditions). 0 runtime errors, 0 missing/NaN metrics.

### Model Configuration
- **STT Engine:** faster-whisper
- **Model sizes tested:** base, tiny
- **Languages in dataset:** de, en, fr
- **Noise conditions:** clean, noisy

### Hardware
CPU-only sandbox (no GPU), faster-whisper int8 quantization, Ubuntu 22.04 / Python 3.10.

---

## 2. Metrics Reference

| Metric | Formula | Interpretation |
|---|---|---|
| **WER** | (S+D+I) / N_ref_words | 0 = perfect; lower is better |
| **CER** | (S+D+I) / N_ref_chars | Stricter than WER; lower is better |
| **RTF** | processing_time / audio_duration | <1 = faster than real-time (good) |

---

## 3. Results Table

| File | Language | Noise | Model | Prep | Prompt | Lang | WER | CER | RTF | Time (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| minds14_en_clean_01.wav | en | clean | tiny | ✗ | ✗ | auto | 58.33% | 60.47% | 0.254 | 2.8 |
| minds14_en_noisy_01.wav | en | noisy | tiny | ✗ | ✗ | auto | 83.33% | 67.44% | 0.157 | 1.7 |
| minds14_en_clean_02.wav | en | clean | tiny | ✗ | ✗ | auto | 93.33% | 69.64% | 0.276 | 1.8 |
| minds14_en_noisy_02.wav | en | noisy | tiny | ✗ | ✗ | auto | 166.67% | 116.07% | 0.229 | 1.5 |
| minds14_en_clean_03.wav | en | clean | tiny | ✗ | ✗ | auto | 55.56% | 60.00% | 0.091 | 2.2 |
| minds14_en_noisy_03.wav | en | noisy | tiny | ✗ | ✗ | auto | 71.11% | 68.67% | 0.125 | 3.0 |
| minds14_en_clean_04.wav | en | clean | tiny | ✗ | ✗ | auto | 71.43% | 29.17% | 0.389 | 1.3 |
| minds14_en_noisy_04.wav | en | noisy | tiny | ✗ | ✗ | auto | 114.29% | 62.50% | 0.476 | 1.5 |
| minds14_en_clean_05.wav | en | clean | tiny | ✗ | ✗ | auto | 10.00% | 5.88% | 0.354 | 1.4 |
| minds14_en_clean_06.wav | en | clean | tiny | ✗ | ✗ | auto | 28.57% | 17.39% | 0.291 | 1.3 |
| minds14_en_clean_07.wav | en | clean | tiny | ✗ | ✗ | auto | 63.64% | 32.61% | 0.255 | 1.5 |
| minds14_en_clean_08.wav | en | clean | tiny | ✗ | ✗ | auto | 18.75% | 9.26% | 0.166 | 1.4 |
| minds14_fr_clean_01.wav | fr | clean | tiny | ✗ | ✗ | auto | 40.00% | 18.52% | 0.322 | 1.2 |
| minds14_fr_noisy_01.wav | fr | noisy | tiny | ✗ | ✗ | auto | 100.00% | 77.78% | 0.695 | 2.6 |
| minds14_fr_clean_02.wav | fr | clean | tiny | ✗ | ✗ | auto | 0.00% | 0.00% | 0.254 | 1.2 |
| minds14_fr_noisy_02.wav | fr | noisy | tiny | ✗ | ✗ | auto | 100.00% | 100.00% | 0.647 | 3.1 |
| minds14_fr_clean_03.wav | fr | clean | tiny | ✗ | ✗ | auto | 109.09% | 73.53% | 0.181 | 2.6 |
| minds14_fr_noisy_03.wav | fr | noisy | tiny | ✗ | ✗ | auto | 136.36% | 101.96% | 0.767 | 11.2 |
| minds14_fr_clean_04.wav | fr | clean | tiny | ✗ | ✗ | auto | 40.00% | 34.38% | 0.344 | 1.2 |
| minds14_fr_noisy_04.wav | fr | noisy | tiny | ✗ | ✗ | auto | 140.00% | 71.88% | 0.825 | 3.0 |
| minds14_fr_clean_05.wav | fr | clean | tiny | ✗ | ✗ | auto | 0.00% | 0.00% | 0.359 | 1.2 |
| minds14_fr_clean_06.wav | fr | clean | tiny | ✗ | ✗ | auto | 50.00% | 16.13% | 0.308 | 1.2 |
| minds14_fr_clean_07.wav | fr | clean | tiny | ✗ | ✗ | auto | 114.29% | 77.78% | 0.811 | 4.5 |
| minds14_fr_clean_08.wav | fr | clean | tiny | ✗ | ✗ | auto | 0.00% | 0.00% | 0.274 | 1.2 |
| minds14_de_clean_01.wav | de | clean | tiny | ✗ | ✗ | auto | 162.50% | 92.31% | 0.509 | 3.0 |
| minds14_de_noisy_01.wav | de | noisy | tiny | ✗ | ✗ | auto | 75.00% | 61.54% | 0.536 | 3.1 |
| minds14_de_clean_02.wav | de | clean | tiny | ✗ | ✗ | auto | 57.50% | 33.15% | 0.131 | 1.8 |
| minds14_de_noisy_02.wav | de | noisy | tiny | ✗ | ✗ | auto | 100.00% | 73.48% | 0.196 | 2.6 |
| minds14_de_clean_03.wav | de | clean | tiny | ✗ | ✗ | auto | 35.71% | 17.74% | 0.161 | 1.4 |
| minds14_de_noisy_03.wav | de | noisy | tiny | ✗ | ✗ | auto | 50.00% | 30.65% | 0.164 | 1.4 |
| minds14_de_clean_04.wav | de | clean | tiny | ✗ | ✗ | auto | 10.00% | 4.76% | 0.238 | 1.3 |
| minds14_de_noisy_04.wav | de | noisy | tiny | ✗ | ✗ | auto | 20.00% | 23.81% | 0.247 | 1.3 |
| minds14_de_clean_05.wav | de | clean | tiny | ✗ | ✗ | auto | 15.38% | 6.78% | 0.117 | 1.6 |
| minds14_de_clean_06.wav | de | clean | tiny | ✗ | ✗ | auto | 23.08% | 6.45% | 0.176 | 1.4 |
| minds14_de_clean_07.wav | de | clean | tiny | ✗ | ✗ | auto | 28.57% | 27.27% | 0.184 | 1.3 |
| minds14_de_clean_08.wav | de | clean | tiny | ✗ | ✗ | auto | 41.67% | 19.30% | 0.115 | 1.6 |
| minds14_en_clean_01.wav | en | clean | tiny | ✓ | ✗ | auto | 58.33% | 60.47% | 0.136 | 1.5 |
| minds14_en_noisy_01.wav | en | noisy | tiny | ✓ | ✗ | auto | 91.67% | 72.09% | 0.135 | 1.5 |
| minds14_en_clean_02.wav | en | clean | tiny | ✓ | ✗ | auto | 73.33% | 57.14% | 0.216 | 1.4 |
| minds14_en_noisy_02.wav | en | noisy | tiny | ✓ | ✗ | auto | 126.67% | 98.21% | 0.229 | 1.5 |
| minds14_en_clean_03.wav | en | clean | tiny | ✓ | ✗ | auto | 60.00% | 63.33% | 0.094 | 2.3 |
| minds14_en_noisy_03.wav | en | noisy | tiny | ✓ | ✗ | auto | 62.22% | 68.67% | 0.091 | 2.2 |
| minds14_en_clean_04.wav | en | clean | tiny | ✓ | ✗ | auto | 71.43% | 29.17% | 0.378 | 1.2 |
| minds14_en_noisy_04.wav | en | noisy | tiny | ✓ | ✗ | auto | 85.71% | 54.17% | 0.366 | 1.2 |
| minds14_en_clean_05.wav | en | clean | tiny | ✓ | ✗ | auto | 10.00% | 8.82% | 0.328 | 1.3 |
| minds14_en_clean_06.wav | en | clean | tiny | ✓ | ✗ | auto | 28.57% | 17.39% | 0.272 | 1.2 |
| minds14_en_clean_07.wav | en | clean | tiny | ✓ | ✗ | auto | 90.91% | 50.00% | 0.232 | 1.4 |
| minds14_en_clean_08.wav | en | clean | tiny | ✓ | ✗ | auto | 12.50% | 5.56% | 0.163 | 1.4 |
| minds14_fr_clean_01.wav | fr | clean | tiny | ✓ | ✗ | auto | 40.00% | 25.93% | 0.306 | 1.1 |
| minds14_fr_noisy_01.wav | fr | noisy | tiny | ✓ | ✗ | auto | 120.00% | 70.37% | 0.994 | 3.7 |
| minds14_fr_clean_02.wav | fr | clean | tiny | ✓ | ✗ | auto | 40.00% | 6.25% | 0.267 | 1.3 |
| minds14_fr_noisy_02.wav | fr | noisy | tiny | ✓ | ✗ | auto | 100.00% | 100.00% | 1.634 | 7.8 |
| minds14_fr_clean_03.wav | fr | clean | tiny | ✓ | ✗ | auto | 100.00% | 71.57% | 0.268 | 3.9 |
| minds14_fr_noisy_03.wav | fr | noisy | tiny | ✓ | ✗ | auto | 100.00% | 100.00% | 0.898 | 13.2 |
| minds14_fr_clean_04.wav | fr | clean | tiny | ✓ | ✗ | auto | 60.00% | 46.88% | 0.398 | 1.4 |
| minds14_fr_noisy_04.wav | fr | noisy | tiny | ✓ | ✗ | auto | 120.00% | 81.25% | 0.855 | 3.1 |
| minds14_fr_clean_05.wav | fr | clean | tiny | ✓ | ✗ | auto | 50.00% | 36.00% | 0.734 | 2.4 |
| minds14_fr_clean_06.wav | fr | clean | tiny | ✓ | ✗ | auto | 50.00% | 9.68% | 0.354 | 1.4 |
| minds14_fr_clean_07.wav | fr | clean | tiny | ✓ | ✗ | auto | 100.00% | 100.00% | 0.661 | 3.7 |
| minds14_fr_clean_08.wav | fr | clean | tiny | ✓ | ✗ | auto | 0.00% | 0.00% | 0.294 | 1.3 |
| minds14_de_clean_01.wav | de | clean | tiny | ✓ | ✗ | auto | 125.00% | 76.92% | 0.690 | 4.0 |
| minds14_de_noisy_01.wav | de | noisy | tiny | ✓ | ✗ | auto | 87.50% | 64.10% | 0.571 | 3.3 |
| minds14_de_clean_02.wav | de | clean | tiny | ✓ | ✗ | auto | 65.00% | 34.25% | 0.161 | 2.1 |
| minds14_de_noisy_02.wav | de | noisy | tiny | ✓ | ✗ | auto | 100.00% | 72.93% | 0.146 | 1.9 |
| minds14_de_clean_03.wav | de | clean | tiny | ✓ | ✗ | auto | 35.71% | 17.74% | 0.186 | 1.6 |
| minds14_de_noisy_03.wav | de | noisy | tiny | ✓ | ✗ | auto | 42.86% | 27.42% | 0.186 | 1.6 |
| minds14_de_clean_04.wav | de | clean | tiny | ✓ | ✗ | auto | 10.00% | 4.76% | 0.263 | 1.4 |
| minds14_de_noisy_04.wav | de | noisy | tiny | ✓ | ✗ | auto | 20.00% | 16.67% | 0.267 | 1.4 |
| minds14_de_clean_05.wav | de | clean | tiny | ✓ | ✗ | auto | 15.38% | 6.78% | 0.126 | 1.7 |
| minds14_de_clean_06.wav | de | clean | tiny | ✓ | ✗ | auto | 15.38% | 9.68% | 0.191 | 1.5 |
| minds14_de_clean_07.wav | de | clean | tiny | ✓ | ✗ | auto | 28.57% | 21.21% | 0.190 | 1.4 |
| minds14_de_clean_08.wav | de | clean | tiny | ✓ | ✗ | auto | 41.67% | 18.42% | 0.128 | 1.7 |
| minds14_en_clean_01.wav | en | clean | tiny | ✓ | ✓ | auto | 58.33% | 60.47% | 0.139 | 1.5 |
| minds14_en_noisy_01.wav | en | noisy | tiny | ✓ | ✓ | auto | 58.33% | 55.81% | 0.228 | 2.5 |
| minds14_en_clean_02.wav | en | clean | tiny | ✓ | ✓ | auto | 73.33% | 57.14% | 0.231 | 1.5 |
| minds14_en_noisy_02.wav | en | noisy | tiny | ✓ | ✓ | auto | 146.67% | 98.21% | 0.239 | 1.6 |
| minds14_en_clean_03.wav | en | clean | tiny | ✓ | ✓ | auto | 57.78% | 64.67% | 0.092 | 2.2 |
| minds14_en_noisy_03.wav | en | noisy | tiny | ✓ | ✓ | auto | 60.00% | 66.67% | 0.098 | 2.4 |
| minds14_en_clean_04.wav | en | clean | tiny | ✓ | ✓ | auto | 71.43% | 29.17% | 0.428 | 1.4 |
| minds14_en_noisy_04.wav | en | noisy | tiny | ✓ | ✓ | auto | 85.71% | 54.17% | 0.431 | 1.4 |
| minds14_en_clean_05.wav | en | clean | tiny | ✓ | ✓ | auto | 20.00% | 20.59% | 0.365 | 1.4 |
| minds14_en_clean_06.wav | en | clean | tiny | ✓ | ✓ | auto | 14.29% | 13.04% | 0.309 | 1.4 |
| minds14_en_clean_07.wav | en | clean | tiny | ✓ | ✓ | auto | 63.64% | 34.78% | 0.247 | 1.4 |
| minds14_en_clean_08.wav | en | clean | tiny | ✓ | ✓ | auto | 12.50% | 11.11% | 0.177 | 1.5 |
| minds14_fr_clean_01.wav | fr | clean | tiny | ✓ | ✓ | auto | 60.00% | 40.74% | 0.345 | 1.3 |
| minds14_fr_noisy_01.wav | fr | noisy | tiny | ✓ | ✓ | auto | 100.00% | 88.89% | 0.786 | 3.0 |
| minds14_fr_clean_02.wav | fr | clean | tiny | ✓ | ✓ | auto | 40.00% | 3.12% | 0.298 | 1.4 |
| minds14_fr_noisy_02.wav | fr | noisy | tiny | ✓ | ✓ | auto | 120.00% | 100.00% | 1.071 | 5.1 |
| minds14_fr_clean_03.wav | fr | clean | tiny | ✓ | ✓ | auto | 118.18% | 83.33% | 0.201 | 3.0 |
| minds14_fr_noisy_03.wav | fr | noisy | tiny | ✓ | ✓ | auto | 100.00% | 100.00% | 0.366 | 5.4 |
| minds14_fr_clean_04.wav | fr | clean | tiny | ✓ | ✓ | auto | 60.00% | 46.88% | 0.381 | 1.4 |
| minds14_fr_noisy_04.wav | fr | noisy | tiny | ✓ | ✓ | auto | 100.00% | 78.12% | 1.089 | 3.9 |
| minds14_fr_clean_05.wav | fr | clean | tiny | ✓ | ✓ | auto | 50.00% | 36.00% | 0.401 | 1.3 |
| minds14_fr_clean_06.wav | fr | clean | tiny | ✓ | ✓ | auto | 50.00% | 9.68% | 0.320 | 1.3 |
| minds14_fr_clean_07.wav | fr | clean | tiny | ✓ | ✓ | auto | 100.00% | 100.00% | 0.604 | 3.4 |
| minds14_fr_clean_08.wav | fr | clean | tiny | ✓ | ✓ | auto | 0.00% | 0.00% | 0.298 | 1.3 |
| minds14_de_clean_01.wav | de | clean | tiny | ✓ | ✓ | auto | 112.50% | 71.79% | 0.796 | 4.7 |
| minds14_de_noisy_01.wav | de | noisy | tiny | ✓ | ✓ | auto | 87.50% | 71.79% | 0.585 | 3.4 |
| minds14_de_clean_02.wav | de | clean | tiny | ✓ | ✓ | auto | 65.00% | 36.46% | 0.158 | 2.1 |
| minds14_de_noisy_02.wav | de | noisy | tiny | ✓ | ✓ | auto | 107.50% | 76.80% | 0.145 | 1.9 |
| minds14_de_clean_03.wav | de | clean | tiny | ✓ | ✓ | auto | 35.71% | 19.35% | 0.193 | 1.7 |
| minds14_de_noisy_03.wav | de | noisy | tiny | ✓ | ✓ | auto | 42.86% | 27.42% | 0.183 | 1.6 |
| minds14_de_clean_04.wav | de | clean | tiny | ✓ | ✓ | auto | 10.00% | 4.76% | 0.441 | 2.4 |
| minds14_de_noisy_04.wav | de | noisy | tiny | ✓ | ✓ | auto | 10.00% | 11.90% | 0.281 | 1.5 |
| minds14_de_clean_05.wav | de | clean | tiny | ✓ | ✓ | auto | 15.38% | 6.78% | 0.141 | 1.9 |
| minds14_de_clean_06.wav | de | clean | tiny | ✓ | ✓ | auto | 15.38% | 9.68% | 0.203 | 1.6 |
| minds14_de_clean_07.wav | de | clean | tiny | ✓ | ✓ | auto | 42.86% | 21.21% | 0.218 | 1.6 |
| minds14_de_clean_08.wav | de | clean | tiny | ✓ | ✓ | auto | 41.67% | 18.42% | 0.141 | 1.9 |
| minds14_en_clean_01.wav | en | clean | tiny | ✓ | ✓ | en | 58.33% | 60.47% | 0.102 | 1.1 |
| minds14_en_noisy_01.wav | en | noisy | tiny | ✓ | ✓ | en | 58.33% | 55.81% | 0.102 | 1.1 |
| minds14_en_clean_02.wav | en | clean | tiny | ✓ | ✓ | en | 73.33% | 57.14% | 0.170 | 1.1 |
| minds14_en_noisy_02.wav | en | noisy | tiny | ✓ | ✓ | en | 146.67% | 98.21% | 0.176 | 1.2 |
| minds14_en_clean_03.wav | en | clean | tiny | ✓ | ✓ | en | 57.78% | 64.67% | 0.085 | 2.0 |
| minds14_en_noisy_03.wav | en | noisy | tiny | ✓ | ✓ | en | 60.00% | 66.67% | 0.083 | 2.0 |
| minds14_en_clean_04.wav | en | clean | tiny | ✓ | ✓ | en | 71.43% | 29.17% | 0.286 | 0.9 |
| minds14_en_noisy_04.wav | en | noisy | tiny | ✓ | ✓ | en | 85.71% | 54.17% | 0.283 | 0.9 |
| minds14_en_clean_05.wav | en | clean | tiny | ✓ | ✓ | en | 20.00% | 20.59% | 0.241 | 0.9 |
| minds14_en_clean_06.wav | en | clean | tiny | ✓ | ✓ | en | 14.29% | 13.04% | 0.185 | 0.8 |
| minds14_en_clean_07.wav | en | clean | tiny | ✓ | ✓ | en | 63.64% | 34.78% | 0.162 | 0.9 |
| minds14_en_clean_08.wav | en | clean | tiny | ✓ | ✓ | en | 12.50% | 11.11% | 0.122 | 1.0 |
| minds14_fr_clean_01.wav | fr | clean | tiny | ✓ | ✓ | fr | 60.00% | 40.74% | 0.231 | 0.9 |
| minds14_fr_noisy_01.wav | fr | noisy | tiny | ✓ | ✓ | fr | 80.00% | 74.07% | 0.700 | 2.6 |
| minds14_fr_clean_02.wav | fr | clean | tiny | ✓ | ✓ | fr | 40.00% | 3.12% | 0.199 | 0.9 |
| minds14_fr_noisy_02.wav | fr | noisy | tiny | ✓ | ✓ | fr | 80.00% | 43.75% | 0.188 | 0.9 |
| minds14_fr_clean_03.wav | fr | clean | tiny | ✓ | ✓ | fr | 118.18% | 83.33% | 0.172 | 2.5 |
| minds14_fr_noisy_03.wav | fr | noisy | tiny | ✓ | ✓ | fr | 113.64% | 81.37% | 0.406 | 6.0 |
| minds14_fr_clean_04.wav | fr | clean | tiny | ✓ | ✓ | fr | 60.00% | 46.88% | 0.260 | 0.9 |
| minds14_fr_noisy_04.wav | fr | noisy | tiny | ✓ | ✓ | fr | 160.00% | 81.25% | 1.106 | 4.0 |
| minds14_fr_clean_05.wav | fr | clean | tiny | ✓ | ✓ | fr | 50.00% | 36.00% | 0.281 | 0.9 |
| minds14_fr_clean_06.wav | fr | clean | tiny | ✓ | ✓ | fr | 50.00% | 9.68% | 0.214 | 0.9 |
| minds14_fr_clean_07.wav | fr | clean | tiny | ✓ | ✓ | fr | 85.71% | 55.56% | 0.587 | 3.3 |
| minds14_fr_clean_08.wav | fr | clean | tiny | ✓ | ✓ | fr | 0.00% | 0.00% | 0.186 | 0.8 |
| minds14_de_clean_01.wav | de | clean | tiny | ✓ | ✓ | de | 75.00% | 58.97% | 0.526 | 3.1 |
| minds14_de_noisy_01.wav | de | noisy | tiny | ✓ | ✓ | de | 87.50% | 71.79% | 0.525 | 3.1 |
| minds14_de_clean_02.wav | de | clean | tiny | ✓ | ✓ | de | 65.00% | 36.46% | 0.122 | 1.6 |
| minds14_de_noisy_02.wav | de | noisy | tiny | ✓ | ✓ | de | 85.00% | 69.61% | 0.401 | 5.4 |
| minds14_de_clean_03.wav | de | clean | tiny | ✓ | ✓ | de | 35.71% | 19.35% | 0.119 | 1.0 |
| minds14_de_noisy_03.wav | de | noisy | tiny | ✓ | ✓ | de | 42.86% | 27.42% | 0.115 | 1.0 |
| minds14_de_clean_04.wav | de | clean | tiny | ✓ | ✓ | de | 10.00% | 4.76% | 0.170 | 0.9 |
| minds14_de_noisy_04.wav | de | noisy | tiny | ✓ | ✓ | de | 10.00% | 11.90% | 0.398 | 2.1 |
| minds14_de_clean_05.wav | de | clean | tiny | ✓ | ✓ | de | 15.38% | 6.78% | 0.092 | 1.2 |
| minds14_de_clean_06.wav | de | clean | tiny | ✓ | ✓ | de | 15.38% | 9.68% | 0.124 | 0.9 |
| minds14_de_clean_07.wav | de | clean | tiny | ✓ | ✓ | de | 42.86% | 21.21% | 0.139 | 1.0 |
| minds14_de_clean_08.wav | de | clean | tiny | ✓ | ✓ | de | 41.67% | 18.42% | 0.092 | 1.2 |
| minds14_en_clean_01.wav | en | clean | base | ✓ | ✗ | auto | 58.33% | 60.47% | 0.445 | 4.8 |
| minds14_en_noisy_01.wav | en | noisy | base | ✓ | ✗ | auto | 58.33% | 60.47% | 0.253 | 2.7 |
| minds14_en_clean_02.wav | en | clean | base | ✓ | ✗ | auto | 80.00% | 66.07% | 0.429 | 2.9 |
| minds14_en_noisy_02.wav | en | noisy | base | ✓ | ✗ | auto | 120.00% | 91.07% | 1.083 | 7.2 |
| minds14_en_clean_03.wav | en | clean | base | ✓ | ✗ | auto | 55.56% | 62.67% | 0.182 | 4.4 |
| minds14_en_noisy_03.wav | en | noisy | base | ✓ | ✗ | auto | 62.22% | 65.33% | 0.181 | 4.4 |
| minds14_en_clean_04.wav | en | clean | base | ✓ | ✗ | auto | 0.00% | 0.00% | 1.062 | 3.4 |
| minds14_en_noisy_04.wav | en | noisy | base | ✓ | ✗ | auto | 14.29% | 12.50% | 0.811 | 2.6 |
| minds14_en_clean_05.wav | en | clean | base | ✓ | ✗ | auto | 30.00% | 17.65% | 0.623 | 2.4 |
| minds14_en_clean_06.wav | en | clean | base | ✓ | ✗ | auto | 14.29% | 13.04% | 0.527 | 2.4 |
| minds14_en_clean_07.wav | en | clean | base | ✓ | ✗ | auto | 72.73% | 50.00% | 0.428 | 2.5 |
| minds14_en_clean_08.wav | en | clean | base | ✓ | ✗ | auto | 6.25% | 3.70% | 0.322 | 2.8 |
| minds14_fr_clean_01.wav | fr | clean | base | ✓ | ✗ | auto | 0.00% | 0.00% | 0.639 | 2.4 |
| minds14_fr_noisy_01.wav | fr | noisy | base | ✓ | ✗ | auto | 120.00% | 62.96% | 0.647 | 2.4 |
| minds14_fr_clean_02.wav | fr | clean | base | ✓ | ✗ | auto | 0.00% | 0.00% | 0.499 | 2.4 |
| minds14_fr_noisy_02.wav | fr | noisy | base | ✓ | ✗ | auto | 100.00% | 71.88% | 1.275 | 6.1 |
| minds14_fr_clean_03.wav | fr | clean | base | ✓ | ✗ | auto | 95.45% | 68.63% | 0.237 | 3.5 |
| minds14_fr_noisy_03.wav | fr | noisy | base | ✓ | ✗ | auto | 150.00% | 100.98% | 0.348 | 5.1 |
| minds14_fr_clean_04.wav | fr | clean | base | ✓ | ✗ | auto | 60.00% | 28.12% | 0.734 | 2.6 |
| minds14_fr_noisy_04.wav | fr | noisy | base | ✓ | ✗ | auto | 180.00% | 100.00% | 2.877 | 10.3 |
| minds14_fr_clean_05.wav | fr | clean | base | ✓ | ✗ | auto | 0.00% | 0.00% | 0.769 | 2.6 |
| minds14_fr_clean_06.wav | fr | clean | base | ✓ | ✗ | auto | 50.00% | 12.90% | 0.609 | 2.4 |
| minds14_fr_clean_07.wav | fr | clean | base | ✓ | ✗ | auto | 14.29% | 8.33% | 0.432 | 2.4 |
| minds14_fr_clean_08.wav | fr | clean | base | ✓ | ✗ | auto | 0.00% | 0.00% | 0.592 | 2.6 |
| minds14_de_clean_01.wav | de | clean | base | ✓ | ✗ | auto | 100.00% | 46.15% | 1.073 | 6.3 |
| minds14_de_noisy_01.wav | de | noisy | base | ✓ | ✗ | auto | 37.50% | 33.33% | 1.236 | 7.2 |
| minds14_de_clean_02.wav | de | clean | base | ✓ | ✗ | auto | 42.50% | 29.28% | 0.275 | 3.7 |
| minds14_de_noisy_02.wav | de | noisy | base | ✓ | ✗ | auto | 70.00% | 54.70% | 1.140 | 15.3 |
| minds14_de_clean_03.wav | de | clean | base | ✓ | ✗ | auto | 14.29% | 4.84% | 0.327 | 2.8 |
| minds14_de_noisy_03.wav | de | noisy | base | ✓ | ✗ | auto | 28.57% | 14.52% | 0.354 | 3.0 |
| minds14_de_clean_04.wav | de | clean | base | ✓ | ✗ | auto | 0.00% | 0.00% | 0.546 | 2.9 |
| minds14_de_noisy_04.wav | de | noisy | base | ✓ | ✗ | auto | 10.00% | 7.14% | 0.713 | 3.8 |
| minds14_de_clean_05.wav | de | clean | base | ✓ | ✗ | auto | 19.23% | 7.63% | 0.233 | 3.1 |
| minds14_de_clean_06.wav | de | clean | base | ✓ | ✗ | auto | 23.08% | 6.45% | 0.362 | 2.8 |
| minds14_de_clean_07.wav | de | clean | base | ✓ | ✗ | auto | 28.57% | 27.27% | 0.372 | 2.6 |
| minds14_de_clean_08.wav | de | clean | base | ✓ | ✗ | auto | 25.00% | 22.81% | 0.213 | 2.9 |

---

## 4. Aggregated Results by Condition

| Condition | Model | n | Mean WER | Mean CER | Mean RTF |
|---|---|---|---|---|---|
| A_baseline | tiny | 36 | 63.4% | 43.6% | 0.323 |
| B_noise_reduction | tiny | 36 | 62.2% | 44.6% | 0.372 |
| D_domain_prompt | tiny | 36 | 61.3% | 45.2% | 0.351 |
| E_forced_language | tiny | 36 | 59.6% | 41.1% | 0.260 |
| F_model_base | base | 36 | 48.3% | 33.6% | 0.635 |

### By Condition × Noise Type

| Condition | Clean WER | Clean CER | Noisy WER | Noisy CER |
|---|---|---|---|---|
| A_baseline | 47.0% | 29.7% | 96.4% | 71.3% |
| B_noise_reduction | 49.2% | 32.4% | 88.1% | 68.8% |
| D_domain_prompt | 49.5% | 33.3% | 84.9% | 69.1% |
| E_forced_language | 47.3% | 30.9% | 84.1% | 61.3% |
| F_model_base | 32.9% | 22.3% | 79.2% | 56.2% |

### By Condition × Language

| Condition | EN WER | FR WER | DE WER |
|---|---|---|---|
| A_baseline | 69.6% | 69.1% | 51.6% |
| B_noise_reduction | 64.3% | 73.3% | 48.9% |
| D_domain_prompt | 60.2% | 74.8% | 48.9% |
| E_forced_language | 60.2% | 74.8% | 43.9% |
| F_model_base | 47.7% | 64.1% | 33.2% |

### Throughput

RTF < 1 (faster than real-time) on **169/180 runs (93.9%)**. Mean RTF: tiny = 0.326 (n=144), base = 0.635 (n=36) — base is ~1.9× slower than tiny on this CPU-only, int8-quantized hardware, but still faster than real-time on the vast majority of clips.

---

## 5. Key Findings

These findings are read directly off the table above and cross-checked against the raw per-file transcripts in `results/transcripts/`; nothing here is asserted without a number behind it.

1. **Noise is the dominant error driver, by far.** Across every condition, WER roughly doubles from clean to noisy audio (e.g. baseline 47.0% → 96.4%). This is a far bigger effect than any of the preprocessing/prompting/model choices tested below, and directly supports the thesis's framing of noise robustness as the central challenge (outline's own "SNR below 10 dB" threshold was used to generate the noisy variants here, at 8 dB).

2. **Noise reduction (noisereduce) helps on noisy audio, costs a little on clean audio.** B vs A: noisy WER improves 96.4% → 88.1% (−8.3 pts), but clean WER slightly worsens 47.0% → 49.2% (+2.2 pts). Net effect across the full set is a small improvement (63.4% → 62.2% mean WER) — consistent with spectral-subtraction-style denoising trading a little fidelity on already-clean signal for resilience under noise.

3. **The Nestlé domain prompt had negligible net effect on WER, and one observed failure mode.** D vs B: mean WER barely moves (62.2% → 61.3%). This is expected given the test corpus (PolyAI/MInDS-14 banking-intent speech) contains none of the prompted brand vocabulary — the condition could only show whether prompting *hurts* general transcription, not whether it *helps* recognize Nestlé-specific terms (that would require Nestlé-domain audio, which this thesis cannot use for confidentiality reasons; see Limitations). One clip (`minds14_de_noisy_02.wav`) shows the prompt being echoed verbatim into the hallucinated output ("...it's **Nestlé Ghana**, the center of the conference room...") despite the reference having nothing to do with Nestlé — a concrete, citable example of prompt-leakage hallucination under low-confidence (noisy + auto-detect) conditions.

4. **Automatic language detection is unreliable for short, noisy, non-English clips — and fails catastrophically for French in this sample.** Comparing auto-detect (D) against forced-correct-language (E) on identical audio: **English transcripts were byte-identical in 12/12 cases (0% mismatch)**; **German differed in 2/12 cases (~17%)**; **French differed in 5/12 cases (~42%)**. The French mismatches are not subtle — auto-detection produced hallucinated output in entirely wrong scripts (Chinese characters, Cyrillic, Hebrew, Turkish) on short noisy French clips, e.g. reference *"bonjour je voudrais changer d'adresse"* was auto-transcribed as *"Боже, будь, дай, дай, дай, дай."* Forcing `language="fr"` recovered at least partially-correct French output in every one of these cases. This is the single strongest, most defensible finding in this pilot and a strong empirical argument for forcing language per-speaker/per-channel in a multilingual corporate deployment rather than relying on auto-detection.

5. **Model size (tiny → base) gives a consistent, meaningful accuracy gain at a real but bounded latency cost.** F vs B (same preprocessing, no prompt): mean WER 62.2% → 48.3% (−13.9 pts), CER 44.6% → 33.6%, improvement holds across clean (49.2%→32.9%) and noisy (88.1%→79.2%) and across all three languages. RTF roughly doubles (0.372 → 0.635) but remains < 1 (faster than real time) on the large majority of clips. This is a genuine, measured accuracy/latency trade-off curve point — small/medium/large-v2 were not run here due to CPU-only sandbox constraints (no GPU available in this environment); the trend (larger model → lower WER, higher RTF) is established but its continuation to larger sizes is extrapolated, not measured.

6. **Absolute WER levels (47–96%) are high relative to typical Whisper benchmarks**, but this is expected and not a sign of a broken pipeline: MInDS-14 is real spontaneous **8 kHz telephone-quality** speech (not studio-quality read speech like LibriSpeech), the models used are the two smallest Whisper sizes (tiny/base), and the "noisy" condition adds aggressive 8 dB SNR white noise on top. Spot-checking transcripts (`results/transcripts/`) confirms the errors are real ASR mistakes (e.g. "bank" → "bake", "einzuzahlen" → "einzuzeilen", trailing hallucinated continuations on short clips) rather than pipeline failures — 0 of 180 runs errored or produced NaN metrics.

---

## 6. Limitations (honestly reported)

- **Condition C (VAD) is not implemented.** `backend/stt/engine.py` defines `load_vad_model()` (Silero VAD) but `transcribe_file()` never calls it — VAD-based segmentation is not actually wired into the transcription path despite being part of the outline's experimental design. This pilot reports its absence rather than fabricating a result for it. Wiring it in is a discrete, scoped piece of follow-up engineering, not a research finding.
- **Detected language is not logged.** `EvalResult` (in `backend/evaluation/runner.py`) does not persist faster-whisper's detected `info.language` — only the *requested* `forced_language` is recorded. Finding #4 above was therefore obtained indirectly, by diffing hypothesis text between the auto-detect and forced-language conditions on identical audio, rather than by reading a logged detected-language value. A direct fix (logging `info.language` per run) would make this measurement exact rather than inferred; noted here as a concrete improvement to the evaluation harness itself.
- **Substitute dataset.** The project's own `datasets/stt_eval/README.md` recommends Common Voice or LibriSpeech and explicitly prohibits committing real Nestlé recordings. Common Voice/LibriSpeech/FLEURS/VoxPopuli all proved impractical to sample quickly in this sandbox (streaming hangs, multi-hundred-MB parquet shards without row-level indices). **PolyAI/MInDS-14** (CC-BY-4.0, real telephone-banking speech, en-US/fr-FR/de-DE, genuine transcripts) was used instead — real spontaneous speech, not synthetic, but not Nestlé-domain content, which is precisely why Finding #3 (domain prompt) is inconclusive on its intended question.
- **Noisy condition is synthetic.** The "noisy" variants are clean recordings with Gaussian white noise added at a controlled 8 dB SNR, not field recordings of an actual noisy meeting room. White noise is a conservative, well-understood proxy but does not capture babble noise, reverberation, or device artifacts typical of real corporate meeting rooms.
- **Sample size.** 36 base clips (12/language) is a pilot-scale sample, consistent with the outline's own "pilot scope: 5–10 files" framing for comparable Azure work — sufficient to establish real, directional findings (as above) but not to claim tight statistical confidence intervals.
- **Single run per condition per file** (no repeated trials) — RTF in particular can vary with sandbox CPU contention; reported RTF values should be read as indicative, not laboratory-precise.
- **A real bug was found and fixed in the codebase during this evaluation:** `backend/stt/engine.py` had `import torch` nested inside the `try/except ImportError` block for `pyannote.audio`, which would raise `NameError` on `torch.cuda.is_available()` inside `load_model()` whenever pyannote.audio was not installed. Fixed by moving `import torch` outside the try/except.

---

## 7. Thesis Interpretation

This pilot constitutes a **real, reproducible empirical foundation** for Topic 2's Results chapter — every number above comes from an actual faster-whisper transcription run against real or controllably-synthetic audio with genuine reference transcripts, not from a single recycled PoC anecdote.

It directly supports: noise robustness as the central problem (Finding 1), a measured (not assumed) benefit of noise reduction preprocessing (Finding 2), a properly caveated and honest treatment of domain-vocabulary prompting given the dataset constraint (Finding 3), a strong and specific argument for forced-language configuration in multilingual deployments (Finding 4 — arguably the standout result), and a real accuracy/latency trade-off curve for model-size selection (Finding 5).

It also surfaces two concrete, scoped engineering gaps (VAD not wired in; detected language not logged) that belong in the thesis's Limitations/Future Work section as honest, specific statements rather than vague caveats — which is itself a defensible academic posture.

**Next step:** use this dataset and these numbers as the factual basis for rewriting Chapter 6 ("Results and Analysis") as part of the broader 45–50 page thesis rewrite, replacing the previous draft's single recycled PoC measurement.