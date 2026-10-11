# Task 4 report: Audio I/O and realistic noise mixing

Status: DONE

## Commit
- c03d87f feat(study): audio I/O and deterministic DEMAND noise mixing at fixed SNR

Files (explicit paths only):
- study_real_meetings/audio.py (new): convert_to_wav16k, load_segment, write_wav, wav_duration
- study_real_meetings/noise.py (new): stable_rng, mix_at_snr, pick_noise, load_demand_bank
- tests/test_rm_audio_noise.py (new): 4 test functions (7 collected cases with SNR parametrization)

Code was taken verbatim from the brief. config.py was not edited.

## TDD evidence
RED: `.venv/Scripts/python.exe -m pytest tests/test_rm_audio_noise.py -q`
  Collection error: `ModuleNotFoundError: No module named 'study_real_meetings.audio'` (1 error, interrupted).

GREEN: `.venv/Scripts/python.exe -m pytest tests/test_rm_audio_noise.py -q`
  `7 passed in 0.15s`

## Full default suite
`.venv/Scripts/python.exe -m pytest -q` -> `91 passed, 4 warnings in 18.84s`
(84 pre-existing + 7 new.)

## Concerns
- Git warned "LF will be replaced by CRLF" for the three new files. This is a line-ending setting in the repo's git config/attributes, not a test or behavior issue. Not changed.
- Working tree had pre-existing unrelated changes (tmp/platform_stderr.log, tmp/platform_stdout.log modified; audioReunion_transcribe.log and topic1/ untracked). Left untouched and not committed.
- ffmpeg path (convert_to_wav16k) is not exercised by tests, per the brief.
