"""Generate an auditable Markdown summary from a generic STT result CSV."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional


def _load_csv(csv_path: str) -> list[dict[str, str]]:
    with open(csv_path, newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _safe_float(value: object) -> Optional[float]:
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (ValueError, TypeError):
        return None


def _avg(values: list[Optional[float]]) -> Optional[float]:
    finite = [value for value in values if value is not None]
    return sum(finite) / len(finite) if finite else None


def _pct(value: Optional[float]) -> str:
    return f"{value * 100:.2f}%" if value is not None else "N/A"


def _fmt(value: Optional[float], decimals: int = 3) -> str:
    return f"{value:.{decimals}f}" if value is not None else "N/A"


def _is_true(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _condition_key(row: dict) -> tuple[str, str, str, str, str]:
    return (
        row.get("model", "?"),
        row.get("preprocessing_enabled", "False"),
        row.get("domain_prompt_enabled", "False"),
        row.get("vad_enabled", "False"),
        row.get("forced_language", ""),
    )


def generate_report(results_csv: str, output_path: str, hardware_notes: str = "") -> str:
    """Create descriptive tables without inventing causal research findings."""
    rows = _load_csv(results_csv)
    if not rows:
        raise ValueError(f"No results found in {results_csv}")

    for row in rows:
        for key in (
            "wer",
            "cer",
            "real_time_factor",
            "duration_audio_seconds",
            "processing_time_seconds",
        ):
            row[f"_{key}"] = _safe_float(row.get(key))

    grouped: dict[tuple[str, str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_condition_key(row)].append(row)
    labels = {key: f"C{index}" for index, key in enumerate(sorted(grouped), start=1)}

    lines: list[str] = [
        "# STT Evaluation Report — Topic 2",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Results file:** `{results_csv}`",
        "",
        "## Experiment setup",
        "",
        "| Condition | Model | Preprocessing | Prompt | VAD | Forced language |",
        "|---|---|---|---|---|---|",
    ]
    for key in sorted(grouped):
        model, preprocessing, prompt, vad, language = key
        lines.append(
            f"| {labels[key]} | {model} | "
            f"{'Yes' if _is_true(preprocessing) else 'No'} | "
            f"{'Yes' if _is_true(prompt) else 'No'} | "
            f"{'Yes' if _is_true(vad) else 'No'} | "
            f"{language if language and language != 'None' else 'Auto'} |"
        )
    if hardware_notes:
        lines.extend(["", "**Hardware:** " + hardware_notes])

    lines.extend(
        [
            "",
            "## Per-file results",
            "",
            "| File | Language | Noise | Condition | WER | CER | RTF | Error |",
            "|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        error = row.get("error", "").replace("|", "\\|")
        lines.append(
            f"| {row.get('filename', '?')} | {row.get('language', '?')} | "
            f"{row.get('noise_condition', '?')} | {labels[_condition_key(row)]} | "
            f"{_pct(row['_wer'])} | {_pct(row['_cer'])} | "
            f"{_fmt(row['_real_time_factor'])} | {error} |"
        )

    lines.extend(
        [
            "",
            "## Descriptive aggregation",
            "",
            "| Condition | Valid WER / rows | Mean WER | Mean CER | Mean RTF |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    condition_means: list[tuple[float, str]] = []
    for key in sorted(grouped):
        condition_rows = grouped[key]
        mean_wer = _avg([row["_wer"] for row in condition_rows])
        mean_cer = _avg([row["_cer"] for row in condition_rows])
        mean_rtf = _avg([row["_real_time_factor"] for row in condition_rows])
        valid = sum(row["_wer"] is not None for row in condition_rows)
        if mean_wer is not None:
            condition_means.append((mean_wer, labels[key]))
        lines.append(
            f"| {labels[key]} | {valid}/{len(condition_rows)} | {_pct(mean_wer)} | "
            f"{_pct(mean_cer)} | {_fmt(mean_rtf)} |"
        )

    valid_rows = [row for row in rows if row["_wer"] is not None]
    realtime_rows = [row for row in rows if row["_real_time_factor"] is not None]
    faster_count = sum(row["_real_time_factor"] < 1 for row in realtime_rows)
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            f"- Completeness: {len(valid_rows)}/{len(rows)} rows have a finite WER.",
            f"- Throughput: {faster_count}/{len(realtime_rows)} finite RTF measurements are below 1."
            if realtime_rows
            else "- Throughput: no finite RTF measurement is available.",
        ]
    )
    if condition_means:
        best_wer, best_label = min(condition_means)
        lines.append(f"- Lowest descriptive mean WER: {best_label} at {_pct(best_wer)}.")
    lines.extend(
        [
            "- These aggregates are descriptive. Intervention claims require matched filenames and paired or clustered uncertainty estimates.",
            "- RTF measures processing throughput, not complete user-perceived caption latency.",
            "- The report does not establish performance on corporate meetings, overlapping speakers, organisation-specific vocabulary, or accessibility outcomes.",
            "",
            "For the thesis inferential results, run "
            "`python -m backend.evaluation.run_statistical_audit` on the canonical CSVs.",
        ]
    )

    report = "\n".join(lines) + "\n"
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    return report
