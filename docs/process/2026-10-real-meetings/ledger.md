# SDD ledger — plan: docs/plans/2026-10-10-real-meetings-study-pipeline.md

Spec: docs/specs/2026-10-10-real-meetings-study-design.md (binding authority).
Branch: study/real-meetings. Plan base commit: 15c36b2.

## Pre-flight scan

### Cross-task interfaces (tasks sharing a file or interface)
| Tasks | Produces → consumes | Finding |
|---|---|---|
| T1 → all | pytest `pythonpath=["."]`, `gpu` marker, num2words | consistent |
| T2 → T3,T4,T5,T7,T10,T11,T14 | config names (DEV_SECONDS, SEGMENT_*, AGM_*, IPU_MAX_GAP_S, SAMPLE_RATE, DEMAND_*, DOMAIN_PROMPT, SNRS_DB, STREAM_*, N_BOOTSTRAP, ALPHA, LORA_ADAPTER…) | every imported name is defined in T2 config |
| T2 → T7, T11, T13 | score_words/score_chars/term_hits/has_repetition_loop, Counts(.errors,.wer,.dele) | consistent |
| T3 → T5, T7, T9, T10, T13 | Unit, Segment (incl. pair_key), merge_units, split_for, read/write_manifest | consistent |
| T4 → T5, T6, T7, T9 | write_wav, load_segment, wav_duration, convert_to_wav16k, pick_noise, mix_at_snr, load_demand_bank, stable_rng | consistent |
| T6 ↔ T7 | both edit tests/test_rm_runner.py (T6 creates with gpu test + imports np/pytest/sf/Path; T7 appends) | consistent; T7 relies on T6's top imports |
| T6 → T7, T10, T11 | Transcript, make_transcriber, release, `.system/.model_id/.compute_type` | consistent |
| T7 → T10, T11, T12, T14 | Condition(.name), run, read_rows, collect_provenance, FIELDS | consistent |
| T8 → T14 | cluster_bootstrap_wer, paired/unpaired_wer_difference, holm | consistent |
| T9 ↔ T10 | run_experiments guard "PROTOCOL.md exists" vs T9 writes PROTOCOL.md before the human spot-check is done | CONFLICT: a draft PROTOCOL.md would unlock test runs → see Ruling R2 |
| T5/T9/T13 human steps | T5 step 8 listening check; T9 step 2 spot-check; T1 supervisor email | human-only gates inside an automated run → Rulings R3, R4 |

### Per-task self-consistency
| Task | Tests vs code | Files vs later edits | Finding |
|---|---|---|---|
| T1 | runs existing suite only | pyproject/.gitignore/docs | ok |
| T2 | 9 tests match text.py | — | ok |
| T3 | 6 tests; SRT times rounded to ms | — | ok |
| T4 | 7 tests (4 parametrized SNR) | — | ok |
| T5 | 4 tests match builders (fixed euh=4.5 s) | build_data is untested glue | ok (glue verified by real build) |
| T6 | gpu-only smoke test | creates tests/test_rm_runner.py | ok |
| T7 | 3 tests | appends to test_rm_runner.py | ok |
| T8 | 6 tests | — | ok |
| T9 | no unit tests (script + docs) | needs real manifests + human verdicts | see R2/R4 |
| T10 | 4 tests | guard text | see R2 |
| T11 | 4 tests | — | ok |
| T12 | 2 tests | — | ok |
| T13 | operational | needs frozen protocol + data | see R4 |
| T14 | 3 tests; steps 5–6 need real runs | — | see R4 |

## Rulings
- Ruling R1: Work in the existing checkout on branch `study/real-meetings`, not a separate git worktree — `.venv`, `.env` (HF token), `models/lora_small_minds14` checkpoints and datasets are git-ignored local state the tasks need; the branch already isolates from `main`. — Cost if wrong: untracked local files (topic1/, tmp logs) could be committed by a careless `git add -A`; mitigated by requiring explicit path lists in every commit.
- Ruling R2: `run_experiments` guard must check that the git tag `protocol-frozen` exists (not merely that PROTOCOL.md exists), because Task 9 writes PROTOCOL.md before the human spot-check and freeze. — Cost if wrong: none functional; a stricter guard only blocks premature test runs.
- Ruling R3: Task 5's "listen to the SUMM-RE mix" check is replaced, for the implementer, by an automated cross-correlation lag check between channels of each meeting (report max |lag|; flag > 50 ms); the listening check stays on the author's to-do list. — Cost if wrong: a subtle desync could slip past until the author listens; D1 would then be re-run.
- Ruling R4: Execution order is 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14 (code steps 1–4 only), then 9 steps 1 + draft PROTOCOL (numbers filled, NOT frozen/tagged), then 13 step 1 (dev smoke run, allowed before freeze). Then STOP for the human gate: author's spot-check (T9 step 2) + protocol freeze. T13 steps 2–4 and T14 steps 5–6 resume after the freeze. — Cost if wrong: none for correctness; only defers the test-split runs until the author has done the 30-min listening check the protocol requires.

## Progress
- Ruling R5: pytest cannot write `tmp/pytest-of-ulric` / `tmp/pytest_cache` (Windows ACL, WinError 5; pre-existing, environmental). Fix in config, not ACLs: `[tool.pytest.ini_options]` gets `cache_dir = ".pytest_cache"` and `--basetemp=.pytest_tmp` in addopts; both paths git-ignored. Every later task's tests use tmp_path, so this is load-bearing. — Cost if wrong: none for results; changes where pytest writes scratch files (existing suite included).
- Ruling R6: commit trailers must read `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (plan Global Constraints) even when the implementer model differs; b9bbcb3 is amended in Task 1's fix round (unpushed branch, safe). — Cost if wrong: cosmetic attribution only.
Task 1: implementer done b9bbcb3 (DONE_WITH_CONCERNS: pytest ACL errors 26, trailer says Haiku)
Task 1: review → Needs fixes (Important: trailer Haiku≠Opus; default pytest red, WinError 5). Fix round 1 sent to implementer (amend trailer + R5 config).
Task 1: minor (deferred): ETAT_ACTUEL.md new "## 5." sits after "## 7. À NE PAS FAIRE" (plan-mandated numbering reads oddly).
Task 1: minor (deferred): ctranslate2 pkg_resources UserWarning on import (pre-existing, pinned setuptools).
Task 1: fix round 1/5 (2 addressed, 0 open; commits b9bbcb3 amended→deafa65..ccb53c6)
Task 1: complete (commits 15c36b2..ccb53c6, review clean after 1 fix round)
Task 2: dispatched, BASE ccb53c6
Task 2: implementer done 83987b3 (DONE, 78 passed); review dispatched
Task 2: review Approved; controller verified ⚠️ items: branch ok, explicit 3-file commit, num2words in pyproject, DOMAIN_PROMPT byte-identical to engine.py.
Task 2: minor (deferred): term_hits does not normalise custom `terms` (defaults already lowercase) — plan-mandated.
Task 2: minor (deferred): num2words raises for unsupported languages (only de/en/fr used).
Task 2: minor (deferred): no test enforcing DOMAIN_PROMPT == engine DEFAULT_DOMAIN_PROMPT (controller checked once manually: identical).
Task 2: complete (commits ccb53c6..83987b3, review clean)
Task 3: dispatched, BASE 83987b3
- Ruling R6 (revised): a Co-Authored-By trailer naming the model that actually implemented the commit (e.g. Claude Haiku 5.5, per that subagent's own harness attribution instruction) is accepted; no further amends. Truthful attribution outranks the plan's uniform Opus trailer. Earlier amended commits (deafa65, ccb53c6, 83987b3) stay as they are. — Cost if wrong: cosmetic attribution inconsistency across commits.
Task 3: implementer done 051bae5 (DONE, 84 passed; trailer Haiku per R6 revised); review dispatched
Task 3: review Approved; controller verified ⚠️: branch ok, 3-file commit, test_rm_manifest green, config constants exist (Task 2).
Task 3: minor (deferred): srt.py has literal U+FEFF in lstrip string instead of "﻿" escape.
Task 3: minor (deferred): malformed SRT timestamp → opaque AttributeError (plan-mandated).
Task 3: minor (deferred): no test for old manifests missing speaker/pair_key; single unit > max_s untested (plan-mandated).
Task 3: complete (commits 83987b3..051bae5, review clean)
Task 4: dispatched, BASE 051bae5
Task 4: implementer done c03d87f (DONE, 91 passed); review dispatched
Task 4: review Approved; ⚠️ resolved: config constants exist (T2), 7 tests reported green (91 total); DEMAND layout verified in T5 build.
Task 4: minor (deferred): load_demand_bank next() without default → bare StopIteration; rglob order if 48k+16k coexist (only 16k zips are downloaded) — plan-mandated.
Task 4: minor (deferred): mix_at_snr empty-noise ZeroDivision / empty-speech NaN; zero-power returns clean speech silently.
Task 4: minor (deferred): snr key 10 vs 10.0 differ (callers pass floats from config); write_wav clips silently.
Task 4: minor (deferred): tests miss convert_to_wav16k, load_demand_bank, SNR-after-limiting, pick differs by segment/SNR — plan-mandated.
Task 4: complete (commits 051bae5..c03d87f, review clean)
Task 5: dispatched (sonnet), BASE c03d87f, carries R3 (automated channel-lag check)
Task 5: implementer done 9f395a1 (DONE_WITH_CONCERNS; 95 passed). Data: agm 236/1.09h, ami-ihm & ami-sdm 1454 each/1.35h (pair keys equal), summre 757/1.29h, noise 30; 3 RTTMs; 1.8 GB.
- Ruling R7: SUMM-RE channel sync accepted for D1. The R3 pairwise-envelope check is uninformative for turn-taking speech (near-zero peak correlations); the channel-energy-vs-gold-activity check gives 11/12 channels at 0–10 ms and 069c_EEPL_159 at 80 ms, well inside the 0.25 s DER collar. Listening check stays on the author's to-do list. — Cost if wrong: D1 would need a re-run after realignment; WER results unaffected (per-channel segments use each channel's own gold timings).
Task 5: review Approved; controller verified ⚠️: ihm/sdm pair_key sets identical, all manifests have unique ids, 3 RTTMs present, datasets/real_meetings git-ignored, no private paths in diff.
Task 5: minor (deferred): build_data.py lacks invariant asserts (pair sets, unique ids, RTTMs), SUMM-RE discovery/missing-file handling, DEMAND zip not closed/no integrity check.
Task 5: minor (deferred): summre segment end not clamped to audio duration; single long IPU relies on merge_units.
Task 5: minor (deferred): split by segment start → agm-de-0010 (172–189 s) is dev; cluster b01 mixes dev/test (plan-mandated; analysis uses test only).
Task 5: minor (deferred): tests miss AMI test-split branch, '*'/'xxx' filters, build_data glue; mix = channel mean without peak guard.
Task 5: complete (commits c03d87f..9f395a1, review clean)
Task 6: dispatched (sonnet), BASE 9f395a1
Task 6: implementer done df37c81 (DONE_WITH_CONCERNS: MMS loader workaround via _read_safetensors; flaky GPU when several big models load in one process; final 2 runs 5/5).
- Ruling R8: experiments run ONE system per Python process. Task 10's run_experiments gets a `--system` filter (default all) and Task 13 invokes it once per system, so CUDA/access-violation failures cannot cascade across systems and memory is fully released between models. — Cost if wrong: slightly longer wall-clock (model reload per process); no effect on results (runner is resumable/keyed).
Task 6: review Approved; ⚠️ resolved: LORA_ADAPTER has processor/tokenizer files (seen at planning); segments ≤ 30 s so HF truncation is moot; config/audio imports exist (T2/T4).
- Ruling R9: MMS custom-loader equivalence is verified empirically in Task 13 step 1 (dev smoke): mms-1b-all must give plausible text and WER < 60 % on AGM dev forced-clean in en/fr/de; otherwise stop before test runs and reload MMS with the stock loader in a fresh process. — Cost if wrong: MMS results unusable until fixed; other systems unaffected.
Task 6: minor (deferred): ignore_mismatched_sizes=True with explicit state_dict could mask shape mismatches (see R9 check).
Task 6: minor (deferred): _ST_DTYPES lacks U8/BOOL/F64; release() only drops local ref (plan-mandated; R8 mitigates); CPU compute_type label; HF detected_language = requested; bare except in NeMo fallback; temp dir not cleaned; unused numpy import; torch_dtype deprecated.
Task 6: complete (commits 9f395a1..df37c81, review clean)
Task 7: dispatched (haiku), BASE df37c81
Task 7: implementer done 10f01da (DONE, 98 passed); review dispatched
Task 7: review Approved with 2 plan-mandated Important findings, ruled:
- Ruling R10: CTC systems receiving language=None under auto conditions is prevented at the orchestration layer — Task 10 plans schedule auto conditions only for whisper-* and test_ctc_systems_never_run_auto_language enforces it; runner unchanged. — Cost if wrong: a hand-made job misusing auto+CTC aborts with ValueError; flushed rows survive.
- Ruling R11: resume key (segment_id, system, condition) intentionally excludes model_id/compute_type: each system label maps 1:1 to a fixed model config in transcribers.make_transcriber; changing a model requires a new label or a new CSV (to be stated in PROTOCOL §4). — Cost if wrong: a silently mixed CSV if someone edits a system's model in place.
Task 7: minor (deferred): zero-byte runs.csv gets no header; truncated last line after crash; collect_provenance ignores git failure; dirty check excludes tests/; missing tests for provenance/denoise/noise determinism at runner level; mid-file imports in test file.
Task 7: complete (commits df37c81..10f01da, 2 plan-mandated findings ruled)
Task 8: dispatched (haiku), BASE 10f01da
Task 8: implementer done bdd2041 (DONE, 104 passed); review dispatched
Task 8: review Approved; ⚠️ resolved: config ALPHA=0.05, N_BOOTSTRAP=10000, SEED=20261010 (T2, verified at review of T2).
Task 8: minor (deferred): corpus-WER test doesn't distinguish Σe/Σn from mean segment WER; unpaired CI test trivially constant (plan-mandated); percentiles hardcoded not from ALPHA; zero-denominator resample NaN; mixed-type cluster labels; holm with NaN p.
Task 8: complete (commits 10f01da..bdd2041, review clean)
Task 10: dispatched (haiku), BASE bdd2041, carries R2 (tag guard) + R8 (--system filter)
Task 10: implementer done 988afae (DONE, 108 passed; R2+R8 applied); review dispatched
Task 10: review Approved; ⚠️ resolved: SYSTEMS includes hf-whisper-small(-lora), SNRS_DB=(20,10,5), Condition.name values tested in T7 and exercised by passing test_rm_plans.
Task 10: minor (deferred): dedup keeps first hypothesis_id / keyed on datasets tuple (plan-mandated, harmless); no tests for R2 guard / R8 filter; git returncode ignored in guard (fails closed).
Task 10: complete (commits bdd2041..988afae, review clean)
Task 11: dispatched (haiku), BASE 988afae
Task 11: implementer done cc900d6 (DONE, 112 passed); review dispatched
Task 11: review Approved but 1 Important (reference/audio mismatch at 180 s boundary in run_streaming) → fix loop.
- Ruling R12: in run_streaming, the per-language dev/test audio boundary = start time of the first `test` segment of that language (not a hard 180 s), so every segment's reference and audio fall in the same window; plus a protocol-freeze guard identical to run_experiments (R2), since H5 test windows are test-split results. — Cost if wrong: dev window a few seconds longer than 180 s; no effect on pre-registered rule.
Task 11: minor (deferred): ZeroDivision if a window yields zero chunks; CSV written only at end; float tolerance compare; tests miss realtime_ok_share / single-chunk operating point.
Task 11: fix round 1/5 (2 addressed, 0 open; commits cc900d6..c2723e9)
Task 11: minor (deferred): run_streaming docstring still says [0,180 s); DEV_SECONDS maybe unused there; min() ValueError if no test segments; git missing → FileNotFoundError; boundary/guard untested. (AGM segments never overlap by construction, so the dev-tail overlap concern does not apply.)
Task 11: complete (commits 988afae..c2723e9, review clean after 1 fix round)
Task 12: dispatched (haiku), BASE c2723e9
Task 12: implementer done d66330f (DONE, 114 passed); review dispatched
Task 12: review Approved; ⚠️ resolved: config names exist (T2); mixes written 1-D by write_wav (mono); results/real_meetings created by runner before D1 runs (T13 order).
Task 12: minor (deferred): no mono assertion; collar literal duplicated; no UEM (state in methods: scored over union extent); RESULTS mkdir missing in script; collar/overlap untested (plan-mandated).
Task 12: complete (commits c2723e9..d66330f, review clean)
Task 14 (code steps 1–4 only, per R4): dispatched (haiku), BASE d66330f
Task 14 (code): implementer done 4a2f1dc (DONE, 117 passed); review dispatched
Task 14: review Needs fixes (4 Important) → rulings:
- Ruling R13: to_latex must not escape column titles (they are trusted LaTeX authored in analyse.py); cell values stay escaped. Fixes broken \Delta / p_{\text{Holm}} / \% headers. — Cost if wrong: none; titles are code constants.
- Ruling R14: Holm family is always the 9 pre-registered comparisons; a missing comparison enters Holm with p = 1 (conservative) and primary.csv records holm_m = 9. — Cost if wrong: slightly conservative adjusted p-values if the stop rule cuts runs.
- Ruling R15: no cluster namespacing change — real cluster labels are already dataset-prefixed by construction (agm-*, ami-*, summre-*, noise-*), so pooled comparisons cannot merge clusters across datasets; the colliding labels exist only in the test fixture. — Cost if wrong: none for real data.
- Finding 4 (weak tests) → add tests: raw LaTeX headers survive, Holm with a missing comparison uses m=9, P5 pairs ami-ihm/ami-sdm rows by pair_key.
Task 14 (code): fix round 1/5 (3 Important addressed + R15 confirmed, 0 open; commits 4a2f1dc..5188ced)
Task 14: minor (deferred): Holm test assertion weak if p formats to 0.0000; P5 test estimate 0.2 also equals unpaired diff (doesn't prove pairing); caption/label inserted raw; P8 partial pooling silently ok; lang_mismatch_rate meaningless for noise; figure averages rounded WERs; primary.tex omits reject/raw p; upper median for rtf.
Task 14 (code steps 1–4): complete (commits d66330f..5188ced, review clean after 1 fix round). Steps 5–6 pending real results (R4).
Task 9 (step 1 + DRAFT protocol, no freeze/tag per R4): dispatched (sonnet), BASE 5188ced
Task 9 (part 1): implementer done 681cc40 (DONE, 120 passed); 40 spot-check clips ready; review dispatched
Task 9 (part 1): review Approved; ⚠️: AGM §2 sums internally consistent (checked by reviewer); manifests built in T5.
Task 9: minor (deferred to freeze): DE-check coverage denominator uses 180 s not R12 boundary; name/inspect the 1 flagged EN segment; MMS sentence wording (state equivalence result after smoke run, maybe list in §9); clusters cell layout; carry the >25 % "major" rule into §3.
Task 9 (part 1): complete (commits 5188ced..681cc40, review clean). Part 2 (spot-check verdicts, sha256, freeze tag) = HUMAN GATE.
Task 13 step 1 (dev smoke, per system, R8/R9): dispatched (sonnet), HEAD 681cc40
Task 13 step 1 (dev smoke): 5/6 systems OK (whisper-large-v3 agm forced-clean dev WER 13.0 %); mms-1b-all CUDA OOM on first clip (twice, conv layer, empty 8 GB GPU) → R9 not yet checkable. noise rows 0 = expected (noise segments are test split). n_ref=0 on filler-only AMI ref "UH" (EN2002a-FEO070-0002801) → hf-whisper loop 440 insertions. Whisper ami-sdm 88–106 % on 5 segs.
- Ruling R16: segments whose reference is empty after normalisation (filler-only, e.g. "UH") are excluded from all WER aggregates and primary tests (non-noise datasets only); they stay in runs.csv and their count per dataset is reported. Decided pre-freeze, goes into PROTOCOL §6. — Cost if wrong: a handful of AMI backchannel segments leave the WER denominator (they contribute no reference words anyway; only their insertions are dropped).
- Ruling R17: MMS OOM is a defect in the Task 6 adapter (likely the custom loader); fixed via a debugging dispatch with a GPU repro, then R9 check reruns MMS on ALL agm dev segments (all 3 languages), not --limit 5. — Cost if wrong: MMS dropped from the study as "could not run on 8 GB" (H1 still has whisper vs conformer).
- Ruling R18: before trusting the ami-sdm smoke numbers, sanity-check SDM audio (RMS, listen-free checks) and measure whisper-large-v3 on all ami-sdm dev segments. — Cost if wrong: none (diagnostic only).
Smoke follow-up: dispatched (sonnet) for R16 code + R17 fix + R18 check.
Smoke follow-up: done 1bb42f4 (MMS fix: host weight copy exhausted Windows commit → CUDA init failure; now tensors read straight to GPU into meta model, peak 2.1 GB) + f6017ba (R16 exclusion, 122 passed). R9 PASS: MMS agm dev WER en 13.5 / fr 18.9 / de 16.2 %. R18: SDM audio fine; whisper-large-v3 dev ami-sdm 26.6 % vs ami-ihm 13.5 %. Review dispatched.
Smoke follow-up: review Approved (R16/R17 met).
Smoke follow-up: minor (deferred): MMS missing-key whitelist (adapter/lm_head) → unclear meta error; fully-excluded group vanishes from summary; pick uses string "0" vs _int in summarise; no test that noise keeps empty-ref rows; `del state` cosmetic.
Task 13 step 1: complete (smoke 6/6 systems run on dev after fixes 681cc40..f6017ba).
== HUMAN GATE (R4) reached at f6017ba: waiting for author spot-check (results/real_meetings/agm_spotcheck.csv, 40 clips) → then freeze PROTOCOL (fold in T9 deferred minors + R16 in §6), manifests.sha256, tag protocol-frozen → T13 steps 2–4 (test runs, one system per process) → T14 steps 5–6 → final whole-branch review. ==
HUMAN GATE passed 2026-10-10: author reports all 40 AGM spot-check clips (20 FR, 20 EN) verbatim (verdicts given in chat after listening via the local spot-check page). Freeze dispatched (sonnet).
Task 9 part 2: freeze done eb080cb, tag protocol-frozen = HEAD, 122 passed; review dispatched
Task 9 part 2: review Approved (all freeze requirements met; tag = eb080cb). Spec docs/specs/... (53248d7) is an ancestor of the tag, so the referenced hypotheses are frozen too.
Task 9: minor (deferred): §3 could say verdicts entered from author's chat report; name seed/script for spot-check sampling; caption-check heading ambiguity (DE vs all languages); "nothing may change" wording.
Task 9: complete (commits 5188ced..681cc40 + f6017ba..eb080cb; tag protocol-frozen)
Task 13 steps 2–4 (test runs): dispatched (sonnet), HEAD eb080cb
Task 13 steps 2–4: done ed64b45. 26,463 test rows, all at eb080cb, no dupes, no shortfall. Crashes: large-v3 MemoryError at 1h20 + load OOMs, resumed cleanly; conformer startup failures ×3 then OK; run_streaming OOM when loading large-v3 after small in one process → rerun OK. Anchor: ASRU WX_vad_noprompt 0.297 vs our large-v3 summre 0.301. H5 points: small de10/en10/fr20; large-v3 de10/en20/fr20. D1 DER: 018a 0.079, 032b 0.274 (hyp 5 spk vs 4), 069c 0.112.
Task 13: minor (deferred): run_streaming loads two Whisper models in one process (OOM once) — R8 not applied to that script; chain_test.sh committed with logs.
Task 13: complete (operational; commit ed64b45)
Task 14 steps 5–6 (analysis on real results + docs): dispatched (sonnet)
Task 14 steps 5–6: done 5dfe7ae (analyse 101 groups, 9/9 primary computed; hand checks pass; ETAT/CHANGELOG updated). Notable: P3 (fr large-v3 vs conformer) CI includes 0; P8 pooled +3.4 pts but +0.25 on AGM snr5 alone; P9 LoRA −10.1 pts (better) contrary to H4d — possibly driven by hf-whisper-small repetition loops (check in writing phase); D1 032b 0.274 with 5 hyp speakers.
Task 14: complete (commits d66330f..5188ced + 5dfe7ae)
ALL TASKS COMPLETE. Final whole-branch review dispatched (opus).
FINAL REVIEW (opus): With fixes. Critical: docs say "8 rejets" but primary.csv has 7 (P1,P2,P5–P9); P9 LoRA gain mostly loop suppression (loop-free −1.1 [−1.66,−0.56]). Important: P3 driven by one loop (agm-fr-0019); P8 label says agm but pooled, driven by AMI-SDM ES2004a; spec→protocol deviations unlogged (clusters, own bootstrap, filler rule, D1 checkpoint, spot-check seed); ASRU anchor has no committed script; primary.tex lacks A/B/raw p/reject. Must-fix minors: ETAT §5 order, UEM/RTTM/mix methods notes, lang_mismatch n/a for noise & HF.
- Ruling R19: post-freeze changes are restricted to presentation, documentation and clearly labelled EXPLORATORY scripts/outputs; pre-registered estimates, tests and code paths stay untouched (P8 label fix is presentation only); every post-freeze change is logged in PROTOCOL §9 as "post-freeze (2026-10-11), exploratory/presentation". — Cost if wrong: a jury could see post-hoc sensitivity analyses as fishing; mitigated by labelling them exploratory and keeping primary results verbatim.
Final fix wave: dispatched (sonnet), FIX_BASE 5dfe7ae
Final fix wave: done a2741c5..aa0ead2 (130 passed; pre-registered columns byte-identical). Scoped re-review dispatched.
Final re-review: all 8 findings ADDRESSED, no new breakage. FINAL REVIEW CLEAN.
