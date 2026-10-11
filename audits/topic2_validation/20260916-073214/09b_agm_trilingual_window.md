# 09b AGM 2026 — the trilingual handover (11:50–12:30): why 16.6 s vanished

On the full 22-min file, Whisper `small` (auto) left no segment between 12:01.8 and 12:18.4.
An external transcript (ElevenLabs Scribe v2, public audio only) shows the CEO opened in French
and German: "Merci, Pablo, et merci chers actionnaires…" / "Liebe Aktionärinnen und Aktionäre…".
Local test on the isolated 40-s window (09b_agm_window_models.json):

| model | language | detected | FR + DE greeting |
|---|---|---|---|
| small | auto | de | correct, both |
| large-v3 | auto | en | **dropped** (one 21-s segment "welcome everyone…") |
| small | forced fr | fr | everything translated into French |
| small | forced de | de | correct |

Mechanism: faster-whisper's file path detects the language once (first 30 s) and decodes the whole
file with that token. Chair speaks English at 0:00 → `en` → the CEO's FR/DE opening 12 min later is
silently dropped. Not a model-size effect (large-v3 identical). Same failure family as T4
(08_codeswitch_live.json): drop or silent translation, never an error message.

Implications
- Manuscript sentence "one language decision per processed segment" is exact; on the file path the
  segment is the whole file. For multilingual meetings this is a design limit of the file path.
- The live path decides per VAD utterance; T4 en→fr succeeded that way. A live replay of this window
  is the natural check (not done).
- No system spelled "Philipp Navratil" correctly (small: Philip/Nabratil; large-v3: philip navratil;
  Scribe: Philippe/Nabkhal). Names remain the risk zone regardless of vendor.
- External services: acceptable for this public AGM file only; internal .m4a recordings must stay local.

Status: verified failure mode on real Nestlé audio (1 file, 1 window); mechanism established by
controlled local runs; no WER (no verified reference).
