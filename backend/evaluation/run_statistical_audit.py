"""Reproduce the corrected paired statistics reported in ``main_revised.tex``.

This script reads existing canonical CSVs only; it does not run ASR models.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from backend.evaluation.statistics import (
    BootstrapEstimate,
    ClusteredBootstrapEstimate,
    clustered_paired_bootstrap_difference,
    latency_summary,
    paired_bootstrap_difference,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _by_filename(rows: list[dict[str, str]], tag: str) -> dict[str, float]:
    selected = {
        row["filename"]: float(row["wer"])
        for row in rows
        if row.get("condition_tag") == tag and not row.get("error", "").strip()
    }
    if not selected:
        raise ValueError(f"No valid rows found for condition {tag!r}.")
    return selected


def _align(
    first: dict[str, float], second: dict[str, float]
) -> tuple[list[str], list[float], list[float]]:
    names = sorted(set(first) & set(second))
    if len(names) != len(first) or len(names) != len(second):
        raise ValueError("Compared conditions do not contain identical filenames.")
    return names, [first[name] for name in names], [second[name] for name in names]


def _source_utterance(filename: str) -> str:
    """Map a noise-augmented file back to its clean source utterance."""
    return filename.replace("_noisy_", "_clean_")


def _clustered_estimate(
    first: dict[str, float], second: dict[str, float]
) -> ClusteredBootstrapEstimate:
    names, a, b = _align(first, second)
    return clustered_paired_bootstrap_difference(
        a, b, [_source_utterance(name) for name in names]
    )


def _matched_noise(rows: list[dict[str, str]]) -> tuple[list[float], list[float]]:
    baseline = [
        row
        for row in rows
        if row.get("condition_tag") == "A_baseline"
        and not row.get("error", "").strip()
    ]
    clean = {
        row["filename"]: float(row["wer"])
        for row in baseline
        if row.get("noise_condition") == "clean"
    }
    noisy = {
        row["filename"]: float(row["wer"])
        for row in baseline
        if row.get("noise_condition") == "noisy"
    }
    clean_values = []
    noisy_values = []
    for noisy_name in sorted(noisy):
        clean_name = noisy_name.replace("_noisy_", "_clean_")
        if clean_name not in clean:
            raise ValueError(f"Missing clean pair for {noisy_name}.")
        clean_values.append(clean[clean_name])
        noisy_values.append(noisy[noisy_name])
    return clean_values, noisy_values


def build_audit(results_dir: Path) -> str:
    cpu_rows = _read_csv(results_dir / "stt_eval_pilot_results_CPU_baseline.csv")
    pilot_rows = _read_csv(results_dir / "stt_eval_pilot_results.csv")
    lora_rows = _read_csv(results_dir / "stt_eval_lora_results.csv")
    mms_rows = _read_csv(results_dir / "stt_eval_wav2vec_results.csv")
    conformer_rows = _read_csv(results_dir / "stt_eval_conformer_results.csv")
    latency_rows = _read_csv(results_dir / "live_latency.csv")

    clean, noisy = _matched_noise(cpu_rows)
    # Positive value means noise increases WER.
    noise = paired_bootstrap_difference(noisy, clean)

    tiny = _by_filename(pilot_rows, "B_noise_reduction")
    large = _by_filename(pilot_rows, "I_model_large_v3")
    size = _clustered_estimate(tiny, large)

    vanilla = _by_filename(lora_rows, "J0_small_hf_vanilla")
    adapted = _by_filename(lora_rows, "J_lora_small")
    lora = _clustered_estimate(vanilla, adapted)

    mms = _by_filename(mms_rows, "K_wav2vec")
    conformer = {
        row["filename"]: float(row["wer"])
        for row in conformer_rows
        if not row.get("error", "").strip()
    }
    architecture = _clustered_estimate(mms, conformer)

    cold_starts = [
        float(row["latency_seconds"])
        for row in latency_rows
        if row.get("utterance_id") == "1"
    ]
    steady = [
        float(row["latency_seconds"])
        for row in latency_rows
        if row.get("utterance_id") != "1"
    ]
    latency = latency_summary(steady)

    def points(value: float) -> float:
        return 100 * value

    lines = [
        "# Reproducible statistical audit",
        "",
        "All confidence intervals use 10,000 bootstrap resamples with seed 42. "
        "System comparisons resample the 24 independent source utterances as "
        "clusters; clean/noisy derivatives remain together.",
        "",
        "| Comparison | Source utterances | Files | Mean difference | 95% CI |",
        "|---|---:|---:|---:|---:|",
        (
            f"| Added noise (noisy - matched clean) | {noise.n_pairs} | "
            f"{2 * noise.n_pairs} | "
            f"{points(noise.mean_difference):.1f} WER points | "
            f"[{points(noise.ci_low):.1f}, {points(noise.ci_high):.1f}] |"
        ),
        (
            f"| Model size (tiny - large-v3) | {size.n_clusters} | "
            f"{size.n_observations} | "
            f"{points(size.mean_difference):.1f} WER points | "
            f"[{points(size.ci_low):.1f}, {points(size.ci_high):.1f}] |"
        ),
        (
            f"| LoRA (vanilla - adapted) | {lora.n_clusters} | "
            f"{lora.n_observations} | "
            f"{points(lora.mean_difference):.1f} WER points | "
            f"[{points(lora.ci_low):.1f}, {points(lora.ci_high):.1f}] |"
        ),
        (
            f"| Architecture (MMS - Conformer) | {architecture.n_clusters} | "
            f"{architecture.n_observations} | "
            f"{points(architecture.mean_difference):.1f} WER points | "
            f"[{points(architecture.ci_low):.1f}, {points(architecture.ci_high):.1f}] |"
        ),
        "",
        "## Live latency",
        "",
        (
            f"Cold starts are rows whose per-session utterance_id equals 1 "
            f"(n={len(cold_starts)}; values: "
            + ", ".join(f"{value:.3f} s" for value in cold_starts)
            + ")."
        ),
        "",
        (
            f"Steady-state post-endpointing latency (n={latency['n']}): "
            f"median {latency['median']:.3f} s, p95 {latency['p95']:.3f} s, "
            f"maximum {latency['maximum']:.3f} s."
        ),
        "",
        "The fixed 0.6 s VAD silence window is not included in these processing latencies.",
    ]
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/statistical_audit_revised.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_audit(args.results_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
