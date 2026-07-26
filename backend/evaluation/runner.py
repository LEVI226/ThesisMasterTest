"""
STT evaluation runner.
Runs transcription experiments across multiple conditions and records metrics.
"""
import csv
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from backend.evaluation.metrics import wer, cer, rtf

logger = logging.getLogger(__name__)

TRANSCRIPT_DIR = Path("results/transcripts")


@dataclass
class EvalResult:
    filename: str
    language: str
    noise_condition: str
    speaker_count: int
    model: str
    preprocessing_enabled: bool
    domain_prompt_enabled: bool
    forced_language: Optional[str]
    duration_audio_seconds: float
    processing_time_seconds: float
    real_time_factor: float
    wer: float
    cer: float
    detected_language: str = ""
    transcript_output_path: str = ""
    reference_text: str = ""
    hypothesis_text: str = ""
    error: str = ""


def _read_reference(path: Path) -> str:
    """Read reference transcript from a plain text file."""
    return path.read_text(encoding="utf-8").strip()


def _save_transcript(filename: str, condition_tag: str, text: str) -> Path:
    """Save generated transcript to results/transcripts/."""
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(filename).stem
    out_path = TRANSCRIPT_DIR / f"{stem}__{condition_tag}.txt"
    out_path.write_text(text, encoding="utf-8")
    return out_path


def run_single(
    sample,                          # EvalSample
    preprocessing: bool = True,
    domain_prompt: bool = True,
    forced_language: Optional[str] = None,
    model_size: Optional[str] = None,
    vad: bool = False,
) -> EvalResult:
    """
    Run one transcription experiment for a single EvalSample.
    Imports the STT engine lazily to avoid loading Whisper at import time.
    """
    from backend.stt.engine import TranscribeConfig, transcribe_file, get_audio_duration

    cfg = TranscribeConfig(
        preprocessing  = preprocessing,
        domain_prompt  = domain_prompt,
        language       = forced_language,
        word_timestamps= False,          # not needed for evaluation
        vad            = vad,
    )
    if model_size:
        cfg.model_size = model_size

    audio_path = str(sample.audio_path)
    try:
        audio_dur = get_audio_duration(audio_path)
    except Exception:
        audio_dur = 0.0

    condition_tag = (
        f"prep{int(preprocessing)}_prompt{int(domain_prompt)}"
        f"_lang{forced_language or 'auto'}"
    )

    try:
        t0 = time.time()
        result = transcribe_file(audio_path, config=cfg)
        elapsed = time.time() - t0

        hypothesis    = result.get("text", "").strip()
        model_used    = result.get("model", "unknown")
        detected_lang = result.get("language", "")

        # Load reference
        ref_text = _read_reference(sample.reference_path) if sample.reference_path and sample.reference_path.exists() else ""

        w = wer(ref_text, hypothesis) if ref_text else float("nan")
        c = cer(ref_text, hypothesis) if ref_text else float("nan")
        r = rtf(audio_dur, elapsed)

        transcript_path = _save_transcript(sample.audio_filename, condition_tag, hypothesis)

        logger.info(
            "Evaluated %s | WER=%.3f | CER=%.3f | RTF=%.3f",
            sample.audio_filename, w, c, r,
        )

        return EvalResult(
            filename              = sample.audio_filename,
            language              = sample.language,
            noise_condition       = sample.noise_condition,
            speaker_count         = sample.speaker_count,
            model                 = model_used,
            preprocessing_enabled = preprocessing,
            domain_prompt_enabled = domain_prompt,
            forced_language       = forced_language,
            duration_audio_seconds= round(audio_dur, 2),
            processing_time_seconds=round(elapsed, 2),
            real_time_factor      = round(r, 4),
            wer                   = round(w, 4) if w == w else w,  # preserve NaN
            cer                   = round(c, 4) if c == c else c,
            detected_language     = detected_lang,
            transcript_output_path= str(transcript_path),
            reference_text        = ref_text,
            hypothesis_text       = hypothesis,
        )

    except Exception as exc:
        logger.error("Transcription failed for %s: %s", sample.audio_filename, exc)
        return EvalResult(
            filename              = sample.audio_filename,
            language              = sample.language,
            noise_condition       = sample.noise_condition,
            speaker_count         = sample.speaker_count,
            model                 = model_size or "unknown",
            preprocessing_enabled = preprocessing,
            domain_prompt_enabled = domain_prompt,
            forced_language       = forced_language,
            duration_audio_seconds= round(audio_dur, 2),
            processing_time_seconds= 0.0,
            real_time_factor      = float("inf"),
            wer                   = float("nan"),
            cer                   = float("nan"),
            transcript_output_path= "",
            error                 = str(exc),
        )


def run_evaluation(
    samples: list,
    output_csv: str,
    conditions: Optional[list[dict]] = None,
    model_size: Optional[str] = None,
) -> list[EvalResult]:
    """
    Run the full evaluation matrix across all samples and conditions.

    Args:
        samples: List of EvalSample objects.
        output_csv: Path to write results CSV.
        conditions: List of condition dicts with keys:
                    preprocessing, domain_prompt, forced_language.
                    Defaults to 4 standard conditions.
        model_size: Whisper model size override (e.g. "base", "small", "medium").

    Returns:
        List of EvalResult objects.
    """
    if conditions is None:
        conditions = [
            {"preprocessing": False, "domain_prompt": False, "forced_language": None},
            {"preprocessing": True,  "domain_prompt": False, "forced_language": None},
            {"preprocessing": True,  "domain_prompt": True,  "forced_language": None},
            {"preprocessing": True,  "domain_prompt": True,  "forced_language": "en"},
        ]

    all_results: list[EvalResult] = []
    total = len(samples) * len(conditions)
    done  = 0

    for sample in samples:
        for cond in conditions:
            done += 1
            logger.info("[%d/%d] %s | %s", done, total, sample.audio_filename, cond)
            result = run_single(
                sample,
                preprocessing  = cond.get("preprocessing", True),
                domain_prompt  = cond.get("domain_prompt", True),
                forced_language= cond.get("forced_language"),
                model_size     = model_size,
            )
            all_results.append(result)

    # Write CSV
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if all_results:
        fieldnames = [f for f in EvalResult.__dataclass_fields__ if f not in ("reference_text", "hypothesis_text")]
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in all_results:
                row = asdict(r)
                row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(row)
        logger.info("Results written to %s", output_csv)

    return all_results
