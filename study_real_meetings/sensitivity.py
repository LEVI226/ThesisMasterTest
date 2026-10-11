"""EXPLORATORY post-freeze sensitivity analyses (PROTOCOL §9, 2026-10-11).

Nothing here changes a pre-registered estimate. Rows carry confidence intervals only (no p-values,
no Holm) and are labelled ``analysis_type = exploratory_post_freeze``.
"""
from __future__ import annotations

from collections import defaultdict

from study_real_meetings.analysis import L3, PRIMARY, Selector, _errors, _int, _paired
from study_real_meetings.stats import paired_wer_difference

ANALYSIS_TYPE = "exploratory_post_freeze"
COLUMNS = ["analysis_type", "analysis", "group", "metric", "estimate", "ci_low", "ci_high",
           "n_pairs", "n_excluded", "n_clusters", "wer_a", "wer_b", "note"]
_COMP = {c.key: c for c in PRIMARY}


def _fmt(x) -> str:
    return f"{x:.4f}"


def _row(analysis, group, metric, **kw) -> dict:
    out = dict.fromkeys(COLUMNS, "")
    out |= {"analysis_type": ANALYSIS_TYPE, "analysis": analysis, "group": group, "metric": metric}
    out |= kw
    return out


def loop_free_pairs(pairs: list[tuple[dict, dict]]) -> tuple[list[tuple[dict, dict]], int]:
    """Drop every pair in which either side has repetition_loop == 1."""
    kept = [(a, b) for a, b in pairs if str(a["repetition_loop"]) != "1" and str(b["repetition_loop"]) != "1"]
    return kept, len(pairs) - len(kept)


def _paired_row(analysis, group, pairs, n_excluded=0, note="") -> dict:
    if not pairs:
        return _row(analysis, group, "wer_diff_a_minus_b", note=note or "no pairs")
    est = paired_wer_difference([_errors(a) for a, _ in pairs], [_errors(b) for _, b in pairs],
                                [_int(a, "n_ref") for a, _ in pairs], [a["cluster"] for a, _ in pairs])
    return _row(analysis, group, "wer_diff_a_minus_b", estimate=_fmt(est.estimate), ci_low=_fmt(est.ci_low),
                ci_high=_fmt(est.ci_high), n_pairs=est.n_segments, n_excluded=n_excluded,
                n_clusters=est.n_clusters, note=note)


def _comparison_pairs(key: str, rows: list[dict]) -> list[tuple[dict, dict]]:
    comp = _COMP[key]
    return _paired(comp.a.pick(rows), comp.b.pick(rows), comp.paired_on)


def _wer(rows) -> float:
    return sum(_errors(r) for r in rows) / sum(_int(r, "n_ref") for r in rows)


def per_meeting_sdm_ihm(rows: list[dict]) -> list[dict]:
    """P5 per AMI meeting: large-v3 forced-clean SDM minus IHM, matched on pair_key (point estimates)."""
    pairs = _comparison_pairs("P5", rows)
    by_meeting = defaultdict(list)
    for a, b in pairs:
        by_meeting[a["pair_key"].split("-")[0]].append((a, b))
    out = []
    for meeting, ps in sorted(by_meeting.items()):
        wa, wb = _wer([a for a, _ in ps]), _wer([b for _, b in ps])
        out.append(_row("P5 per meeting", meeting, "wer_diff_a_minus_b", estimate=_fmt(wa - wb),
                        n_pairs=len(ps), wer_a=_fmt(wa), wer_b=_fmt(wb),
                        note="a = SDM, b = IHM; point estimate, no CI"))
    return out


def loop_rates(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for r in rows:
        if r["split"] == "test" and not (r["dataset"] != "noise" and r["n_ref"] == "0"):
            groups[(r["system"], r["dataset"], r["condition"])].append(r)
    return [_row("loop rate", "|".join(k), "share_repetition_loop",
                 estimate=_fmt(sum(str(r["repetition_loop"]) == "1" for r in rs) / len(rs)), n_pairs=len(rs))
            for k, rs in sorted(groups.items())]


# P8 conditions per dataset (the pre-registered pooling is split into its three parts).
P8_PARTS = (("agm", "auto-snr5", "forced-snr5"), ("ami-sdm", "auto-clean", "forced-clean"),
            ("summre", "auto-clean", "forced-clean"))


def sensitivity_rows(rows: list[dict]) -> list[dict]:
    out = []
    for key, label in (("P9", "P9"), ("P3", "P3")):
        pairs = _comparison_pairs(key, rows)
        out.append(_paired_row(f"{label} with loops (reference)", "all", pairs,
                               note="same selection and seed as the pre-registered test"))
        kept, n_excl = loop_free_pairs(pairs)
        out.append(_paired_row(f"{label} loop-free", "all", kept, n_excl,
                               note="pairs where either side has repetition_loop=1 removed"))
    for dataset, auto, forced in P8_PARTS:
        a = Selector(L3, auto, (dataset,)).pick(rows)
        b = Selector(L3, forced, (dataset,)).pick(rows)
        out.append(_paired_row("P8 per dataset", dataset, _paired(a, b, "segment_id"),
                               note=f"a = {auto}, b = {forced}"))
    for dataset, auto, _ in P8_PARTS:
        a = Selector(L3, auto, (dataset,)).pick(rows)
        if a:
            out.append(_row("P8 wrong-language rate (auto)", dataset, "share_detected_ne_language",
                            estimate=_fmt(sum(r["detected_language"] != r["language"] for r in a) / len(a)),
                            n_pairs=len(a), note=f"condition {auto}"))
    out += per_meeting_sdm_ihm(rows)
    out += loop_rates(rows)
    return out
