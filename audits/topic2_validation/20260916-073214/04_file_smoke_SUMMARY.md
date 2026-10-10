# 04 File path: real inference (model small, app default config)

Scope: transcribe_file(path, forced_language=...) exactly as /transcribe calls it. 
preprocessing=True, Nestlé domain_prompt=True, vad=False. No HTTP, no diarization, no browser.


## gpu_fp16: model=small device=cuda compute_type=float16 (cuda_available=True, load 3.15 s)

| file | mode | detected | WER | CER | audio s | engine s | wall s | RTF(wall) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| minds14_en_clean_01 | auto | en | 0.5833 | 0.6047 | 10.837 | 1.3983347415924072 | 1.4 | 0.129 |
| minds14_en_clean_01 | forced | en | 0.5833 | 0.6047 | 10.837 | 0.7696065902709961 | 0.771 | 0.071 |
| minds14_fr_clean_01 | auto | fr | 0.0 | 0.0 | 3.755 | 0.6015501022338867 | 0.604 | 0.161 |
| minds14_fr_clean_01 | forced | fr | 0.0 | 0.0 | 3.755 | 0.5277194976806641 | 0.529 | 0.141 |
| minds14_de_clean_01 | auto | de | 0.125 | 0.1026 | 5.851 | 0.6703925132751465 | 0.671 | 0.115 |
| minds14_de_clean_01 | forced | de | 0.125 | 0.1026 | 5.851 | 0.6271469593048096 | 0.628 | 0.107 |
| minds14_fr_noisy_01 | auto | fr | 0.2 | 0.1852 | 3.755 | 0.5980849266052246 | 0.599 | 0.16 |
| minds14_fr_noisy_01 | forced | fr | 0.2 | 0.1852 | 3.755 | 0.6051831245422363 | 0.607 | 0.162 |
| minds14_de_noisy_01 | auto | de | 0.5 | 0.3846 | 5.851 | 0.8061656951904297 | 0.808 | 0.138 |
| minds14_de_noisy_01 | forced | de | 0.5 | 0.3846 | 5.851 | 0.8132193088531494 | 0.815 | 0.139 |

mean wall auto=0.82s forced=0.67s; RTF(wall) min=0.071 max=0.162; detection correct on 5/5 auto runs

UTF-8 check: DE hypothesis stored as bytes c3 b6 ('ö') — correct; any '?' in console output is a cp1252 display artefact.

## cpu_int8: model=small device=cpu compute_type=int8 (cuda_available=True, load 1.97 s)

| file | mode | detected | WER | CER | audio s | engine s | wall s | RTF(wall) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| minds14_en_clean_01 | auto | en | 0.5833 | 0.6047 | 10.837 | 6.625891208648682 | 6.627 | 0.611 |
| minds14_en_clean_01 | forced | en | 0.5833 | 0.6047 | 10.837 | 3.9104056358337402 | 3.912 | 0.361 |
| minds14_fr_clean_01 | auto | fr | 0.0 | 0.0 | 3.755 | 6.538260459899902 | 6.539 | 1.742 |
| minds14_fr_clean_01 | forced | fr | 0.0 | 0.0 | 3.755 | 3.2775309085845947 | 3.279 | 0.873 |
| minds14_de_clean_01 | auto | de | 0.125 | 0.1026 | 5.851 | 5.757085561752319 | 5.759 | 0.984 |
| minds14_de_clean_01 | forced | de | 0.125 | 0.1026 | 5.851 | 3.6159136295318604 | 3.617 | 0.618 |
| minds14_fr_noisy_01 | auto | fr | 0.2 | 0.1852 | 3.755 | 5.5710976123809814 | 5.572 | 1.484 |
| minds14_fr_noisy_01 | forced | fr | 0.2 | 0.1852 | 3.755 | 3.211911916732788 | 3.214 | 0.856 |
| minds14_de_noisy_01 | auto | de | 0.5 | 0.3846 | 5.851 | 5.518336057662964 | 5.519 | 0.943 |
| minds14_de_noisy_01 | forced | de | 0.5 | 0.3846 | 5.851 | 3.450151205062866 | 3.454 | 0.59 |

mean wall auto=6.00s forced=3.50s; RTF(wall) min=0.361 max=1.742; detection correct on 5/5 auto runs

UTF-8 check: DE hypothesis stored as bytes c3 b6 ('ö') — correct; any '?' in console output is a cp1252 display artefact.

## Observations

- Transcription works end to end on both backends; hypotheses identical across GPU/float16 and CPU/int8 on these 5 clips.
- With `small`, auto language detection was correct on all 5 clips; forcing changed no text. This does NOT contradict H4, which was measured on `tiny`: it means the effect is model-size dependent and must not be claimed for `small` without more clips.
- `minds14_en_clean_01`: hypothesis ends with 'How do I proceed…' absent from the reference, on both backends and both modes. Same as the morning smoke. **Reference must be checked by listening** (audit item 14) before any conclusion. Human task.
- Nestlé domain prompt was active (app default) on every run; no prompt leakage observed on these 5 clips. Not a general result.
- CPU/int8: auto mode ~2x wall time of forced mode (language detection pass). GPU: difference small.
- RTF here is wall-clock around the whole call (preprocessing + decode), excluding model load; it is not comparable to the manuscript's CPU RTF column without checking that column's scope.
