"""Statistical helpers for paired STT evaluation results.

The evaluation design reuses the same utterances across systems, so uncertainty
must be estimated from per-utterance differences rather than independent groups.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class BootstrapEstimate:
    """Mean paired difference and percentile-bootstrap confidence interval."""

    mean_difference: float
    ci_low: float
    ci_high: float
    n_pairs: int
    n_resamples: int
    seed: int


@dataclass(frozen=True)
class ClusteredBootstrapEstimate:
    """Mean difference with resampling at the independent-source level."""

    mean_difference: float
    ci_low: float
    ci_high: float
    n_observations: int
    n_clusters: int
    n_resamples: int
    seed: int


def paired_bootstrap_difference(
    values_a: Iterable[float],
    values_b: Iterable[float],
    *,
    n_resamples: int = 10_000,
    seed: int = 42,
) -> BootstrapEstimate:
    """Estimate mean(A - B) with a paired non-parametric bootstrap."""
    a = np.asarray(list(values_a), dtype=float)
    b = np.asarray(list(values_b), dtype=float)
    if a.ndim != 1 or b.ndim != 1 or len(a) != len(b):
        raise ValueError("Paired samples must be one-dimensional and equally sized.")
    if len(a) == 0:
        raise ValueError("At least one paired observation is required.")
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive.")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Paired samples must contain only finite values.")

    differences = a - b
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(differences), size=(n_resamples, len(differences)))
    bootstrap_means = differences[indices].mean(axis=1)
    ci_low, ci_high = np.percentile(bootstrap_means, [2.5, 97.5])
    return BootstrapEstimate(
        mean_difference=float(differences.mean()),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        n_pairs=len(differences),
        n_resamples=n_resamples,
        seed=seed,
    )


def clustered_paired_bootstrap_difference(
    values_a: Iterable[float],
    values_b: Iterable[float],
    clusters: Iterable[str],
    *,
    n_resamples: int = 10_000,
    seed: int = 42,
) -> ClusteredBootstrapEstimate:
    """Estimate mean(A - B), resampling independent source utterances.

    A clean recording and its noise-augmented copy are separate evaluation files
    but not independent observations. Resampling their shared cluster preserves
    the file-weighted estimand without pseudo-replicating the source utterance.
    """
    a = np.asarray(list(values_a), dtype=float)
    b = np.asarray(list(values_b), dtype=float)
    labels = list(clusters)
    if a.ndim != 1 or b.ndim != 1 or len(a) != len(b) or len(a) != len(labels):
        raise ValueError("Values and cluster labels must be one-dimensional and equally sized.")
    if len(a) == 0:
        raise ValueError("At least one paired observation is required.")
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive.")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Paired samples must contain only finite values.")

    grouped: dict[str, list[float]] = {}
    for label, difference in zip(labels, a - b):
        grouped.setdefault(label, []).append(float(difference))
    groups = list(grouped.values())
    rng = np.random.default_rng(seed)
    sampled_clusters = rng.integers(
        0, len(groups), size=(n_resamples, len(groups))
    )
    bootstrap_means = np.empty(n_resamples, dtype=float)
    for index, sample in enumerate(sampled_clusters):
        bootstrap_means[index] = np.mean(
            [value for group_index in sample for value in groups[group_index]]
        )
    ci_low, ci_high = np.percentile(bootstrap_means, [2.5, 97.5])
    return ClusteredBootstrapEstimate(
        mean_difference=float((a - b).mean()),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        n_observations=len(a),
        n_clusters=len(groups),
        n_resamples=n_resamples,
        seed=seed,
    )


def latency_summary(values: Iterable[float]) -> dict[str, float | int]:
    """Return explicit steady-state latency statistics using linear percentiles."""
    array = np.asarray(list(values), dtype=float)
    if array.ndim != 1 or len(array) == 0:
        raise ValueError("At least one latency observation is required.")
    if not np.isfinite(array).all() or (array < 0).any():
        raise ValueError("Latencies must be finite and non-negative.")
    return {
        "n": len(array),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "p95": float(np.percentile(array, 95, method="linear")),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
    }
