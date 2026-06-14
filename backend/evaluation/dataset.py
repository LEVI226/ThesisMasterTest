"""
Dataset loader for STT evaluation.
Reads metadata.csv mapping audio files to reference transcripts.
"""
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EvalSample:
    audio_filename: str
    reference_filename: str
    language: str
    noise_condition: str          # "clean", "noisy", "very_noisy"
    speaker_count: int
    notes: str = ""
    audio_path: Optional[Path] = field(default=None, repr=False)
    reference_path: Optional[Path] = field(default=None, repr=False)


def load_metadata(
    csv_path: str,
    audio_dir: Optional[str] = None,
    reference_dir: Optional[str] = None,
) -> list[EvalSample]:
    """
    Load evaluation samples from metadata.csv.

    Args:
        csv_path: Path to metadata.csv
        audio_dir: Base directory for audio files (defaults to datasets/stt_eval/audio)
        reference_dir: Base directory for reference files (defaults to datasets/stt_eval/references)

    Returns:
        List of EvalSample with resolved paths.

    Raises:
        FileNotFoundError: If csv_path does not exist.
        ValueError: If required columns are missing.
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {csv_path}")

    base = csv_file.parent
    audio_base = Path(audio_dir) if audio_dir else base / "audio"
    ref_base   = Path(reference_dir) if reference_dir else base / "references"

    required = {"audio_filename", "reference_filename", "language", "noise_condition", "speaker_count"}
    samples: list[EvalSample] = []

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("metadata.csv appears to be empty.")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"metadata.csv is missing required columns: {missing}")

        for i, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            try:
                sample = EvalSample(
                    audio_filename   = row["audio_filename"].strip(),
                    reference_filename = row["reference_filename"].strip(),
                    language         = row["language"].strip().lower(),
                    noise_condition  = row["noise_condition"].strip().lower(),
                    speaker_count    = int(row["speaker_count"]),
                    notes            = row.get("notes", "").strip(),
                    audio_path       = audio_base / row["audio_filename"].strip(),
                    reference_path   = ref_base   / row["reference_filename"].strip(),
                )
                samples.append(sample)
            except (KeyError, ValueError) as e:
                raise ValueError(f"Error parsing metadata.csv row {i}: {e}") from e

    return samples


def validate_samples(samples: list[EvalSample]) -> list[str]:
    """
    Check that audio and reference files exist.
    Returns list of warning messages (empty = all good).
    """
    warnings = []
    for s in samples:
        if s.audio_path and not s.audio_path.exists():
            warnings.append(f"Audio file not found: {s.audio_path}")
        if s.reference_path and not s.reference_path.exists():
            warnings.append(f"Reference file not found: {s.reference_path}")
    return warnings
