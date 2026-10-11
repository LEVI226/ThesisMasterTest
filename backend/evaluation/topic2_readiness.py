"""Audit the legacy live log without treating appended sessions as a fixed study.

Run: python -m backend.evaluation.topic2_readiness
Session boundaries are inferred from sequential utterance IDs, not timestamps.
"""

import argparse
import csv
import hashlib
import math
from pathlib import Path

from backend.evaluation.statistics import latency_summary


def summarize_sessions(rows):
    sessions = []
    previous_id = 0
    for row in rows:
        utterance_id = int(row["utterance_id"])
        latency = float(row["latency_seconds"])
        if not math.isfinite(latency) or latency < 0:
            raise ValueError("Latency must be finite and non-negative.")
        if utterance_id == 1:
            sessions.append({"cold_start": latency, "values": []})
        elif not sessions or utterance_id != previous_id + 1:
            raise ValueError("Cannot infer sessions from non-sequential utterance IDs.")
        else:
            sessions[-1]["values"].append(latency)
        previous_id = utterance_id
    return [
        {"cold_start": session["cold_start"],
         "steady": latency_summary(session["values"]) if session["values"] else None}
        for session in sessions
    ]


def build_report(path):
    raw = path.read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    sessions = summarize_sessions(rows)
    lines = [
        "# Topic 2: live latency evidence audit", "",
        f"Source: `{path.as_posix()}`; {len(rows)} observations.",
        f"SHA-256: `{hashlib.sha256(raw).hexdigest()}`.", "",
        "Sessions are inferred from utterance_id restarting at 1. The legacy CSV",
        "does not record timestamps, model, device, load or reference transcripts.",
        "Session comparability and live WER therefore cannot be established.", "",
        "| Inferred session | Cold start (s) | Steady n | Median (s) | p95 (s) | Max (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for index, session in enumerate(sessions, 1):
        stats = session["steady"]
        prefix = f"| {index} | {session['cold_start']:.3f} |"
        lines.append(
            prefix + f" {stats['n']} | {stats['median']:.3f} | {stats['p95']:.3f} | {stats['maximum']:.3f} |"
            if stats else prefix + " 0 | NA | NA | NA |"
        )
    steady = [float(row["latency_seconds"]) for row in rows if row["utterance_id"] != "1"]
    if steady:
        stats = latency_summary(steady)
        lines += ["", f"Pooled descriptive summary: n={stats['n']}, median={stats['median']:.3f} s, "
                  f"p95={stats['p95']:.3f} s, max={stats['maximum']:.3f} s."]
    lines += ["", "## Interpretation", "",
              "No slow observation is discarded. The first observation in each session is",
              "reported separately as the legacy cold-start proxy; loading itself was not isolated.",
              "The historical 22-row study covers the first two inferred sessions only.",
              "Appended sessions must not silently replace that study or be hidden by its summary.",
              "The timer excludes the configured silence window and does not establish browser",
              "render latency. Adding 0.6 s is an approximation, not a measured end-to-end result.", "",
              "A new controlled run must log run/session IDs, timestamp, model/device,",
              "endpointing configuration, final-speech time, endpoint time, server send time,",
              "browser receipt/render time and reference/hypothesis for the SAME utterance.",
              "Use monotonic durations; do not subtract unsynchronised client/server clocks.",
              "Report WER and latency together, retain failures, and compare identical audio",
              "across configurations with repeated trials. No accuracy/latency optimum is proven."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/live_latency.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/topic2_readiness_audit.md"))
    args = parser.parse_args()
    report = build_report(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
