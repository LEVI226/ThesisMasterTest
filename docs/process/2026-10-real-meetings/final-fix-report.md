# Final-review fix wave: report (2026-10-11)

Branch study/real-meetings. Commits: a2741c5 (docs count), 007ca91 (sensitivity), 10d9f04 (anchor), 0efc50e (analysis presentation), aa0ead2 (PROTOCOL 9 + ETAT/CHANGELOG). No push, no tag moved, no experiment re-run.

## Per item
1. ETAT_ACTUEL.md (line ~149) and CHANGELOG.md (line ~135): "8 rejets" -> "7 rejets sur 9" (primary.csv reject_h0=1 for P1,P2,P5,P6,P7,P8,P9). ETAT study section "## 5." renumbered "## 8."; CHANGELOG cross-reference updated to section 8.
2. study_real_meetings/sensitivity.py (pure functions loop_free_pairs, per_meeting_sdm_ihm, loop_rates, sensitivity_rows), scripts/sensitivity.py, tests/test_rm_sensitivity.py (5 tests), results/real_meetings/sensitivity.csv (65 rows, analysis_type=exploratory_post_freeze, no p-values). The "with loops (reference)" rows reproduce primary.csv P9 (-0.1009 [-0.1903,-0.0292]) and P3 (-0.0498 [-0.0981,0.0114]) exactly. TDD: the test module first failed at collection (module absent), then passed; one test adjusted for 4-decimal rounding tolerance.
3. analysis.py primary_tests: P8 a/b labels now "whisper-large-v3|auto|agm-snr5+ami-sdm+summre|all" / "...|forced|...".
4. scripts/analyse.py + analysis.py (COMPARISON_LABELS, format_p, P_HOLM_FLOOR_DISPLAY): primary table columns Test, Comparison (A vs B), delta WER, CI, p, p_Holm, H0 decision; floor values shown "<0.001" (raw) / "<0.002" (Holm); caption states A-B in WER points, cluster bootstrap, Holm m=9. Memoire_LaTeX/generated/real_meetings_primary.tex regenerated. real_meetings_snr.pdf (only metadata differs) was NOT committed.
5. scripts/anchor.py + results/real_meetings/anchor.csv (below).
6. PROTOCOL.md section 9: spec->protocol entries, dev-split clarification, and post-freeze entries (sensitivity, anchor, P8 label/table/lang_mismatch, doc count fix).
7. analysis.summarise: lang_mismatch_rate "" for dataset noise and systems hf-whisper-small / hf-whisper-small-lora (NO_LANG_DETECTION).
8. ETAT_ACTUEL.md (new subsections "Analyses exploratoires (post-gel)" and "Limites") and CHANGELOG.md (dated 2026-10-11 entry); anchor line in ETAT updated to exact values. All numbers taken from sensitivity.csv / anchor.csv / summary.csv / primary.csv.

## TDD evidence
tests/test_rm_analysis.py: 3 new tests (P8 label, lang_mismatch n/a, format_p) shown failing (3 failed, 8 passed) with analysis.py stashed to HEAD, passing (11) after. Full default suite: 122 -> 127 (sensitivity) -> 130 (analysis); final "130 passed, 5 deselected".

## Proof pre-registered numbers unchanged (column-wise diff vs HEAD before the change)
primary.csv: only columns a and b changed, one row each (P8): 'whisper-large-v3|auto-snr5|agm|all' -> 'whisper-large-v3|auto|agm-snr5+ami-sdm+summre|all' and 'whisper-large-v3|forced-snr5|agm|all' -> 'whisper-large-v3|forced|agm-snr5+ami-sdm+summre|all'. estimate, CI, p, n, Holm, reject unchanged in all 9 rows.
summary.csv: same shape; only lang_mismatch_rate changed (10 cells, to ""); every WER/CI/count column unchanged. runs.csv, streaming.csv, diarization.csv, stats.py, text.py, runner.py, plans.py, transcribers.py untouched.

## anchor.csv
system,wer,n_ref_words,n_segments
asru-published-whisper (WX_vad_noprompt),0.2948,13063,649
whisper-large-v3 forced-clean (ours),0.3012,13063,649

Without R16 the published figure is 0.2967 (the 0.297 first quoted); with R16 (consistent with our row) 0.2948. Ratio ours/published = 1.022.

## sensitivity.csv (non-loop-rate rows)
```
analysis_type,analysis,group,metric,estimate,ci_low,ci_high,n_pairs,n_excluded,n_clusters,wer_a,wer_b,note
exploratory_post_freeze,P9 with loops (reference),all,wer_diff_a_minus_b,-0.1009,-0.1903,-0.0292,1949,0,28,,,same selection and seed as the pre-registered test
exploratory_post_freeze,P9 loop-free,all,wer_diff_a_minus_b,-0.0110,-0.0166,-0.0056,1929,20,28,,,pairs where either side has repetition_loop=1 removed
exploratory_post_freeze,P3 with loops (reference),all,wer_diff_a_minus_b,-0.0498,-0.0981,0.0114,68,0,11,,,same selection and seed as the pre-registered test
exploratory_post_freeze,P3 loop-free,all,wer_diff_a_minus_b,-0.0893,-0.1103,-0.0681,65,3,11,,,pairs where either side has repetition_loop=1 removed
exploratory_post_freeze,P8 per dataset,agm,wer_diff_a_minus_b,0.0026,0.0000,0.0081,203,0,32,,,"a = auto-snr5, b = forced-snr5"
exploratory_post_freeze,P8 per dataset,ami-sdm,wer_diff_a_minus_b,0.0831,0.0228,0.1735,1300,0,16,,,"a = auto-clean, b = forced-clean"
exploratory_post_freeze,P8 per dataset,summre,wer_diff_a_minus_b,0.0076,0.0040,0.0131,649,0,12,,,"a = auto-clean, b = forced-clean"
exploratory_post_freeze,P8 wrong-language rate (auto),agm,share_detected_ne_language,0.0049,,,203,,,,,condition auto-snr5
exploratory_post_freeze,P8 wrong-language rate (auto),ami-sdm,share_detected_ne_language,0.0885,,,1300,,,,,condition auto-clean
exploratory_post_freeze,P8 wrong-language rate (auto),summre,share_detected_ne_language,0.1495,,,649,,,,,condition auto-clean
exploratory_post_freeze,P5 per meeting,EN2002a,wer_diff_a_minus_b,0.2713,,,734,,,0.4792,0.2079,"a = SDM, b = IHM; point estimate, no CI"
exploratory_post_freeze,P5 per meeting,ES2004a,wer_diff_a_minus_b,0.1746,,,183,,,0.3159,0.1413,"a = SDM, b = IHM; point estimate, no CI"
exploratory_post_freeze,P5 per meeting,IS1009a,wer_diff_a_minus_b,0.1115,,,146,,,0.2544,0.1430,"a = SDM, b = IHM; point estimate, no CI"
exploratory_post_freeze,P5 per meeting,TS3003a,wer_diff_a_minus_b,0.1820,,,237,,,0.3152,0.1332,"a = SDM, b = IHM; point estimate, no CI"
```
Loop-rate rows: 51 (system x dataset x condition); see the CSV.
