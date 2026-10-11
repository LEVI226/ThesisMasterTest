"""Build the evidence payload used by the Topic 2 research dashboard.

The browser receives already-computed summaries.  It never recomputes thesis
metrics or silently combines incompatible experimental conditions.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Any

from backend.evaluation.run_statistical_audit import (
    _by_filename,
    _clustered_estimate,
    _matched_noise,
    _read_csv,
)
from backend.evaluation.statistics import latency_summary, paired_bootstrap_difference


RESULT_FILES = (
    "stt_eval_pilot_results_CPU_baseline.csv",
    "stt_eval_pilot_results.csv",
    "stt_eval_lora_results.csv",
    "stt_eval_wav2vec_results.csv",
    "stt_eval_conformer_results.csv",
    "meeting_eval_results.csv",
    "live_latency.csv",
)


def _valid(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if not row.get("error", "").strip()]


def _mean(rows: list[dict[str, str]], field: str) -> float:
    values = [float(row[field]) for row in _valid(rows) if row.get(field, "").strip()]
    if not values:
        raise ValueError(f"No valid values for {field!r}.")
    return fmean(values)


def _condition(rows: list[dict[str, str]], tag: str) -> list[dict[str, str]]:
    selected = [row for row in rows if row.get("condition_tag") == tag]
    if not selected:
        raise ValueError(f"No rows found for condition {tag!r}.")
    return selected


def _points(value: float) -> float:
    return round(100 * value, 1)


def _source(path: str, selector: str, description: str) -> dict[str, str]:
    return {"path": path, "selector": selector, "description": description}


def _comparison(
    *,
    comparison_id: str,
    label: str,
    estimate: Any,
    interpretation: str,
    sources: list[dict[str, str]],
) -> dict[str, Any]:
    if hasattr(estimate, "n_observations"):
        observations = estimate.n_observations
        clusters = estimate.n_clusters
    else:
        observations = 2 * estimate.n_pairs
        clusters = estimate.n_pairs
    return {
        "id": comparison_id,
        "label": label,
        "mean_difference_points": _points(estimate.mean_difference),
        "ci95_points": [_points(estimate.ci_low), _points(estimate.ci_high)],
        "source_utterances": clusters,
        "files": observations,
        "resamples": estimate.n_resamples,
        "seed": estimate.seed,
        "interpretation": interpretation,
        "sources": sources,
    }


def build_research_dashboard(results_dir: Path = Path("results")) -> dict[str, Any]:
    """Return a JSON-serialisable, provenance-rich Topic 2 evidence summary."""
    paths = {name: results_dir / name for name in RESULT_FILES}
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing dashboard evidence: " + ", ".join(missing))

    cpu = _read_csv(paths["stt_eval_pilot_results_CPU_baseline.csv"])
    pilot = _read_csv(paths["stt_eval_pilot_results.csv"])
    lora = _read_csv(paths["stt_eval_lora_results.csv"])
    mms = _read_csv(paths["stt_eval_wav2vec_results.csv"])
    conformer = _read_csv(paths["stt_eval_conformer_results.csv"])
    meetings = _read_csv(paths["meeting_eval_results.csv"])
    latency = _read_csv(paths["live_latency.csv"])

    clean, noisy = _matched_noise(cpu)
    noise_estimate = paired_bootstrap_difference(noisy, clean)
    model_size_estimate = _clustered_estimate(
        _by_filename(pilot, "B_noise_reduction"),
        _by_filename(pilot, "I_model_large_v3"),
    )
    lora_estimate = _clustered_estimate(
        _by_filename(lora, "J0_small_hf_vanilla"),
        _by_filename(lora, "J_lora_small"),
    )
    conformer_by_file = {
        row["filename"]: float(row["wer"])
        for row in _valid(conformer)
        if row.get("wer", "").strip()
    }
    architecture_estimate = _clustered_estimate(
        _by_filename(mms, "K_wav2vec"), conformer_by_file
    )

    cold_starts = [
        float(row["latency_seconds"])
        for row in latency
        if row.get("utterance_id") == "1"
    ]
    steady_latency = [
        float(row["latency_seconds"])
        for row in latency
        if row.get("utterance_id") != "1"
    ]
    live = latency_summary(steady_latency)
    diarization_der = _mean(meetings, "der")

    model_series = [
        {
            "label": "Whisper small",
            "detail": "Vanilla, automatic language detection",
            "wer_percent": _points(_mean(_condition(lora, "J0_small_hf_vanilla"), "wer")),
        },
        {
            "label": "Whisper small + LoRA",
            "detail": "Adapted on the available training split",
            "wer_percent": _points(_mean(_condition(lora, "J_lora_small"), "wer")),
        },
        {
            "label": "MMS / wav2vec 2.0",
            "detail": "Language supplied",
            "wer_percent": _points(_mean(_condition(mms, "K_wav2vec"), "wer")),
        },
        {
            "label": "Conformer",
            "detail": "Language-specific checkpoints",
            "wer_percent": _points(_mean(conformer, "wer")),
        },
    ]

    model_ladder = [
        {
            "label": label,
            "wer_percent": _points(_mean(_condition(pilot, tag), "wer")),
        }
        for label, tag in (
            ("tiny", "B_noise_reduction"),
            ("base", "F_model_base"),
            ("small", "G_model_small"),
            ("medium", "H_model_medium"),
            ("large-v3", "I_model_large_v3"),
        )
    ]

    audit_path = results_dir / "statistical_audit_revised.md"
    newest_source_mtime = max(path.stat().st_mtime for path in paths.values())
    audit_is_stale = not audit_path.exists() or audit_path.stat().st_mtime < newest_source_mtime
    latest_source = max(paths.values(), key=lambda path: path.stat().st_mtime)

    common_method = {
        "estimator": "Paired percentile bootstrap; clustered by independent source utterance for system comparisons",
        "confidence_level": "95%",
        "resamples": 10_000,
        "seed": 42,
    }

    return {
        "meta": {
            "title": "Topic 2 Research Evidence",
            "study_status": "Preliminary academic prototype",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "audit_status": "configuration_mismatch" if audit_is_stale else "current",
            "audit_note": (
                f"{latest_source.as_posix()} is newer than the published statistical audit. "
                "Dashboard summaries use the current CSV files."
                if audit_is_stale
                else "The published statistical audit is current with the canonical CSV files."
            ),
            "method": common_method,
        },
        "scope": {
            "languages": ["English", "French", "German"],
            "primary_corpus": "MInDS-14 telephone banking speech with synthetic-noise derivatives",
            "corpus_warning": "This is not a representative corporate meeting benchmark.",
            "independent_source_utterances": 24,
            "meeting_samples": len(meetings),
            "live_latency_observations": len(latency),
        },
        "research_questions": [
            {
                "id": "rq1",
                "nav_label": "RQ1 · Robustness",
                "question": "How robust are advanced STT architectures to multilingual speech and added noise?",
                "verdict": "Supported within the pilot scope",
                "verdict_tone": "supported",
                "summary": (
                    f"Added noise increased WER by {_points(noise_estimate.mean_difference):.1f} points on matched utterances. "
                    "Model choice also produced material differences, but the corpus remains narrow."
                ),
                "headline_metric": {
                    "value": _points(noise_estimate.mean_difference),
                    "unit": "WER points",
                    "label": "matched noise penalty",
                    "ci": [_points(noise_estimate.ci_low), _points(noise_estimate.ci_high)],
                },
                "series_title": "Cross-architecture mean WER",
                "series_note": "Descriptive overview. Direct inferential claims use matched comparisons below.",
                "series": model_series,
                "comparisons": [
                    _comparison(
                        comparison_id="noise-penalty",
                        label="Added noise − matched clean",
                        estimate=noise_estimate,
                        interpretation="The interval remains above zero, supporting a substantial noise penalty in this pilot.",
                        sources=[
                            _source(
                                "results/stt_eval_pilot_results_CPU_baseline.csv",
                                "condition_tag=A_baseline; matched clean/noisy filenames",
                                "Per-file WER used for the paired comparison.",
                            )
                        ],
                    ),
                    _comparison(
                        comparison_id="model-size",
                        label="Whisper tiny − large-v3",
                        estimate=model_size_estimate,
                        interpretation="The interval remains above zero; larger Whisper variants reduced WER on these files.",
                        sources=[
                            _source(
                                "results/stt_eval_pilot_results.csv",
                                "B_noise_reduction vs I_model_large_v3",
                                "Matched model-size evaluation with clustered resampling.",
                            )
                        ],
                    ),
                    _comparison(
                        comparison_id="architecture",
                        label="MMS − Conformer",
                        estimate=architecture_estimate,
                        interpretation="Conformer produced lower mean WER than MMS on the matched files and supplied-language setup.",
                        sources=[
                            _source("results/stt_eval_wav2vec_results.csv", "condition_tag=K_wav2vec", "MMS per-file WER."),
                            _source("results/stt_eval_conformer_results.csv", "all valid rows", "Conformer per-file WER."),
                        ],
                    ),
                ],
                "limitation": "MInDS-14 contains short telephone banking utterances, not overlapping multilingual corporate meetings.",
            },
            {
                "id": "rq2",
                "nav_label": "RQ2 · Adaptation",
                "question": "Do preprocessing, model scale, or domain adaptation materially improve transcription accuracy?",
                "verdict": "Mixed evidence",
                "verdict_tone": "mixed",
                "summary": (
                    "Model scale produced the clearest improvement. The observed LoRA gain was small and its confidence interval crossed zero."
                ),
                "headline_metric": {
                    "value": _points(lora_estimate.mean_difference),
                    "unit": "WER point",
                    "label": "vanilla − adapted Whisper small",
                    "ci": [_points(lora_estimate.ci_low), _points(lora_estimate.ci_high)],
                },
                "series_title": "Whisper model-size ladder",
                "series_note": "Mean WER by matched condition; lower is better.",
                "series": model_ladder,
                "comparisons": [
                    _comparison(
                        comparison_id="lora",
                        label="Vanilla Whisper small − LoRA adapted",
                        estimate=lora_estimate,
                        interpretation="The confidence interval crosses zero; this experiment does not establish a reliable LoRA benefit.",
                        sources=[
                            _source(
                                "results/stt_eval_lora_results.csv",
                                "J0_small_hf_vanilla vs J_lora_small",
                                "Matched vanilla and adapted per-file WER.",
                            ),
                            _source(
                                "results/lora_training_log.csv",
                                "all steps",
                                "Training-loss trace for the adaptation run.",
                            ),
                        ],
                    ),
                    _comparison(
                        comparison_id="model-scale",
                        label="Whisper tiny − large-v3",
                        estimate=model_size_estimate,
                        interpretation="Model scale had a much larger measured effect than the tested LoRA adaptation.",
                        sources=[
                            _source(
                                "results/stt_eval_pilot_results.csv",
                                "B_noise_reduction vs I_model_large_v3",
                                "Matched model-size evaluation.",
                            )
                        ],
                    ),
                ],
                "limitation": "The adaptation split is small and domain transfer was not validated on a held-out corporate meeting corpus.",
            },
            {
                "id": "rq3",
                "nav_label": "RQ3 · Real-time",
                "question": "Can the prototype support accessible meeting captions with acceptable latency and speaker separation?",
                "verdict": "Feasible with material caveats",
                "verdict_tone": "caution",
                "summary": (
                    f"Current steady-state post-endpointing latency has a median of {live['median']:.3f} s and p95 of {live['p95']:.3f} s. "
                    "A fixed 0.6 s silence window is additional, and diarization remains weak."
                ),
                "headline_metric": {
                    "value": round(live["p95"], 3),
                    "unit": "seconds",
                    "label": "steady-state p95 after endpointing",
                    "ci": None,
                },
                "series_title": "Current latency profile",
                "series_note": "Processing latency excludes the fixed 0.6 s VAD silence window.",
                "series": [
                    {"label": "Median", "detail": f"n={live['n']} steady-state segments", "wer_percent": round(live["median"], 3), "display_unit": "s"},
                    {"label": "p95", "detail": "Linear percentile", "wer_percent": round(live["p95"], 3), "display_unit": "s"},
                    {"label": "Maximum", "detail": "Includes observed outliers", "wer_percent": round(live["maximum"], 3), "display_unit": "s"},
                    {"label": "Mean DER", "detail": f"n={len(meetings)} limited meeting clips", "wer_percent": round(100 * diarization_der, 1), "display_unit": "%"},
                ],
                "comparisons": [
                    {
                        "id": "latency",
                        "label": "Steady-state post-endpointing latency",
                        "mean_difference_points": round(live["median"], 3),
                        "ci95_points": None,
                        "source_utterances": live["n"],
                        "files": len(latency),
                        "resamples": None,
                        "seed": None,
                        "interpretation": f"Median {live['median']:.3f} s; p95 {live['p95']:.3f} s; maximum {live['maximum']:.3f} s. Cold starts are reported separately.",
                        "sources": [
                            _source("results/live_latency.csv", "utterance_id != 1", "Current steady-state latency observations."),
                            _source("backend/main.py", "RealTimeSTTHandler.silence_threshold", "Fixed 0.6 s VAD endpointing window."),
                        ],
                    },
                    {
                        "id": "diarization",
                        "label": "Meeting diarization error rate",
                        "mean_difference_points": round(100 * diarization_der, 1),
                        "ci95_points": None,
                        "source_utterances": len(meetings),
                        "files": len(meetings),
                        "resamples": None,
                        "seed": None,
                        "interpretation": "The mean DER is descriptive only and is too high to claim reliable speaker attribution.",
                        "sources": [
                            _source("results/meeting_eval_results.csv", "all rows", "DER, misses, false alarms, and confusion by meeting clip.")
                        ],
                    },
                ],
                "limitation": "The live path performs VAD-segmented batch inference rather than native frame-synchronous streaming; diarization clips contain sequential turns and no overlap.",
            },
        ],
        "methods": {
            "metrics": [
                {"name": "WER", "definition": "(substitutions + deletions + insertions) / reference words"},
                {"name": "CER", "definition": "Character-level edit error rate after normalisation"},
                {"name": "RTF", "definition": "processing time / audio duration; values below 1 are faster than real time"},
                {"name": "DER", "definition": "missed speech + false alarm + speaker confusion over scored time"},
            ],
            "bootstrap": common_method,
            "cold_starts_seconds": [round(value, 3) for value in cold_starts],
            "canonical_files": [path.as_posix() for path in paths.values()],
        },
        "limitations": [
            "No completed study with hearing-impaired participants is available.",
            "No representative multilingual corporate meeting benchmark has been completed.",
            "Synthetic noise does not cover the acoustic diversity of real meeting rooms.",
            "Persistent speaker identity and overlapping speech remain unvalidated.",
            "Results support an academic prototype, not production deployment or clinical accessibility claims.",
        ],
    }
