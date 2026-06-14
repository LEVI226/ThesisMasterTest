# STT Evaluation Dataset — Topic 2

This directory holds audio files and reference transcripts used for evaluating the
Speech-to-Text engine (faster-whisper) across different noise conditions and languages.

## Directory Structure

```
datasets/stt_eval/
  audio/          ← place .wav / .mp3 audio files here
  references/     ← place .txt reference transcripts here (one per audio file)
  metadata.csv    ← maps audio → reference, language, noise condition
```

## How to Add Files

1. Place audio files in `audio/` (WAV preferred, 16kHz mono).
2. Create a matching plain text file in `references/` with the exact transcript.
   - One reference per audio file.
   - Use UTF-8 encoding.
   - Include all words but no speaker labels.
3. Add a row to `metadata.csv`.

## metadata.csv Format

| Column | Type | Values | Description |
|---|---|---|---|
| audio_filename | string | e.g. `meeting_en_clean.wav` | Filename in audio/ |
| reference_filename | string | e.g. `meeting_en_clean.txt` | Filename in references/ |
| language | string | `en`, `fr`, `de` | Primary spoken language |
| noise_condition | string | `clean`, `noisy`, `very_noisy` | Recording environment |
| speaker_count | integer | 1, 2, 3… | Number of distinct speakers |
| notes | string | (optional) | Any additional notes |

## Privacy and Copyright

- Do **not** commit private, confidential, or copyrighted audio recordings.
- Use publicly available datasets such as:
  - [Mozilla Common Voice](https://commonvoice.mozilla.org/) (open license)
  - [LibriSpeech](https://www.openslr.org/12) (CC BY 4.0)
  - Own recordings of publicly available speeches (check copyright).
- For Nestlé-internal test cases, store files outside the repository and reference them by path in `.env`.

## Running the Evaluation

```bash
uv run python -m backend.evaluation.run_stt_eval \
    --metadata datasets/stt_eval/metadata.csv \
    --output results/stt_eval_results.csv \
    --report results/stt_evaluation_report.md
```
