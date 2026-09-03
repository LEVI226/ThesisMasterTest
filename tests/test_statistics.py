import csv
from pathlib import Path

import pytest

from backend.evaluation.run_statistical_audit import build_audit
from backend.evaluation.statistics import (
    clustered_paired_bootstrap_difference,
    latency_summary,
    paired_bootstrap_difference,
)


def test_paired_bootstrap_is_deterministic_for_constant_difference():
    estimate = paired_bootstrap_difference([0.4, 0.5, 0.6], [0.2, 0.3, 0.4])
    assert estimate.mean_difference == pytest.approx(0.2)
    assert estimate.ci_low == pytest.approx(0.2)
    assert estimate.ci_high == pytest.approx(0.2)
    assert estimate.n_pairs == 3
    assert estimate.n_resamples == 10_000
    assert estimate.seed == 42


@pytest.mark.parametrize(
    "first,second",
    [([], []), ([1.0], []), ([1.0, float("nan")], [1.0, 2.0])],
)
def test_paired_bootstrap_rejects_invalid_pairs(first, second):
    with pytest.raises(ValueError):
        paired_bootstrap_difference(first, second)


def test_latency_summary_uses_linear_percentile():
    summary = latency_summary([0.1, 0.2, 0.3, 0.4])
    assert summary["n"] == 4
    assert summary["median"] == pytest.approx(0.25)
    assert summary["p95"] == pytest.approx(0.385)
    assert summary["maximum"] == pytest.approx(0.4)


def test_clustered_bootstrap_preserves_related_files():
    estimate = clustered_paired_bootstrap_difference(
        [0.4, 0.6, 0.8], [0.2, 0.4, 0.5], ["source-1", "source-1", "source-2"]
    )
    assert estimate.mean_difference == pytest.approx(0.7 / 3)
    assert estimate.n_observations == 3
    assert estimate.n_clusters == 2


def test_statistical_audit_reproduces_corrected_results():
    report = build_audit(Path("results"))
    assert "Added noise (noisy - matched clean) | 12 | 24 | 35.3 WER points" in report
    assert "Model size (tiny - large-v3) | 24 | 36 | 37.6 WER points" in report
    assert "LoRA (vanilla - adapted) | 24 | 36 | 1.0 WER points" in report
    assert "Architecture (MMS - Conformer) | 24 | 36 | 9.1 WER points" in report
    with Path("results/live_latency.csv").open(encoding="utf-8-sig", newline="") as stream:
        latency_rows = list(csv.DictReader(stream))
    current = latency_summary(
        float(row["latency_seconds"])
        for row in latency_rows
        if row["utterance_id"] != "1"
    )
    assert (
        f"median {current['median']:.3f} s, p95 {current['p95']:.3f} s, "
        f"maximum {current['maximum']:.3f} s"
    ) in report
