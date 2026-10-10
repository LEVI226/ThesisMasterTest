# 00 Inventory and audit frame

Run id: see directory name. Auditor: Claude Opus 5, executed locally, read-only
on all canonical artefacts. No CSV, audio, model or historical result was modified.

## Repository state

- Root: `C:/Users/ulric/Documents/ThesisMasterTest`
- Branch: `main`
- Commit: `f62705a2f4c1298a8a3089f2cf2fbccc5edf99eb`
- Working tree: dirty (9 modified, 11 untracked). The audit ran against the
  working tree, not the commit.

## Environment (inspected, not modified)

| component | version |
|---|---|
| Python | 3.13.7 (`.venv`) |
| torch | 2.6.0+cu124 |
| faster-whisper | 1.2.1 |
| CTranslate2 | 4.7.1 |
| transformers | 5.3.0 |
| peft | 0.19.1 |
| NeMo | 3.0.0 |
| pyannote.audio | 4.0.4 |
| CUDA device | NVIDIA GeForce RTX 4060 Laptop GPU, available |

Two environment defects, neither affecting the recalculation:

1. `torchcodec` fails to load (`libtorchcodec_core{4..8}.dll` missing; FFmpeg
   shared libraries absent). Built-in audio decoding through torchcodec is
   therefore unavailable. pyannote emits this warning on import.
2. `jiwer` is NOT installed. Prompt 3 asks for a comparison against an
   independent implementation "if one is already available". None is.
   Nothing was installed. The cross-check was performed instead by
   reimplementing the scorer (see `recalc.py`), not by adding a dependency.

## What was NOT executed

- No new transcription campaign, no training, no model download.
- No real-audio inference on `audioReunionréel/` (authorisation not established).
- No LaTeX build (no local TeX distribution with babel-french/biblatex).
