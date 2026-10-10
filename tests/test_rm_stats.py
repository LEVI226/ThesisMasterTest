import math

import pytest

from study_real_meetings.stats import (
    cluster_bootstrap_wer,
    corpus_wer,
    holm,
    paired_wer_difference,
    unpaired_wer_difference,
)


def test_corpus_wer_is_total_errors_over_total_words():
    assert corpus_wer([1, 3], [10, 30]) == pytest.approx(0.1)


def test_identical_systems_have_zero_difference_and_p_one():
    e = [1, 2, 0, 3, 1, 2]
    est = paired_wer_difference(e, e, [10] * 6, list("aabbcc"), n_resamples=500, seed=1)
    assert (est.estimate, est.ci_low, est.ci_high) == (0.0, 0.0, 0.0)
    assert est.p_value == pytest.approx(1.0)
    assert est.n_clusters == 3


def test_consistently_worse_system_is_detected():
    clusters = [f"c{i // 2}" for i in range(40)]
    est = paired_wer_difference([5] * 40, [1] * 40, [10] * 40, clusters, n_resamples=2000, seed=1)
    assert est.estimate == pytest.approx(0.4)
    assert est.ci_low > 0 and est.p_value < 0.01


def test_single_system_interval_contains_estimate():
    est = cluster_bootstrap_wer([1, 2, 3, 4], [10, 10, 10, 10], ["a", "a", "b", "b"], n_resamples=500, seed=1)
    assert est.ci_low <= est.estimate <= est.ci_high and math.isnan(est.p_value)


def test_unpaired_difference_between_groups():
    est = unpaired_wer_difference([3] * 10, [10] * 10, [f"a{i}" for i in range(10)],
                                  [1] * 10, [10] * 10, [f"b{i}" for i in range(10)],
                                  n_resamples=500, seed=1)
    assert est.estimate == pytest.approx(0.2) and est.ci_low == pytest.approx(0.2)


def test_holm_step_down():
    out = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert out["a"] == (pytest.approx(0.03), True)
    assert out["c"] == (pytest.approx(0.06), False)
    assert out["b"] == (pytest.approx(0.06), False)
