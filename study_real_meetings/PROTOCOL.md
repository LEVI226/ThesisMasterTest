# PROTOCOL: Real-Meetings Validation Study (frozen 2026-10-10)

Frozen at the commit tagged `protocol-frozen` (see `git show protocol-frozen`).

Pre-registration of the study described in `docs/specs/2026-10-10-real-meetings-study-design.md`.
Nothing below may change after the freeze commit; changes go to §9 "Deviations" with date and reason.

## 1. Questions and hypotheses
H1, H2, H3, H4a, H4b, H4c, H4d, H5, D1: exactly as in spec §5.

## 2. Data (manifests checksummed in `manifests.sha256`, written at freeze)
| Manifest | Segments (all / test) | Hours (all / test) | Clusters (all / test) |
|---|---|---|---|
| agm | 236 / 203 | 1.10 / 0.94 | 35 / 32 (2-min blocks per language) |
| ami-ihm | 1454 / 1316 | 1.35 / 1.20 | 16 / 16 (meeting × speaker; meetings EN2002a, ES2004a, IS1009a, TS3003a) |
| ami-sdm | 1454 / 1316 (same utterances as ami-ihm, paired by pair_key) | 1.35 / 1.20 | 16 / 16 |
| summre | 757 / 677 | 1.29 / 1.14 | 12 / 12 (meeting × participant; 018a_EARZ, 032b_EADH, 069c_EEPL) |
| noise | 30 / 30 | 0.08 / 0.08 | 3 / 3 (DEMAND environment) |

Counts computed with `study_real_meetings.manifest.read_manifest` on `datasets/real_meetings/manifests/*.jsonl`:
segments = number of records (test = `split == "test"`); hours = Σ duration / 3600; clusters = number of distinct `cluster` values.
Segmentation: caption/IPU units merged to target 15 s, max 20 s, max gap 2 s, padding 0.15 s.
AMI: official utterances, 1–30 s. Dev = first 180 s of each source cluster; test = the rest.

## 3. Reference quality
AGM FR verbatim rate: 20/20 (minor 0, major 0). AGM EN: 20/20 (minor 0, major 0). Author listening check of 20 seed-drawn test segments per language (results/real_meetings/agm_spotcheck.csv).
The rule that more than 25 % "major" segments would trigger action was pre-declared and is not triggered.
AGM DE: publisher captions, partially verified. Automatic checks (`results/real_meetings/agm_de_caption_checks.csv`, test segments):

| Language | Segments | Words/s | Coverage | Flagged (outside 0.5–4.5 words/s) |
|---|---|---|---|---|
| de | 69 | 1.90 | 0.969 | 0 |
| en | 66 | 1.83 | 0.966 | 1 |
| fr | 68 | 2.19 | 0.997 | 0 |

DE speech rate and coverage are in line with EN/FR and no DE segment is flagged.
The 1 flagged EN segment is agm-en-0014 (245.04–260.8 s, 0.44 words/s, "and resilience. Very well-deserved by our people."); it was inspected as a rate outlier only.
The coverage denominator uses (file duration − 180 s), an approximation of the test window (the R12 boundary differs by less than one segment).
AMI and SUMM-RE: published human gold transcripts.

## 4. Systems and decoding
whisper-small, whisper-large-v3 (faster-whisper 1.2.1, CT2 4.6.0, fp16; beam 5, temperature 0 with
no fallback, condition_on_previous_text=False, no VAD); mms-1b-all (greedy CTC, language adapter);
conformer-ctc-large (NeMo stt_{en,fr,de}_conformer_ctc_large, greedy CTC);
hf-whisper-small and hf-whisper-small-lora (transformers, adapter models/lora_small_minds14, beam 5).
CTC systems always receive the language. Whisper receives it in "forced" conditions only.
Each system label maps to exactly one model configuration (study_real_meetings/transcribers.make_transcriber); changing a model requires a new label or a new results file.
mms-1b-all weights are read with a custom safetensors reader directly to the GPU (same file, same fp16 cast) because the stock loader exhausts host memory on this machine; dev check (R9): AGM forced-clean WER en 13.5 %, fr 18.9 %, de 16.2 %.

## 5. Conditions
Noise: DEMAND OMEETING / OOFFICE / PCAFETER (channel 1), one environment and offset per
(segment, SNR) drawn with seed 20261010; SNR 20 / 10 / 5 dB. Denoising: noisereduce spectral gating
per segment. Prompt: the thesis domain prompt (identical text). Streaming (H5): fixed chunks of
1/2/5/10/20 s, no overlap, no context carry-over.

## 6. Metrics
Primary: corpus WER = Σ(S+D+I)/ΣN, thesis normaliser + filler removal (lists in config.py).
Segments whose reference is empty after normalisation (filler-only, e.g. AMI 'UH') are excluded from all WER aggregates and primary tests and counted per dataset (n_excluded_empty_ref); they remain in runs.csv (ruling R16).
Secondary: WER with the digits→words rule (num2words), CER, Nestlé-term recall (10 terms, config.py),
repetition-loop rate (a 4-gram repeated ≥ 3 times), insertions on noise-only clips, DER
(collar 0.25 s, overlap scored), RTF, streaming latency (p50/p95).

## 7. Statistics
95 % CIs by cluster bootstrap (10 000 resamples, seed 20261010). Primary comparisons (Holm, α = 0.05):
P1–P3 H1 large-v3 vs conformer (AGM forced-clean; de, en, fr) · P4 H2 large-v3 forced-snr10 vs
forced-clean (AGM) · P5 H2 large-v3 SDM vs IHM (AMI, paired by pair_key) · P6 H3 large-v3 AMI-IHM
vs AGM-EN (unpaired) · P7 H3 large-v3 SUMM-RE vs AGM-FR (unpaired) · P8 H4a large-v3 auto vs forced
(AGM snr5 + AMI-SDM + SUMM-RE, pooled) · P9 H4d hf-small-lora vs hf-small (AMI-IHM + SUMM-RE, pooled).
Everything else is exploratory (CIs, no significance claims).
Holm family size is fixed at 9; a comparison that could not be run enters with p = 1.

## 8. Decision rules
H5 operating point: the smallest chunk whose DEV WER is within 1 point (absolute) of the 20 s chunk,
per system; reported on TEST. Stop rule: everything not run by the end of week 2 → "future work".

## 9. Deviations
- 2026-10-10 (planning): D1 on SUMM-RE instead of AMI, reported per meeting without CI; H5 on AGM only;
  DEMAND instead of MUSAN; optional sources (Senate, investor call, YouTube auto-captions) not run
  (reasons: plan "Deviations" section).
- 2026-10-10: H5 dev/test audio boundary = start of the first test segment per language (ruling R12).
- 2026-10-10: one system per Python process (ruling R8).
- 2026-10-10: test-split runs are gated on the git tag `protocol-frozen` (ruling R2).
- 2026-10-10: segments with an empty normalised reference are excluded from WER aggregates and primary tests, counted as n_excluded_empty_ref, kept in runs.csv (ruling R16).
- 2026-10-10: mms-1b-all is loaded with a custom safetensors reader directly to the GPU (same file, same fp16 cast) because the stock loader exhausts host memory.
