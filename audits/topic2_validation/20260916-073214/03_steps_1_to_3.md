# Steps 1-3: reproduce, fix, regression-test

Scope: software contracts only. Nothing here is evidence of ASR quality.
Historical CSVs, transcripts and the manuscript were not modified.

## Reproduced BEFORE any change (01_repro_defects_BEFORE.json)

| # | Defect | Evidence |
|---|---|---|
| 1 | `/transcribe` ignores `language` sent as multipart form | engine received `None` via form, `fr` via query string |
| 2 | last utterance lost on WebSocket disconnect | 32 000 bytes pending, 0 transcription calls |
| 3 | transcript side files collide across model / VAD | 324 rows -> 180 paths; 72 paths shared across different model or condition; 219 rows whose stored hypothesis differs from the file on disk |

## Fixes (02_fixes.diff — 62 insertions, 13 deletions, 3 files)

- **backend/main.py**
  - `language` accepted as `Form(None)`; query string still accepted via `Query(alias="language")`; whichever is given is forwarded.
  - WebSocket loop reads `receive()` so a text frame is visible; `__end__` triggers `_flush_pending()` and a `{"type":"flushed"}` ack; `finally:` flushes on disconnect (best effort, text logged before send so a dead socket never loses it).
  - `latency_csv` read per session from `LIVE_LATENCY_CSV` (default unchanged: historical file). Validation runs MUST set this variable.
- **backend/evaluation/runner.py**
  - transcript file name now `{stem}__{model_used}_prep{}_prompt{}_lang{}_vad{}.txt`, computed after the model actually used is known.
  - `TRANSCRIPT_DIR` overridable from env (default unchanged).
- **frontend/index.html**
  - `liveStopRecord()` sends `__end__`; `liveDisconnect()` waits up to 2 s for the `flushed` ack before closing.

Original mixed line endings preserved on untouched lines (restore_endings.py).

## Reproduced AFTER (01_repro_defects_AFTER.json)

| # | Result |
|---|---|
| 1 | form -> `fr`, query -> `fr`. **Fixed.** |
| 2 | 0 bytes pending, 1 transcription call. **Fixed.** |
| 3 | historical collision counts unchanged **by design** (the probe reads the historical CSVs, which stay untouched). The fix applies to new runs and is proven by regression tests, not by rewriting history. |

## Regression tests (tests/test_contract_regressions.py, 10 tests)

- language via form / via query / absent -> auto
- disconnect flushes pending speech; `__end__` flushes and acks; `__end__` on empty buffer is harmless
- `LIVE_LATENCY_CSV` honoured per session, default preserved
- transcript paths differ between models, between VAD settings; `TRANSCRIPT_DIR` honoured

Full suite: **61 passed** (51 existing + 10 new), 0 failed.

## Claims status after this step

| Claim | Status | Proof |
|---|---|---|
| "The language chosen in the upload menu is forced" | **contradicted before fix, verified after fix (contract only)** | 01_repro_defects_BEFORE/AFTER.json, 3 tests |
| "The last sentence is transcribed when the user stops" | **contradicted before fix, verified after fix (contract only; real-audio check pending)** | idem |
| "Each run's transcript file is unique" | **contradicted for the historical campaign; verified for new runs** | idem; CSV text columns remain authoritative for the historical results |
| Any WER / latency figure | **not tested here** | — |
