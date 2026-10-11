# Task 8 report: Statistics (corpus WER, clustered bootstrap, Holm)

Status: DONE
Commit: bdd2041 feat(study): corpus-WER cluster bootstrap (paired/unpaired) and Holm correction
Files: study_real_meetings/stats.py (new), tests/test_rm_stats.py (new). Brief code used verbatim.

## TDD evidence

RED: `.venv/Scripts/python.exe -m pytest tests/test_rm_stats.py -q`
  -> collection error: `ModuleNotFoundError: No module named 'study_real_meetings.stats'`
  -> "Interrupted: 1 error during collection"

GREEN: same command after creating stats.py
  -> `6 passed in 0.14s`

## Full default suite

Before: `98 passed, 5 deselected, 4 warnings in 19.18s`
After:  `104 passed, 5 deselected, 4 warnings in 18.07s` (98 + 6 new)

## Concerns
- Inputs must be sequences (list/ndarray), not one-shot generators: `corpus_wer` and `_cluster_sums` each consume the input, and `len(list(...))` is used for segment counts. Callers in Task 9+ should pass lists.
- `backend/evaluation/statistics.py` untouched. config.py untouched.
- git emits LF->CRLF warnings on commit (Windows autocrlf); content unaffected.
- Working tree has unrelated pre-existing changes (tmp/*.log, untracked topic1/, audioReunion_transcribe.log) that were NOT staged or committed.
