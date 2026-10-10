# 09c AGM 2026 replayed through the live path (loudspeaker → microphone, auto language)

Session live_20260916T175115_35f5db, `small` cuda/float16, VAD, pyannote loaded. The 11:10–15:30
stretch of the AGM was played on speakers into the laptop microphone. Caveat: re-recorded acoustics,
not the file; the language mechanism is what is under test.

| Claim | Status | Evidence |
|---|---|---|
| Per-utterance language decision keeps the trilingual greeting | **verified** — utterance detected `de` (p=0.66); German correct, English kept, French rendered through the German token ("und merci, Scherz-Aktionär, der hier zu sein"). File path (09b) dropped it entirely | session log + server log |
| Live path handles a 3-language utterance perfectly | **contradicted** — one token per utterance still; the French half is garbled | idem |
| Utterance length is bounded on the live path | **contradicted** — fluent speech without ≥0.6 s pauses produced silence-triggered utterances of 35, 25, 30 and 70 s (latency 4.3 / 2.6 / 3.7 / 8.3 s) and a **149 s** block that was closed only by the user's Stop (`end_signal`, 13.6 s decode); RTF ≈ 0.1 | idem |
| Server-side post-endpointing latency is the caption delay | **contradicted for fluent speakers** — the caption appears only after the utterance ends; on continuous speech the live path degenerates into batch mode | idem |
| Diarization separates chair and CEO | **not assessable** — both voices came through the same loudspeaker/mic; SPEAKER_00 for all 8 | — |
| Domain terms | "pet care" → "tech care"; "Philippe Naprati" (third spelling of Navratil across systems) | screen |

Recommendation (not implemented): a maximum utterance length on the live path (e.g. force a cut at
10–15 s of continuous speech, or a streaming decoder) — a product change that would alter the
latency semantics described in the manuscript; to be decided by the author.
