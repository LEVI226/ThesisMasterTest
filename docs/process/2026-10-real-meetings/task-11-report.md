# Task 11: Streaming simulation (H5) - report

Status: DONE
Commit: cc900d6 feat(study): H5 fixed-chunk streaming simulation with dev-chosen operating point (branch study/real-meetings)

## TDD evidence
- RED: `.venv\Scripts\python.exe -m pytest tests/test_rm_streaming.py -q` -> collection error `ModuleNotFoundError: No module named 'study_real_meetings.streaming'`.
- GREEN: same command -> `4 passed in 3.90s`.

## Import check
- `.venv\Scripts\python.exe -c "import study_real_meetings.scripts.run_streaming"` -> OK (script not executed; it needs GPU models and the protocol freeze).

## Full default suite
- `.venv\Scripts\python.exe -m pytest -q` -> `112 passed, 5 deselected, 4 warnings` (108 prior + 4 new).

## Files
- Created: study_real_meetings/streaming.py
- Created: study_real_meetings/scripts/run_streaming.py
- Created: tests/test_rm_streaming.py
- Output (when run): results/real_meetings/streaming.csv

## Interface checks
- score_words returns Counts with n_ref, errors (property), wer (property): matches script usage.
- latency_summary returns n, median, p95: matches.
- collect_provenance returns git_commit and gpu: matches.
- Segment has language, split, reference: matches. Transcript(text, detected_language, seconds): matches.

## Concerns
- Working tree has unrelated pre-existing changes (tmp/platform_*.log modified; audioReunion_transcribe.log and topic1/ untracked). Not staged or committed.
- Git emitted LF->CRLF warnings on the new files; content is unaffected.
- run_streaming.py divides by len(res) for the realtime share and passes an empty list to latency_summary if a window yields no chunks (would raise ZeroDivisionError / ValueError). Brief code kept verbatim; flagged only.
- Commit uses the Co-Authored-By trailer "Claude Haiku 5.5 <noreply@anthropic.com>" as given by the harness.

## Fix round 1 (review)
1. Dev/test boundary (R12): per language, `boundary = min(s.start for s in segs if s.language == lang and s.split == "test")`; windows are `{"dev": (0.0, boundary), "test": (boundary, wav_duration(wav))}`. References unchanged (join of segment references per split).
2. Protocol-freeze guard (R12): `main()` starts with `git tag -l protocol-frozen` run in C.ROOT; if empty, `raise SystemExit("Protocol not frozen (git tag 'protocol-frozen' missing): H5 test windows are test-split results (Task 9).")`. Added `import subprocess`.
- Pure functions in streaming.py unchanged.
- `tests/test_rm_streaming.py`: 4 passed.
- Import check `study_real_meetings.scripts.run_streaming`: OK (script not run; no protocol-frozen tag exists yet, so a real run would exit at the guard).
- Full default suite: 112 passed, 5 deselected.
- An IDE hint flagged `subprocess` as unused right after the edit; it is used in main(), so the hint is stale.
