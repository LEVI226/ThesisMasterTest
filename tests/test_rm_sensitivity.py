import pytest

from study_real_meetings.sensitivity import (
    loop_free_pairs,
    loop_rates,
    per_meeting_sdm_ihm,
    sensitivity_rows,
)


def _row(system, condition, dataset, seg, errors, n=10, lang="en", loop=0, pair=None, cluster=None, detected=None):
    return {"system": system, "condition": condition, "dataset": dataset, "language": lang,
            "segment_id": f"{dataset}-{seg}", "pair_key": pair or f"{dataset}-{seg}",
            "cluster": cluster or f"c{seg % 4}", "split": "test", "sub": str(errors), "del": "0",
            "ins": "0", "n_ref": str(n), "repetition_loop": str(loop), "detected_language": detected or lang}


def _p9_rows(loop_errors=40):
    rows = []
    for i in range(8):
        rows.append(_row("hf-whisper-small", "forced-clean", "ami-ihm", i, 5))
        rows.append(_row("hf-whisper-small-lora", "forced-clean", "ami-ihm", i, 3))
    # segment 8: baseline loops (many errors); LoRA does not
    rows.append(_row("hf-whisper-small", "forced-clean", "ami-ihm", 8, loop_errors, loop=1))
    rows.append(_row("hf-whisper-small-lora", "forced-clean", "ami-ihm", 8, 3))
    return rows


def test_loop_free_pairs_drop_pair_when_either_side_loops():
    a = [_row("A", "c", "d", i, 1, loop=int(i == 1)) for i in range(3)]
    b = [_row("B", "c", "d", i, 1, loop=int(i == 2)) for i in range(3)]
    kept, n_excluded = loop_free_pairs(list(zip(a, b)))
    assert [x["segment_id"] for x, _ in kept] == ["d-0"] and n_excluded == 2


def test_p9_loop_free_changes_estimate_and_counts_exclusions():
    out = {(r["analysis"], r["group"]): r for r in sensitivity_rows(_p9_rows())}
    full = out[("P9 with loops (reference)", "all")]
    free = out[("P9 loop-free", "all")]
    assert float(full["estimate"]) == pytest.approx((9 * 3 - (8 * 5 + 40)) / 90, abs=1e-4)
    assert float(free["estimate"]) == pytest.approx(-0.2)
    assert free["n_pairs"] == 8 and free["n_excluded"] == 1
    assert free["analysis_type"] == "exploratory_post_freeze"
    assert "p_value" not in free and "p_holm" not in free


def test_p8_per_dataset_and_wrong_language_rate():
    rows = []
    for i in range(8):
        rows.append(_row("whisper-large-v3", "auto-clean", "summre", i, 4, lang="fr", detected="en" if i < 2 else "fr"))
        rows.append(_row("whisper-large-v3", "forced-clean", "summre", i, 2, lang="fr"))
    out = {(r["analysis"], r["group"]): r for r in sensitivity_rows(rows)}
    assert float(out[("P8 per dataset", "summre")]["estimate"]) == pytest.approx(0.2)
    assert float(out[("P8 wrong-language rate (auto)", "summre")]["estimate"]) == pytest.approx(0.25)


def test_per_meeting_sdm_ihm_uses_pair_key_prefix():
    rows = []
    for i in range(3):
        rows.append(_row("whisper-large-v3", "forced-clean", "ami-sdm", i, 4, pair=f"EN2002a-X-{i}"))
        rows.append(_row("whisper-large-v3", "forced-clean", "ami-ihm", i, 1, pair=f"EN2002a-X-{i}"))
    rows.append(_row("whisper-large-v3", "forced-clean", "ami-sdm", 9, 6, pair="ES2004b-Y-9"))
    rows.append(_row("whisper-large-v3", "forced-clean", "ami-ihm", 9, 2, pair="ES2004b-Y-9"))
    out = {r["group"]: r for r in per_meeting_sdm_ihm(rows)}
    assert float(out["EN2002a"]["estimate"]) == pytest.approx(0.3)
    assert float(out["ES2004b"]["wer_a"]) == pytest.approx(0.6)


def test_loop_rate_by_system_dataset_condition():
    rows = [_row("A", "forced-clean", "agm", i, 1, loop=int(i == 0)) for i in range(4)]
    (r,) = loop_rates(rows)
    assert r["group"] == "A|agm|forced-clean" and float(r["estimate"]) == pytest.approx(0.25) and r["n_pairs"] == 4
