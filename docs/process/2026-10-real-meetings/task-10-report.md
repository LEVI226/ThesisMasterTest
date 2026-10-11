# Task 10 report: Experiment plans and the experiment CLI

Status: DONE
Commit: 988afae feat(study): pre-registered experiment plans and resumable CLI
Branch: study/real-meetings

## TDD evidence
- RED: `.venv/Scripts/python.exe -m pytest tests/test_rm_plans.py -q` -> collection error `ModuleNotFoundError: No module named 'study_real_meetings.plans'`.
- GREEN: same command -> `4 passed`.

## --help output
```
usage: run_experiments.py [-h] --plan {H1,H2,H3,H4a,H4b,H4c,H4d,NOISE,ALL}
                          [--split {dev,test,all}] [--limit LIMIT] [--out OUT]
                          [--system {whisper-small,whisper-large-v3,mms-1b-all,conformer-ctc-large,hf-whisper-small,hf-whisper-small-lora}]
options: -h, --plan, --split, --limit, --out, --system (run only this system; default all)
```

## Full default suite
`.venv/Scripts/python.exe -m pytest -q` -> 108 passed, 5 deselected, 4 warnings (104 prior + 4 new). The warnings are not from the new files.

## Deviations (controller rulings applied)
- R2: test-split guard checks git tag `protocol-frozen` (via `git tag -l`, cwd=ROOT) instead of PROTOCOL.md existence. Added `import subprocess`.
- R8: added `--system` (choices=SYSTEMS, default None). Filter applied right after `jobs_for(args.plan)`. If nothing remains, prints a one-line message and exits 0.
- Docstring examples use forward slashes (`.venv/Scripts/python.exe`) to avoid a SyntaxWarning from `\S` escapes. Not a behavioural change.
- plans.py and tests/test_rm_plans.py are verbatim from the brief.

## Files
- study_real_meetings/plans.py (new)
- study_real_meetings/scripts/run_experiments.py (new)
- tests/test_rm_plans.py (new)

## Concerns
- The CLI was not run for real (it loads GPU models), per instructions. Only parsing was verified.
- Git warned that LF will be replaced by CRLF on the three new files. This is a line-ending config matter and does not affect the commit.
- Pre-existing uncommitted changes (tmp/platform_*.log, audioReunion_transcribe.log, topic1/) were left untouched and not staged.
