# Microphone manipulation 6 — slow flush on CPU, Disconnect while still speaking (FR forced)

Server: small **cpu/int8** (forced via STT_DEVICE), new frontend (round 4). Sessions 13:38:15 and 13:38:45.

| Claim | Status | Evidence |
|---|---|---|
| Text is displayed after a flush that takes > 2 s | **verified on screen** — two `end_signal` flushes of 10.4 s / 9.0 s of pending audio decoded in **5.05 s / 5.03 s**; both delivered (no send error), both visible in the user's transcript | sessions + server3_cpu.log + user screen |
| Browser residual reaches the server | **verified** — min packet 256 B | session_end.chunks.min |
| Old behaviour would have lost them | by construction: the 2 s cap closed the socket before a 5 s decode | apply_fixes_4 diff |
| Start of recording | **observed**: the first words ("Je souhaite changer") are missing in all three utterances — speech began before mic/AudioContext were live. Not the flush; an end-to-end start-up latency item for T5 | screen |

Stop-scenario coverage is now complete on index.html (server + browser + human). /live has the same code but was not exercised in a browser.
