# Task 13 Step 1 - DEV smoke report

Branch study/real-meetings. No code changed, nothing committed. Artifacts: results/real_meetings/smoke.csv (190 data rows), logs in results/real_meetings/logs/ (smoke_<system>.log, smoke_mms-1b-all_try1.log, runsys.sh, chain.sh, analyze.py).

## Commands
Per system, one process each, sequential:
`.venv/Scripts/python.exe -m study_real_meetings.scripts.run_experiments --plan ALL --split dev --limit 5 --out results/real_meetings/smoke.csv --system <S>`
(wrapped by logs/runsys.sh for log+wall-clock; chain.sh retried a failing system once).

## Per-system outcome
| system | outcome | rows | wall |
|---|---|---|---|
| whisper-small | OK | 55 | 38 s |
| whisper-large-v3 | OK | 80 | 156 s |
| conformer-ctc-large | OK | 35 | 50 s |
| hf-whisper-small | OK | 10 | 36 s |
| hf-whisper-small-lora | OK | 10 | 20 s |
| mms-1b-all | FAILED twice (CUDA out of memory), 0 rows | 0 | 28 s each |

Peak VRAM not recorded (nvidia-smi showed 0 MiB used before/after, so no other process held GPU memory during the MMS failure).

## MMS crash (both attempts identical)
transcribers.py line 137 (transcribe) -> torch -> transformers wav2vec2 `modeling_wav2vec2.py` feature-extractor conv_layer -> activation: `RuntimeError: CUDA error: out of memory`. It fails on the first segment (agm de, ~17 s), right after weights load (1096 tensors), in a fresh process with an otherwise empty 8 GB GPU. Full tracebacks: logs/smoke_mms-1b-all_try1.log and logs/smoke_mms-1b-all.log. Not retried further, no code changed.

## Table: system x dataset x condition (corpus WER = sum(sub+del+ins)/sum(n_ref), median rtf; 5 clips each)
```
system                dataset  condition             nref  WER%   rtf
conformer-ctc-large   agm      forced-clean          146   19.2  0.005
                               forced-snr20          146   21.2  0.005
                               forced-snr10          146   22.6  0.005
                               forced-snr5           146   25.3  0.005
                      ami-ihm  forced-clean           17   11.8  0.029
                      ami-sdm  forced-clean           17   64.7  0.033
                      summre   forced-clean           68   41.2  0.054
hf-whisper-small      ami-ihm  forced-clean           17 2600.0  0.149   (one repetition loop, 440 ins on ref "UH")
                      summre   forced-clean           68   32.4  0.224
hf-whisper-small-lora ami-ihm  forced-clean           17   47.1  0.109
                      summre   forced-clean           68   33.8  0.182
whisper-large-v3      agm      forced-clean          146   13.0  0.107
                               forced-clean-prompt   146   29.5  0.129
                               forced-clean-denoise  146   17.1  0.098
                               forced-snr20/10/5     146   13.0/13.0/15.1  0.091/0.096/0.098
                               forced-snr20/10/5-denoise 146 14.4/17.8/17.8 0.13-0.16
                               auto-clean / auto-snr5 146  13.0 / 15.1  0.118/0.113
                      ami-ihm  forced-clean           17   23.5  0.220
                      ami-sdm  forced-clean / auto    17   88.2  0.25/0.39
                      summre   forced-clean / auto    68   35.3  0.45/0.66
whisper-small         agm      forced-clean          146   15.8  0.040
                               forced-snr20/10/5     146   17.1/15.1/19.2  ~0.04
                               auto-clean / auto-snr5 146 15.8 / 19.2 0.042
                      ami-ihm  forced-clean           17   41.2  0.078
                      ami-sdm  forced-clean / auto    17   105.9  0.07/0.11
                      summre   forced-clean / auto    68   38.2  0.12/0.16
```
Noise dataset: no rows for any system (log shows `NOISE <system> noise forced-clean +0`), so mean `ins` per clip cannot be reported.
Wall (sum proc_s): whisper-large-v3 133 s, whisper-small 26 s, hf-whisper-small 16 s, lora 4 s, conformer 4 s.

## Checks
1. Table: above. Totals per system match the CSV (35/10/10/80/55 rows).
2. Plausibility.
 - Language: for every forced-clean row `detected_language == language` (no mismatches). Examples: summre fr hyps are French for all 5 systems; agm hyps German.
 - n_ref > 0 for non-noise rows: FAILED on 10 rows. All are segment `*-EN2002a-FEO070-0002801` (ami-ihm / ami-sdm), reference "UH" - the reference normalises to zero words (filler removed), so n_ref = 0 (WER undefined; any hypothesis words count as insertions). It occurs in every system run on ami. Needs a controller ruling (drop zero-ref segments at sampling, or accept). It also inflates tiny-n ami WERs.
 - noise_type filled only for snr conditions: PASS (0 violations both ways).
 - whisper-large-v3 agm forced-clean WER < 30 %: PASS, 13.0 %.
3. R9 (MMS): NOT VERIFIABLE / FAIL. MMS produced no output (CUDA OOM on the first clip, twice), so no WER for any language. In addition, with `--limit 5` the dev split only provided agm=de, ami=en, summre=fr; there are no agm en/fr clips in this smoke, so the "WER < 60 % on agm forced-clean in each of en/fr/de" check cannot be done with this command even once MMS runs. No hypothesis/reference pairs to show. The controller must rule (memory fix for MMS; and per-language coverage, e.g. a per-language limit).
4. Empty/garbage text: no system is empty everywhere. conformer-ctc-large has 2 empty hyps (the "UH" segment, ami-ihm and ami-sdm). conformer on summre fr prints a mojibake char ("au d�but de ns") in a sample hypothesis, probably only the console/log encoding of "é", to be confirmed in a UTF-8 read. hf-whisper-small and lora each produced one repetition-loop hypothesis on ami-ihm ("Ha ha ha ..." x 440 tokens, ref "UH"). Whisper on ami-sdm is poor (88-106 % WER; e.g. ref "OKAY" -> hyp "Thank you.", ref "UH" -> "Yeah, sorry."), expected for distant mic on 1-5 s clips with n_ref=17.
5. Wall-clock: see per-system table. Peak VRAM not observed.

## Other observations
- Prompt condition roughly doubles whisper-large-v3 WER on agm (29.5 % vs 13.0 %), and denoise worsens it (17.1 %), consistent with the hypotheses being tested but worth a look at the prompt-hallucination examples before freezing.
- Dev sample at limit 5 is tiny (n_ref 17-146); WERs are for plumbing validation only.
