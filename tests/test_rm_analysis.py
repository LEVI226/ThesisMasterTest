import pytest

from study_real_meetings.analysis import PRIMARY, primary_tests, summarise, to_latex


def _row(system, condition, dataset, seg, errors, n=10, lang="en", split="test", pair=None, cluster=None):
    return {"system": system, "condition": condition, "dataset": dataset, "language": lang,
            "segment_id": f"{dataset}-{seg}", "pair_key": pair or f"{dataset}-{seg}",
            "cluster": cluster or f"c{seg % 4}", "split": split, "sub": str(errors), "del": "0",
            "ins": "0", "n_ref": str(n), "errors_num": str(errors), "n_ref_num": str(n),
            "c_errors": "0", "c_ref": "1", "term_hits": "0", "term_total": "0",
            "repetition_loop": "0", "rtf": "0.1", "detected_language": lang}


def test_summary_ignores_dev_and_computes_corpus_wer():
    rows = [_row("A", "forced-clean", "agm", i, 2) for i in range(8)] + [_row("A", "forced-clean", "agm", 99, 10, split="dev")]
    (s,) = summarise(rows)
    assert s["n_segments"] == 8 and abs(float(s["wer"]) - 0.2) < 1e-9


def test_primary_tests_cover_nine_comparisons_and_apply_holm():
    assert len(PRIMARY) == 9
    rows = []
    for lang in ("de", "en", "fr"):
        rows += [_row("whisper-large-v3", "forced-clean", "agm", i, 1, lang=lang) for i in range(8)]
        rows += [_row("conformer-ctc-large", "forced-clean", "agm", i, 3, lang=lang) for i in range(8)]
    out = {r["key"]: r for r in primary_tests(rows)}
    assert out["P1"]["status"] == "ok" and float(out["P1"]["estimate"]) < 0
    assert out["P5"]["status"] == "missing"
    assert "p_holm" in out["P1"]


def test_latex_table_escapes_and_has_booktabs():
    tex = to_latex([{"system": "whisper_large", "wer": "0.123"}], [("system", "System"), ("wer", "WER")], "Cap", "tab:x")
    assert "\\toprule" in tex and "whisper\\_large" in tex and "\\label{tab:x}" in tex


def test_latex_headers_are_not_escaped():
    tex = to_latex([{"x": "a_b"}], [("x", r"$\Delta$WER (\%)")], "C", "tab:y")
    assert r"$\Delta$WER (\%)" in tex
    assert "\\textbackslash" not in tex
    assert r"a\_b" in tex


def test_holm_family_is_nine_even_when_comparisons_are_missing():
    rows = []
    for lang in ("de", "en", "fr"):
        rows += [_row("whisper-large-v3", "forced-clean", "agm", i, 1, lang=lang) for i in range(8)]
        rows += [_row("conformer-ctc-large", "forced-clean", "agm", i, 3, lang=lang) for i in range(8)]
    out = {r["key"]: r for r in primary_tests(rows)}
    assert out["P1"]["holm_m"] == 9
    assert float(out["P1"]["p_holm"]) >= float(out["P1"]["p_value"]) * 7
    assert out["P5"]["p_holm"] == ""


def test_p5_pairs_ihm_and_sdm_by_pair_key():
    rows = [_row("whisper-large-v3", "forced-clean", "ami-sdm", i, 3, pair=f"k{i}") for i in range(8)]
    rows += [_row("whisper-large-v3", "forced-clean", "ami-ihm", 100 + i, 1, pair=f"k{i}") for i in range(8)]
    out = {r["key"]: r for r in primary_tests(rows)}
    assert out["P5"]["status"] == "ok"
    assert float(out["P5"]["estimate"]) == pytest.approx(0.2)
