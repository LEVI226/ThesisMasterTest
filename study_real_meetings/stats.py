"""Corpus-level WER with cluster bootstrap.

Corpus WER = total errors / total reference words (not the mean of per-segment WER),
the standard ASR convention. Clusters (meeting x speaker, or 2-minute AGM blocks)
are resampled because segments inside a cluster are not independent.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from study_real_meetings.config import ALPHA, N_BOOTSTRAP, SEED


@dataclass(frozen=True)
class Estimate:
    estimate: float
    ci_low: float
    ci_high: float
    p_value: float
    n_segments: int
    n_clusters: int


def corpus_wer(errors, n_ref) -> float:
    return float(np.sum(errors)) / float(np.sum(n_ref))


def _cluster_sums(clusters, *columns):
    labels = sorted(set(clusters))
    index = {label: i for i, label in enumerate(labels)}
    sums = np.zeros((len(columns), len(labels)))
    for row, label in enumerate(clusters):
        for c, column in enumerate(columns):
            sums[c, index[label]] += column[row]
    return sums


def _p_two_sided(boot: np.ndarray) -> float:
    n = len(boot)
    below = (np.sum(boot <= 0) + 1) / (n + 1)
    above = (np.sum(boot >= 0) + 1) / (n + 1)
    return float(min(1.0, 2 * min(below, above)))


def cluster_bootstrap_wer(errors, n_ref, clusters, *, n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate:
    e, n = _cluster_sums(list(clusters), list(errors), list(n_ref))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, e.size, size=(n_resamples, e.size))
    boot = e[idx].sum(axis=1) / n[idx].sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return Estimate(corpus_wer(errors, n_ref), float(lo), float(hi), math.nan, len(list(errors)), e.size)


def paired_wer_difference(errors_a, errors_b, n_ref, clusters, *, n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate:
    ea, eb, n = _cluster_sums(list(clusters), list(errors_a), list(errors_b), list(n_ref))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n.size, size=(n_resamples, n.size))
    boot = (ea[idx].sum(axis=1) - eb[idx].sum(axis=1)) / n[idx].sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    point = (float(np.sum(errors_a)) - float(np.sum(errors_b))) / float(np.sum(n_ref))
    return Estimate(point, float(lo), float(hi), _p_two_sided(boot), len(list(n_ref)), n.size)


def unpaired_wer_difference(errors_a, n_a, clusters_a, errors_b, n_b, clusters_b, *,
                            n_resamples=N_BOOTSTRAP, seed=SEED) -> Estimate:
    ea, na = _cluster_sums(list(clusters_a), list(errors_a), list(n_a))
    eb, nb = _cluster_sums(list(clusters_b), list(errors_b), list(n_b))
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, na.size, size=(n_resamples, na.size))
    ib = rng.integers(0, nb.size, size=(n_resamples, nb.size))
    boot = ea[ia].sum(axis=1) / na[ia].sum(axis=1) - eb[ib].sum(axis=1) / nb[ib].sum(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    point = corpus_wer(errors_a, n_a) - corpus_wer(errors_b, n_b)
    return Estimate(point, float(lo), float(hi), _p_two_sided(boot),
                    len(list(n_a)) + len(list(n_b)), na.size + nb.size)


def holm(p_values: dict[str, float], alpha: float = ALPHA) -> dict[str, tuple[float, bool]]:
    order = sorted(p_values, key=p_values.get)
    m = len(order)
    out: dict[str, tuple[float, bool]] = {}
    running = 0.0
    for rank, key in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p_values[key]))
        out[key] = (running, running <= alpha)
    return out
