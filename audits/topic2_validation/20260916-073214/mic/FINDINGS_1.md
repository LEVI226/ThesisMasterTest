# Microphone manipulation 1 — findings (server side)

Setup: uvicorn on 8001, `small` cuda/float16, Silero VAD loaded, **pyannote failed to load**
(`OneLoggerPTLTrainer.save_checkpoint: weights_only …`) while the startup log still printed
"✅ VAD and Diarization models loaded". Session logs: mic/sessions/*.jsonl; latency: mic/live_latency_mic.csv.
Historical `results/live_latency.csv` unchanged (sha256 25edc394…).

Four sessions (08:19–08:22), one speaker, French sentence
"Je souhaite changer mon adresse et confirmer mon numéro de compte."

| Claim | Status | Evidence |
|---|---|---|
| The full sentence reaches the screen | **verified** (user report + server log) | 7 utterances with the target sentence; 6 exact, 1 "numéro du contenu" |
| Frontend sends `__end__` on Stop and the server flushes | **verified end-to-end** | session 1: flush → `skipped empty_text` on 1 s residual; session 2: flush → utterance "Thank you." |
| The flush is what delivered the sentence | **not in this test** — every target sentence came through `trigger=silence` | human reaction time on Stop ≥ 0.6 s VAD window; flush proven separately on truncated audio (05b) |
| Language selected = language used | **contradicted, then fixed** — the live page had **no language selector**; all 4 sessions ran `lang=None` | backend accepts `?lang=` (manuscript is right about the backend); UI now exposes `liveLang`, injected into the URL at connect |
| Server-side latency | 0.63–1.24 s for 5–7 s utterances (n=8), GPU | live_latency_mic.csv |
| Packets | all 32 000 B = exactly 1 s of 16 kHz int16 | session_end.chunks |
| Diarization | **unavailable** in this environment; every speaker = SPEAKER_UNKNOWN | startup log |

Open points, not changed:
- **Hallucination on flush**: 1 s of residual audio after the sentence passed the VAD (>0.5) and the RMS guard,
  and Whisper produced "Thank you." A stricter guard on the flush path would also drop a genuine one-word ending
  ("Oui."). Decision left to the author.
- The startup message must not say "Diarization loaded" when the pipeline is None (audit item 10).
- The manuscript's "language is now a connection parameter (?lang=…)" is accurate for the backend; before today
  the demo UI could not set it without editing the URL. One sentence to have ready if asked.
