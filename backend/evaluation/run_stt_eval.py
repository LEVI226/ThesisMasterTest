"""
CLI entry point for STT evaluation.

Usage:
    uv run python -m backend.evaluation.run_stt_eval \\
        --metadata datasets/stt_eval/metadata.csv \\
        --output results/stt_eval_results.csv \\
        [--model small] \\
        [--report results/stt_evaluation_report.md]
"""
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("stt-eval")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run STT evaluation experiments for Topic 2 Master Thesis."
    )
    parser.add_argument(
        "--metadata", required=True,
        help="Path to metadata.csv (e.g. datasets/stt_eval/metadata.csv)",
    )
    parser.add_argument(
        "--output", default="results/stt_eval_results.csv",
        help="Path to write results CSV (default: results/stt_eval_results.csv)",
    )
    parser.add_argument(
        "--model", default=None,
        help="Whisper model size override: tiny, base, small, medium, large-v3",
    )
    parser.add_argument(
        "--report", default=None,
        help="If set, generate a Markdown report at this path.",
    )
    parser.add_argument(
        "--audio-dir", default=None,
        help="Override audio directory (default: metadata CSV parent / audio/)",
    )
    parser.add_argument(
        "--ref-dir", default=None,
        help="Override reference directory (default: metadata CSV parent / references/)",
    )
    parser.add_argument(
        "--hardware-notes", default="",
        help="Hardware description string to include in the report.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    from backend.evaluation.dataset import load_metadata, validate_samples
    from backend.evaluation.runner import run_evaluation

    logger.info("Loading metadata from %s", args.metadata)
    try:
        samples = load_metadata(args.metadata, args.audio_dir, args.ref_dir)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to load metadata: %s", e)
        sys.exit(1)

    warnings = validate_samples(samples)
    for w in warnings:
        logger.warning(w)

    if not samples:
        logger.error("No samples found in metadata CSV. Aborting.")
        sys.exit(1)

    missing_audio = [s for s in samples if s.audio_path and not s.audio_path.exists()]
    if missing_audio:
        logger.warning(
            "%d sample(s) have missing audio files and will fail during evaluation.",
            len(missing_audio),
        )

    logger.info("Starting evaluation: %d samples", len(samples))
    results = run_evaluation(
        samples   = samples,
        output_csv= args.output,
        model_size= args.model,
    )

    logger.info(
        "Evaluation complete: %d results written to %s",
        len(results), args.output,
    )

    if args.report:
        from backend.evaluation.report import generate_report
        logger.info("Generating report at %s", args.report)
        try:
            generate_report(args.output, args.report, args.hardware_notes)
            logger.info("Report written to %s", args.report)
        except Exception as e:
            logger.error("Report generation failed: %s", e)


if __name__ == "__main__":
    main()
