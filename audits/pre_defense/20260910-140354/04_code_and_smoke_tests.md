# 04 Software tests

## Test suite

First run, default configuration:

    .venv/Scripts/python.exe -m pytest tests/ -q
    -> 43 passed, 8 errors

All 8 errors were `PermissionError: [WinError 5]` on
`C:\Users\ulric\AppData\Local\Temp\pytest-of-ulric`. Classification:
**resource unavailable**, not a code regression. The pytest temp root is not
writable in this environment.

Re-run with a writable base temp directory:

    .venv/Scripts/python.exe -m pytest tests/ -q --basetemp=<writable dir>
    -> 51 passed, 0 failed, 0 skipped

The 8 errored tests are `tests/test_evaluation.py::TestLoadMetadata` (6) and
`tests/test_evaluation_runner.py` (2). All pass once the temp directory is
writable. No test was modified, skipped or removed.

**Caveat carried forward:** 51 passing unit tests do not establish scientific
accuracy. None of these tests performs real inference; they validate metadata
loading, configuration forwarding and CSV shape.

## Not executed

A real ASR smoke test was NOT run in this pass. The recalculation in report 03
works from stored `reference_text`/`hypothesis_text`, which is a stronger check
of the reported numbers than a fresh small inference would be. A smoke test
remains the correct next step for verifying that the *current* code still
reproduces the historical pipeline; it is marked NOT EXECUTED.
