# Microphone manipulation 2 — German, non-native speaker, auto vs forced

Same speaker (native French, non-native German), same sentence
"Ich möchte gerne Geld auf mein Konto einzahlen", model `small` cuda/float16, live path.
Reference for scoring: MInDS-14 `minds14_de_clean_01` text (canonical scorer, backend/evaluation/metrics.py).
Sessions: live_20260916T083119 (lang=None, 7 utterances) · live_20260916T083658 (lang='de', 3 utterances).
Session B carries `lang='de'` in its header and the server log shows **no** "Detected language" line during it.

| mode | n | WER mean / median | CER mean | latency median / max | server RTF max | scripts observed |
|---|---|---|---|---|---|---|
| auto | 7 | 1.02 / 1.00 | 0.64 | 3.25 s / **14.16 s** | **1.18** | Latin, IPA (2×), English, Nynorsk; `de` once at p=0.58 |
| forced `de` | 3 | 0.75 / 0.88 | 0.37 | 0.69 s / 0.88 s | 0.12 | German only |

What forcing the language did and did not do:
- **Did**: removed every wrong-script output (IPA, Latin, English); cut CER from 0.64 to 0.37;
  cut median latency by ~5× and max by ~16×; brought every utterance well under real time.
- **Did not**: fix accent-driven word errors — "möchte" → "murte/Morte/Horte", "einzahlen" →
  "Heisland/Heselen/Eisenhalle" in all three forced runs. WER stays high (0.38–1.00).

Mechanism visible in the log: in auto mode, low language confidence (p 0.23–0.60) leads to long
hallucinated decodes (12 s audio → 14.2 s latency, RTF 1.18). This is the same failure family as the
11.0 s maximum in the historical extended log, now reproduced with its cause identified.

Claims:
| Claim | Status | Evidence |
|---|---|---|
| Forced language repairs wrong-script output on the live path (H4) | **verified**, 1 speaker, 1 sentence, 10 utterances | both sessions |
| Forced language reduces live latency on accented speech | **verified** (directional, n=7 vs 3) | latency columns |
| Forced language fixes accent-driven word errors | **contradicted** — WER remains 0.38–1.00 | forced session |
| Live RTF < 1 for every utterance | **contradicted** — one utterance at 1.18 in auto mode | utterance 1, session A |
| Auto detection is usable for non-native German with `small` | **contradicted** — 1/7 detections `de`, at p=0.58 | server.log |

Limits: one non-native speaker, one sentence, one model, one microphone, no repetition across days.
These are pilot observations that illustrate the manuscript's H4 and RQ3 discussion; they are not a
new statistical result and must not be reported as one.
