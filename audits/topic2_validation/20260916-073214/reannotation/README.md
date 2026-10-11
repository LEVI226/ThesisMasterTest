# Blind re-annotation of the 24 clean MInDS-14 clips

Rules
- Listen first, write what you hear, verbatim (hesitations included, "um"/"euh"). Do NOT read the current
  reference or any model output before writing: the sheet deliberately shows neither.
- Mark anything you are not sure of in `uncertain_passages` (write the words with a `?`).
- Casing and punctuation do not matter (the scorer normalises them). Numbers as spoken.
- Fill `annotator` (your name) and `date`. One row per clip; do the 5 PRIORITY rows first, then all controls.
- German rows are marked `needs_other_person`: leave them blank; a German-competent annotator fills them.
- A second, independent listener on the 5 priority clips is desirable; add their version in `notes` if it differs.

After filling: run `python audits/topic2_validation/20260916-073214/reannotation/ingest_sheet.py`
It versions each transcription under `reannotation/references_v2/`, logs annotator/date/reason, and compares
against the original reference. Originals in `datasets/stt_eval/references/` are never modified.
