import pytest

from backend.evaluation.topic2_readiness import summarize_sessions


def test_sessions_keep_cold_starts_and_slow_observations_separate():
    rows = [
        {"utterance_id": "1", "latency_seconds": "3"},
        {"utterance_id": "2", "latency_seconds": "0.5"},
        {"utterance_id": "1", "latency_seconds": "4"},
        {"utterance_id": "2", "latency_seconds": "11"},
        {"utterance_id": "3", "latency_seconds": "1"},
    ]
    sessions = summarize_sessions(rows)
    assert len(sessions) == 2
    assert sessions[0]["cold_start"] == 3
    assert sessions[0]["steady"]["n"] == 1
    assert sessions[1]["steady"]["maximum"] == 11
    assert sessions[1]["steady"]["median"] == 6


def test_cold_only_session_has_no_steady_summary():
    assert summarize_sessions([
        {"utterance_id": "1", "latency_seconds": "2"}
    ])[0]["steady"] is None


@pytest.mark.parametrize("rows", [
    [{"utterance_id": "2", "latency_seconds": "0.5"}],
    [{"utterance_id": "1", "latency_seconds": "nan"}],
    [{"utterance_id": "1", "latency_seconds": "-1"}],
    [{"utterance_id": "1", "latency_seconds": "1"},
     {"utterance_id": "3", "latency_seconds": "1"}],
])
def test_ambiguous_or_invalid_logs_fail(rows):
    with pytest.raises(ValueError):
        summarize_sessions(rows)
