# Microphone manipulation 5 — long sentences, Disconnect straight after speech (FR forced)

Session live_20260916T133103_8a73e1, lang='fr', model small cuda/float16, new frontend (round 4).

| Claim | Status | Evidence |
|---|---|---|
| Browser sends its residual (< 1 packet) before `__end__` | **verified end-to-end** — min packet 512 B (16 ms) vs 32 000 B in every pre-fix session | session_end.chunks.min |
| Close waits for the `flushed` ack | **verified** — `__end__` received, empty buffer, ack sent, socket closed after it | server log |
| Text displayed after a flush that takes > 2 s | **not exercised** — all 7 utterances ended by natural silence; GPU decodes 14 s of audio in ≤ 1.54 s, so no flush ever approached 2 s | latencies 0.59–1.54 s |
| Long utterances (9–14 s) on the live path | 7/7 delivered; acoustic word errors ("agresse", "images" for "démarches" ×2, "part de nez/donnée", "patenaire"); 1 near-exact | screen + log |

To exercise the slow-flush display, the server must be slow: rerun with STT_DEVICE=cpu WHISPER_MODEL=medium (manual step 6).
