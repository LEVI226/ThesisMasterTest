# Re-annotation notes — 2026-09-16

Annotator: the author, listening, sheet without references or model outputs (07b). NOT fully blind: before
transcribing, the author had been shown the three-model hypotheses for the 5 priority clips and a word-level
triage summary for two controls (en_08 'um', fr_07 'vais'). The 9 other controls were transcribed without
prior exposure. No second annotator: the second listening of the priority clips is a second pass by the
same person, not an independent validation.
Coverage: 16/24 clean clips (all English and French). 8 German clips not annotated: no German
speaker available; they keep the published reference and are reported as **unverified**.

Result vs published references
- 7 differ: en_01, en_03, fr_03 (truncated in source); en_02, en_07 (mis-transcribed in source);
  en_08, fr_07 (disfluencies "um … um", "je vais veux" present in the audio, absent from the source).
- 9 identical: en_04, en_05, en_06, fr_01, fr_02, fr_04, fr_05, fr_06, fr_08.
- All 24 local references were verified identical to the published PolyAI/minds14 `transcription`
  field, so every difference above is a property of the published corpus for these clips.

Conventions
- Verbatim: hesitations and false starts are kept ("um", "je vais veux"). The canonical scorer
  does not strip disfluencies, so models that clean them are charged; this is stated, not hidden.
- Casing/punctuation irrelevant (normalised by the scorer). Numbers as spoken.

Intra-annotator variability (the 5 priority clips were listened to twice)
- fr_03: "je vais changer" (1st) vs "j'avais changé" (2nd; large-v3 agrees; published source agrees
  with the 1st). Genuinely ambiguous passage; 2nd kept, flagged in `uncertain_passages`.
- en_03: "Uh," present in 1st, dropped in 2nd. en_07: "Thank you" present in 1st, dropped in 2nd.
- Lesson: a single human pass is not exact either; a second independent listener on these three
  passages would settle them. Effect on aggregates is ≤ 1 word per clip.

Sensitivity of small effects to the reference version
- LoRA J0−J: +1.0 (original) → −0.1 (large-v3 wording) → −0.5 (5 human) → +0.6 (16 human).
  Every interval contains zero. The effect is indistinguishable from reference noise.

Status of figures in revision_v2/REVISION_v2.md
- Final for English and French; provisional for German; originals untouched.
