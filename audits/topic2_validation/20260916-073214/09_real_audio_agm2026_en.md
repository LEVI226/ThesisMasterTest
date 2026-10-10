# 09 Real Nestlé audio — AGM 2026, Chair + CEO speeches (EN), file path

Source: "Nestlé Chair & CEO Annual General Meeting 2026 (EN).mp3", 30.5 MB, public webcast audio
(audioReunionréel/). Processed locally on 2026-09-16 via /transcribe: model `small` cuda/float16,
app defaults (preprocessing ON, Nestlé domain prompt ON, diarization loaded this time: 95.9 s).
Language auto-detected `en` (p=0.78). Audio 22:13. The UI's "⏱️ 1334s" is `duration_seconds`
(audio length), NOT processing time — processing time is returned by the API but never displayed.

**No WER**: no verified verbatim transcript exists for the 2026 AGM (the PDF in the folder is 2025;
PLAN_TESTS_ET_RETOUR forbids cross-year comparison). What follows is a qualitative reading.

## Named entities (public facts, checked by name)

| Spoken | Transcribed by `small` | Correct? |
|---|---|---|
| Philipp Navratil (CEO) | "Philip Navratil" / "Philip Nabratil" | ~ / no |
| Marie-Gabrielle Ineichen-Fleisch (vice-chair) | "Marie-Gabrielle in Agent Flash" | **no** — rendered as common words |
| Dick Boer | "Dick Boer" | yes |
| Paul Bulcke | "Paul Bulke" | no |
| Peter Brabeck-Letmathe | "Peter Brabeck Lemate" | no |
| Hanne de Mora | "Hanny de Mora" | no |
| Fama Francisco, Thomas Jordan, Pablo (Isla) | correct | yes |
| Inditex, Nescafé, Starbucks, Procter & Gamble, Swiss National Bank | correct | yes |
| "three francs and ten centimes" | "ten cent teams" | no |

People: 5 of 9 surnames wrong. Brands/institutions: 0 of 6 wrong.

## Reading against the thesis

- The static domain prompt contains brands only (Nestlé, Nespresso, Maggi, Purina, KitKat, Nescafé,
  supply chain, plant-based portfolio, Nestlé Ghana). Every brand in the speech is right; every
  unlisted person's name is at risk. This is the thesis's H2 point (a static prompt "cannot change
  weak acoustic evidence"; "aggregate WER can hide poor performance on named entities") shown on
  real Nestlé audio: the overall text reads fluently while the names an organisation cares about are wrong.
- Semantic slips a reader would not notice: "Delivering under expectations" (on), "we want to achieve
  success and failure" (own), "with a skill" (unclear). Same family as the silent translation seen in T4.
- No prompt leakage observed in 22 minutes of English (the "Nestlé Ghana" token did not appear).
- Diarization ran but the file UI does not show speaker turns; the chair→CEO handover (~12:02) is
  the natural check for T1 — not assessed here.

## Status

| Claim | Status |
|---|---|
| Pipeline handles a 22-minute real corporate speech end to end | **verified** (1 file) |
| Fluent, mostly correct English on real meeting audio | **observed**, unquantified (no reference) |
| Domain prompt protects Nestlé vocabulary | **partially contradicted** — protects listed brands, not people |
| Entity error rate on real Nestlé audio | ≈ 5/9 on surnames — **qualitative, 1 file, no verified reference** |
| UI shows processing time | **contradicted** — shows audio duration under a clock icon |

Reference for a future T2 measurement: an official 2026 verbatim, or a human transcription of this
file (22 min; public audio, can be outsourced), scored with entity recall alongside WER.
