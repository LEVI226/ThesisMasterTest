# Topic 2 validation — run 20260916-073214 — SUMMARY

Commit `f62705a`, branch `main`, dirty tree (see 00_inventory.md).
Historical CSVs, transcripts and the manuscript were **not modified**
(`results/live_latency.csv` sha256 `25edc394…` verified unchanged after every live run).

Statuses: **verified** · **contradicted** · **partially verified** · **not tested** · **blocked**.
A software fix is never a scientific validation; the two are kept apart below.

## A. Software contracts (steps 1–3, plus logging from step 4)

| Claim | Before | After | Proof |
|---|---|---|---|
| Language chosen in the upload menu is forced | **contradicted** — form field ignored, engine received `None` | **verified** (contract) — form and query both forwarded | 01_repro_defects_BEFORE/AFTER.json; 3 tests |
| Audio the server has received is transcribed when the user stops | **contradicted** — 32 000 B pending, 0 calls (contract); 0/6 delivered on real audio cut mid-speech | **verified server-side** — 6/6 delivered, `flushed` ack on `__end__`, flush on bare disconnect. Browser-side residual (< 1 packet) and slow decodes (> 2 s) not yet covered — see B4 | 05b_live_flush_before_after.json; 4 tests |
| Each run's transcript side file is unique | **contradicted** for the historical campaign: 72 shared paths, 219 rows whose stored hypothesis ≠ file on disk | **verified** for new runs (model + VAD in the name; `TRANSCRIPT_DIR` overridable). History left as is; CSV text columns remain authoritative | 01_repro_defects_*.json; 3 tests |
| The live path records what actually ran | impossible — device/precision not stored, one hard-coded CSV | **verified** — per-session JSONL: model, device, compute_type, versions, options, packets, trigger, latency, text, skips, errors; `LIVE_LATENCY_CSV` per session | backend/stt/session_log.py; sessions/*.jsonl; 2 tests |
| CPU/int8 can be selected explicitly when CUDA is present | impossible (engine always picked CUDA) | **verified** — `STT_DEVICE`/`STT_COMPUTE_TYPE`; `get_model_info()` reports `cpu/int8` with `cuda_available=True` | 04_file_smoke_cpu_int8.json |

Test suite: **66 passed** (51 existing + 15 new), 0 failed. Diff: 02_fixes.diff + round 4 (browser residual/ack on both live interfaces) + startup/health report what is actually loaded.

## B. Scientific / behavioural claims (real inference, bounded)

| Proposal expectation | Exact test | Proof file | Result | Limit | Status |
|---|---|---|---|---|---|
| ASR transcribes multilingual speech (file path) | `transcribe_file` as `/transcribe` calls it; `small`; 5 clips en/fr/de clean+noisy; auto and forced | 04_file_smoke_gpu_fp16.json, _cpu_int8.json | works on both backends; identical hypotheses; WER fr 0.0/0.2, de 0.125/0.5, en 0.583 | 5 clips; app default config (Nestlé prompt ON); no HTTP | **verified (bounded)** |
| Auto language detection is reliable | same | same | correct 5/5 with `small` on the file path | `small` only; tiny showed failures this morning | **partially verified** — size dependent |
| Forcing the language repairs wrong-language output (H4) | live handler, German clip, auto vs `lang=de` | 05_live_sim.json | auto → detected `no` p=0.32, WER 1.0 garbage; forced `de` → WER 0.125 | 1 clip; live path only (file path already detected `de`) | **verified on the live path, 1 clip** |
| File-path scores transfer to the live path | same German clip through both paths | 04_* vs 05_* | file: `de`, WER 0.125 · live: `no`, WER 1.0 | 1 clip | **contradicted** — do not transpose (audit item 5 demonstrated) |
| Live server-side latency ≈ 0.56 s median | 32 utterances, GPU float16, `small`, fake socket | live_latency_validation.csv, sessions/ | median 0.304 s, p95 0.467 s, max 0.703 s | no network, no browser, no mic; ~2–4 s utterances | **partially verified** — server-side only, consistent with manuscript order of magnitude |
| Nestlé prompt active on the file path, no leakage | app default | 04_* | prompt ON by default; no leakage on 5 clips | 5 clips | **partially verified** — not a general result |
| LoRA adapter active in the application | code reading | engine.py, main.py | no LoRA load anywhere in the app engine | — | **verified as absent** — must not be announced as active |
| Speaker diarization works | — | — | pipeline not loaded in these runs; torchcodec DLLs missing | — | **not tested** |
| `minds14_en_clean_01` reference is complete | model output vs reference, 4 configurations | 04_*, 05_* | every configuration adds "How do I proceed…" after the reference text | listened by the author | **contradicted** — see B3 |
| Real-time transcription in simulated Teams meetings | — | — | — | — | **not tested** |
| Meetings with real speaker identities (T1) | — | — | — | — | **not tested** |
| Domain vocabulary adaptation on Nestlé terms (T2) | — | — | — | — | **not tested** |

## B2. Microphone tests (human voice, live path, `small` cuda/float16, diarization unavailable)

| Claim | Status | Evidence |
|---|---|---|
| Full sentence reaches the screen (FR, native) | **verified** — 6/7 exact, 1 word error | mic/FINDINGS_1.md |
| Stop button sends `__end__`, server flushes | **verified end-to-end** | mic/sessions, session 1–2 |
| Live UI lets the user force the language | **contradicted, then fixed** — no selector existed; all first sessions ran auto | frontend `liveLang` added |
| Forced language repairs wrong-script output on accented German (H4) | **verified** — auto: Latin/IPA/EN/NN, CER 0.64; forced `de`: German only, CER 0.37 | mic/FINDINGS_2.md |
| Lower live latency observed with forced language on accented speech | **observed in these trials** (7 vs 3 productions of the same sentence, not the same recordings; order, pronunciation and warm-up uncontrolled) — median 3.25 s → 0.69 s, max 14.2 s → 0.88 s. Not established causality; the historical 11 s maximum cannot be attributed to this mechanism | idem |
| Forced language fixes accent-driven word errors | **contradicted** — "möchte"/"einzahlen" wrong in 3/3 forced runs, WER 0.38–1.00 | idem |
| Live RTF < 1 for every utterance | **contradicted** — 1.18 on one auto-mode utterance (12 s audio, 14.2 s latency) | idem |
| Forced English on a French speaker | **verified** — 4/6 exact, 0.53–1.08 s | session 08:43 |
| Diarization in the running app | **failed to load before 14:02, loads after** — not intermittent: a separate session repaired the environment (lightning 2.4.0, CTranslate2 4.6.0, pyannote file-path call) between my startups; see audits/diarization_20260916/DIAGNOSTIC.md. Loading is verified; attribution accuracy is not | mic/server*.log, diarization_20260916 |
| Flush can hallucinate on 1 s residual audio ("Thank you.") | **observed**, not changed — guard trade-off left to the author | mic/FINDINGS_1.md |

## B4. Stop scenarios on both live interfaces (review 2026-09-16)

| Claim | Status | Evidence |
|---|---|---|
| Browser sends its < 1 s residual before `__end__` (index.html and /live) | **contradicted before** (residual discarded, /live sent no signal) → **fixed**; server side verified (0.4 s residual transcribed) | apply_fixes_4.py; test_residual_packet… |
| Disconnect waits for the flush to finish even when decoding takes > 2 s | **contradicted before** (2 s cap) → **fixed**: close on `flushed` ack, 30 s guard; ack proven to follow a 2.3 s flush | test_flushed_ack_is_sent_only_after… |
| Stop then Disconnect does not duplicate the last utterance | **verified** (server): two `__end__` → one transcription | test_stop_then_disconnect… |
| Text actually displayed in the browser after a slow flush | **verified** (index.html, human) — CPU/int8, two `end_signal` flushes decoded in 5.05 s / 5.03 s, both shown on screen; /live not exercised in a browser | mic/FINDINGS_4.md |
| Startup log / `/health` report unavailability truthfully | **contradicted before** ("✅ Diarization loaded" while None; health reported an env default) → **fixed**: both use `get_model_info()` | main.py lifespan, /health |

## B5. T4 probe — language switch inside one utterance (live path, `small`, auto)

| Pair | Result | Status |
|---|---|---|
| en → fr, no pause | both languages transcribed correctly in one segment (WER 0.08) | **partially contradicts** "does not natively resolve": it sometimes does |
| fr → en, no pause | English half silently **translated into French** | **verified failure mode** — invisible to the reader |
| fr → de | German half garbled into French ("geld"), or Khmer script with a pause | **verified failure mode** — wrong script |
| Limit | 3 pairs, concatenated telephone clips, one model; no human code-switched speech | pilot |

## B6. Real Nestlé audio — AGM 2026 EN, 22 min, file path (09, 09b)

| Claim | Status | Evidence |
|---|---|---|
| Pipeline handles a real 22-min corporate speech | **verified** — 151 s processing, RTF 0.11, GPU | UI pills, file_* session log |
| Domain prompt protects Nestlé vocabulary | **partially contradicted** — 6/6 brands right, 5/9 people's surnames wrong; prompt lists brands only | 09 |
| Multilingual robustness on the file path | **contradicted** — the CEO's French+German opening (16.6 s) silently dropped; large-v3 identical; cause = one language decision on the first 30 s of the file | 09b |
| Live per-utterance decision avoids this | **verified (loudspeaker replay)** — greeting kept, detected `de`; German right, English kept, French garbled through the German token | 09c |
| Live utterance length is bounded | **contradicted** — fluent speech gave a 70 s utterance (silence-triggered, 8.3 s decode) and a 149 s block closed only by the user's Stop (`end_signal`, 13.6 s decode): without that click it would have kept growing. No max length in the handler. Caption delay = utterance length + decode, not the post-trigger latency alone | 09c, session 17:51 |
| UI shows processing time | **fixed** — audio / processed / RTF pills | frontend |

## B3. Reference integrity (human listening, 2026-09-16)

| Claim | Status | Evidence |
|---|---|---|
| The 24 clean MInDS-14 references are correct | **differences found after re-annotation** — 7/16 en+fr clips differ from the published text after the author's listening (en_01, en_03, fr_03 end earlier than the audio; en_02, en_07 differ in wording; en_08, fr_07 differ only in hesitations); not all are established corpus errors, some passages remain uncertain. Noisy twins share the files → **9/36 files, 117/468 rows** for the first five | 07_reference_triage.csv (3-architecture agreement used only to prioritise listening) |
| Absolute WER levels in the manuscript | **affected**; a sensitivity analysis with provisional alternative references moves aggregates by −0 (de Conformer) to −22 pts (en Conformer); overall −10 to −15 on the 36-file conditions. Not a definitive correction | 06b (sensitivity analysis), 117 rescored rows |
| Orderings the manuscript relies on | **order checks hold under provisional references**, with reservations: LoRA and prompt effects change sign (+1.0→−0.1, +0.9→−0.8) so no equivalence is proven; ladder monotonicity is exposed to large-v3 bias; intervals to be recomputed after independent re-annotation | idem, "Order checks" |
| Human re-annotation by the author | **done for 16/24** (all en + fr, 2026-09-16): 7 differ from the published source, 9 confirmed identical; 8 German unverified (no speaker). **Not fully blind**: the author had seen model outputs for the 5 priority clips and a word-level triage for two controls before transcribing. Priority clips listened twice by the same person (3/5 changed between passes; fr_03 tense ambiguous) — a second pass, not an independent validation | reannotation/references_v2/, CHANGELOG, ANNOTATION_NOTES.md |
| Revision v2 (16 human references, 8 German original), clustered 95 % CIs | tiny 50.6 · base 35.5 · small 19.4 · medium 13.2 · large-v3 10.9 (monotone); size +39.9 [26.3, 53.0]; noise +36.9 [7.6, 62.8]; LoRA +0.6 [−1.9, 3.0]; prompt −0.5 [−3.2, 2.1]; **forced language +2.4 [−2.6, 7.0]**; MMS−J0 +5.0 [−1.9, 13.0]. LoRA estimate moved +1.0→−0.1→−0.5→+0.6 across reference versions, every interval containing zero: no benefit established on this sample; equivalence not shown | reannotation/revision_v2/REVISION_v2.md |
| Corrected figures are publishable | **final for en/fr, provisional for de** — as an erratum/revision alongside the original figures, never replacing them | — |
| Provenance | **verified** — all 24 local references identical to the published PolyAI/minds14 `transcription` field (HF cache 2026-07-26); the defects are in the published transcriptions of these 5 clips, not in local extraction. No generalisation to the whole corpus | 06b, Provenance |
| Handling | canonical CSVs and references **kept as scored**; neutral re-annotation sheet prepared (07b); rescoring + intervals in a separate revision once references are validated; supervisor informed with the provisional wording below | — |

## C. What still needs a human

1. A German speaker for the 8 remaining clips (public CC-BY audio: Goethe-Institut Ouagadougou, university language dept, a Nestlé contact, or a freelance transcriber). Optional: a second listener on fr_03 / en_03 / en_07.
2. T1–T6 material (step 7): to be prepared next; T1/T6 need people and Teams, T2 needs Nestlé vocabulary audio with verified references.
3. Decide on the flush hallucination guard. (Startup/health message fixed.)
4. Start-of-recording loss: first words missing when speech begins before the mic is live — to measure in T5.
5. Decide on a maximum utterance length for the live path (fluent speakers never trigger the 0.6 s silence rule).

## D. Files in this run

- 00_inventory.md · 01_repro_defects_{BEFORE,AFTER}.json · 02_fixes.diff · 03_steps_1_to_3.md
- 04_file_smoke_{gpu_fp16,cpu_int8}.{json,csv} · 04_file_smoke_SUMMARY.md · transcripts/
- 05_live_sim.json (fixed) · 05_live_sim_PRISTINE.json · 05b_live_flush_before_after.json (+ .stdout/.stderr)
- live_latency_validation.csv (fixed) · live_latency_validation_PRISTINE.csv · sessions/*.jsonl
- pristine/ (originals of every edited file) · scripts: repro_defects.py, apply_fixes*.py, restore_endings.py, file_smoke.py, live_sim*.py
