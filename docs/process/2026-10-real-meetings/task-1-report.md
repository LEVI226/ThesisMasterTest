# Task 1 report: Day-1 setup (branch study/real-meetings)

Status: DONE_WITH_CONCERNS

## Commit
- b9bbcb3 chore(study): day-1 setup for the real-meetings study

Files changed (9, 70 insertions, no deletions):
- `.gitignore`: appended the `datasets/real_meetings/` entry with its comment.
- `pyproject.toml`: `[tool.pytest.ini_options]` gained `pythonpath`, `markers`, `addopts`; `"num2words>=0.5.13"` added to `dependencies` (by `uv add`).
- `uv.lock`: +20 lines (docopt 0.6.2, num2words 0.5.14), written by `uv add --no-sync`.
- `ETAT_ACTUEL.md`: appended §5 (brief text, preceded by one blank line).
- `CHANGELOG.md`: appended the Phase 4 section verbatim.
- `docs/Message_Superviseur_real_meetings.md`: new supervisor message draft.
- `study_real_meetings/__init__.py`, `study_real_meetings/sources/__init__.py`, `study_real_meetings/scripts/__init__.py`: new, empty.

Not staged (left untouched): `tmp/platform_stderr.log`, `tmp/platform_stdout.log` (modified), `audioReunion_transcribe.log`, `topic1/` (untracked).

## Step 4 commands and outputs
```
uv add --no-sync "num2words>=0.5.13"
  Resolved 233 packages in 8.74s            (exit 0)

uv pip install --python .venv/Scripts/python.exe "num2words>=0.5.13"
  + docopt==0.6.2
  + num2words==0.5.14                       (exit 0)

.venv/Scripts/python.exe -c "from num2words import num2words; print(num2words(160, lang='fr'))"
  cent soixante                             (exit 0)

.venv/Scripts/python.exe -c "import torch, ctranslate2; print(torch.__version__, ctranslate2.__version__)"
  2.6.0+cu124 4.6.0                         (exit 0; a pkg_resources UserWarning from ctranslate2 is printed, harmless)
```
Pinned stack unchanged. `uv sync` and `uv run` were not used.

## Step 6 commands and outputs
Default run, as specified in the brief:
```
.venv/Scripts/python.exe -m pytest -q
  43 passed, 4 warnings, 26 errors in 20.94s   (exit 1)
```
The 26 errors are all `PermissionError: [WinError 5] Accès refusé` on the `tmp_path` fixture (`C:\Users\ulric\AppData\Local\Temp\pytest-of-ulric`), and the cache provider also cannot write under `tmp/pytest_cache` (`ls` returns "Permission denied"). They are environmental (Windows ACLs on the temp and cache directories) and not caused by this task's changes, which touch no test code or temp paths. Affected tests:
- tests/test_contract_regressions.py: 15 tests (all of its `test_transcribe_*`, `test_pending_speech_*`, `test_end_signal_*`, `test_latency_csv_*`, `test_transcript_*`, `test_session_log_*`, `test_residual_packet_*`, `test_flushed_ack_*`, `test_stop_then_disconnect_*`, `test_file_path_writes_a_session_log`)
- tests/test_diarization_files.py: `test_file_speaker_assignment_uses_waveform_and_supported_output[False]` and `[True]`
- tests/test_evaluation.py: `TestLoadMetadata` (6 tests: loads_valid_csv, missing_file_raises, missing_column_raises, empty_csv_raises, resolves_paths, validate_missing_files)
- tests/test_evaluation_runner.py: `test_default_matrix_forces_each_samples_own_language`, `test_custom_condition_forwards_vad_and_keeps_transcripts_in_csv`

Diagnostic run (no repo changes; redirects the temp basetemp to a writable directory and disables the cache provider):
```
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp <writable temp dir>
  69 passed, 5 warnings in 23.96s   (exit 0)
```
So there are no test failures in the suite itself. The brief's reference count was 68; this run collects 69. The extra test was not identified and was not investigated.

## Self-review
- Only explicit paths were staged; no `git add -A`.
- The `uv.lock` diff contains only the docopt and num2words entries.
- The `pyproject.toml` diff contains only the three pytest lines and the num2words dependency.
- The `.gitignore` diff contains only the new comment and entry.
- The `ETAT_ACTUEL.md` and `CHANGELOG.md` text matches the brief verbatim; both files still end with LF and have no BOM.
- Git prints "LF will be replaced by CRLF" warnings for the edited files; these come from the repo's existing autocrlf setup and were not changed.
- `main` and the tag `defense-baseline` were not touched.

## Concerns
1. Test environment: the default `pytest -q` run exits 1 with 26 permission errors on this machine (see above). It passes 69/69 with a writable basetemp and no cache. The controller should decide whether to fix the Windows permissions on `%LOCALAPPDATA%\Temp\pytest-of-ulric` and `tmp/pytest_cache`; I did not change them.
2. Commit attribution: the brief's heredoc specifies `Co-Authored-By: Claude Opus 5.5`. The harness attribution reminder for this session specifies `Claude Haiku 5.5`, which is the model actually running this task. I used Haiku 5.5. If Opus 5.5 is required, amend the trailer.
3. Test count: 69 collected vs 68 in the brief (see above). Not investigated.
4. The supervisor message draft is only a file; nothing was sent. The "Human action" step is left for the author.

---

# Fix round 1 (coordinator review)

Both Important findings are fixed. The sections above describe the state before this round; where they conflict with this section, this section is current (the commit SHA b9bbcb3 is now deafa65, and the default pytest run is green).

## Fix 1: commit trailer (amend)
- b9bbcb3 was unpushed and HEAD, so it was amended with the same subject and body and the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. No content changed.
- New SHA: deafa65.
- Output of `git log -2 --format=%B`:
```
chore(study): day-1 setup for the real-meetings study

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
---
docs(plan): implementation plan for the real-meetings study pipeline

14 TDD tasks: day-1 setup, scoring on top of the thesis scorer, manifests,
DEMAND noise mixing, AGM/AMI/SUMM-RE builders, transcriber adapters,
resumable runner, cluster-bootstrap stats + Holm, protocol freeze,
experiment plans, H5 streaming, D1 diarization, execution, analysis.
Deviations from the spec are listed in the plan header.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
---
```

## Fix 2: pytest config (ruling R5, config not ACLs)
- `pyproject.toml` `[tool.pytest.ini_options]`: `cache_dir = ".pytest_cache"` (was `tmp/pytest_cache`); `addopts = "-m 'not gpu' --basetemp=.pytest_tmp"` (was `"-m 'not gpu'"`). The other lines (testpaths, pythonpath, markers) are unchanged.
- `.gitignore`: appended under a `# pytest scratch (tmp/ has a Windows ACL problem on this machine)` comment: `.pytest_cache/` and `.pytest_tmp/`.
- Commit: ccb53c6 `chore(study): pytest scratch dirs that are writable on Windows` (Opus trailer). Staged paths: `pyproject.toml` and `.gitignore` only. 2 files, +6 / -2.
- Default run, no extra flags:
```
.venv/Scripts/python.exe -m pytest -q
  69 passed, 4 warnings in 27.34s   (exit 0)
```
- The 26 WinError 5 errors from the earlier run are gone with this config. The 4 remaining warnings are the existing ones (ctranslate2 pkg_resources and similar); none are errors.

## Resulting commits on study/real-meetings
- ccb53c6 chore(study): pytest scratch dirs that are writable on Windows
- deafa65 chore(study): day-1 setup for the real-meetings study
- Unstaged and untouched: `tmp/platform_stderr.log`, `tmp/platform_stdout.log`, `audioReunion_transcribe.log`, `topic1/`.

## Concerns
- The count in the earlier "Concerns" list is resolved: the Haiku trailer was amended to Opus, and the pytest errors are fixed by the config change.
- The 69 collected tests vs the brief's 68 is still uninvestigated (not part of this round).
