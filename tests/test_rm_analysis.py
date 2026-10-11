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


def test_summary_excludes_empty_reference_rows_from_wer():
    rows = [_row("A", "forced-clean", "ami-ihm", i, 2) for i in range(8)]
    empty = _row("A", "forced-clean", "ami-ihm", 50, 0, n=0)
    empty["ins"] = "440"
    (s,) = summarise(rows + [empty])
    assert abs(float(s["wer"]) - 0.2) < 1e-9
    assert s["n_excluded_empty_ref"] == 1 and s["n_segments"] == 8
    (s0,) = summarise(rows)
    assert s0["n_excluded_empty_ref"] == 0


def test_primary_test_ignores_empty_reference_rows():
    def build(extra):
        rows = []
        for i in range(8):
            rows.append(_row("whisper-large-v3", "forced-clean", "agm", i, 1, lang="de"))
            rows.append(_row("conformer-ctc-large", "forced-clean", "agm", i, 3, lang="de"))
        if extra:
            bad = _row("whisper-large-v3", "forced-clean", "agm", 77, 0, n=0, lang="de")
            bad["ins"] = "440"
            rows.append(bad)
            rows.append(_row("conformer-ctc-large", "forced-clean", "agm", 77, 0, n=0, lang="de"))
        return {r["key"]: r for r in primary_tests(rows)}["P1"]
    assert build(True)["estimate"] == build(False)["estimate"]


def test_p8_label_states_pooling_and_estimate_unchanged_by_label():
    rows = []
    for i in range(8):
        rows += [_row("whisper-large-v3", "auto-snr5", "agm", i, 3), _row("whisper-large-v3", "forced-snr5", "agm", i, 1)]
        rows += [_row("whisper-large-v3", "auto-clean", "summre", i, 3, lang="fr"),
                 _row("whisper-large-v3", "forced-clean", "summre", i, 1, lang="fr")]
    p8 = {r["key"]: r for r in primary_tests(rows)}["P8"]
    assert p8["a"] == "whisper-large-v3|auto|agm-snr5+ami-sdm+summre|all"
    assert p8["b"] == "whisper-large-v3|forced|agm-snr5+ami-sdm+summre|all"
    assert float(p8["estimate"]) == pytest.approx(0.2) and p8["n_segments"] == 16


def test_lang_mismatch_rate_is_na_for_noise_and_hf_baselines():
    base = [_row("S", "forced-clean", "agm", i, 1) for i in range(4)]
    base[0]["detected_language"] = "de"
    noise = [dict(_row("whisper-small", "forced-clean", "noise", i, 0, n=0), ins="3") for i in range(3)]
    hf = [_row("hf-whisper-small-lora", "forced-clean", "ami-ihm", i, 1) for i in range(4)]
    out = {(s["dataset"], s["system"]): s for s in summarise(base + noise + hf)}
    assert out[("agm", "S")]["lang_mismatch_rate"] == "0.250"
    assert out[("noise", "whisper-small")]["lang_mismatch_rate"] == ""
    assert out[("ami-ihm", "hf-whisper-small-lora")]["lang_mismatch_rate"] == ""
    assert out[("ami-ihm", "hf-whisper-small-lora")]["wer"] == "0.1000"


def test_format_p_shows_bootstrap_floor_as_bound():
    from study_real_meetings.analysis import format_p
    assert format_p("0.0018", floor=0.002) == "$<$0.002"
    assert format_p("0.0048", floor=0.002) == "0.005"
    assert format_p("", floor=0.002) == "--"
