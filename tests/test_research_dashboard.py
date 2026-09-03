from pathlib import Path

from backend.evaluation.research_dashboard import build_research_dashboard


def test_dashboard_exposes_three_research_questions_and_provenance():
    payload = build_research_dashboard(Path("results"))

    assert [item["id"] for item in payload["research_questions"]] == [
        "rq1",
        "rq2",
        "rq3",
    ]
    assert payload["research_questions"][0]["headline_metric"]["value"] == 35.3
    assert payload["research_questions"][1]["headline_metric"]["value"] == 1.0
    assert payload["research_questions"][2]["headline_metric"]["value"] >= 0
    assert all(
        comparison["sources"]
        for question in payload["research_questions"]
        for comparison in question["comparisons"]
    )


def test_dashboard_discloses_corpus_and_live_method_limits():
    payload = build_research_dashboard(Path("results"))

    assert "not a representative corporate meeting benchmark" in payload["scope"]["corpus_warning"]
    rq3 = payload["research_questions"][2]
    assert "VAD-segmented batch inference" in rq3["limitation"]
    assert payload["meta"]["audit_status"] in {"current", "configuration_mismatch"}

