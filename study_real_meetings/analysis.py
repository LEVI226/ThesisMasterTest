"""Summary tables and the nine pre-registered primary comparisons (PROTOCOL §7)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from study_real_meetings.stats import (
    cluster_bootstrap_wer,
    holm,
    paired_wer_difference,
    unpaired_wer_difference,
)


def _int(row, key):
    return int(row[key])


def _errors(row):
    return _int(row, "sub") + _int(row, "del") + _int(row, "ins")


def summarise(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        if r["split"] == "test":
            groups[(r["dataset"], r["language"], r["system"], r["condition"])].append(r)
    out = []
    for (dataset, language, system, condition), rs in sorted(groups.items()):
        n_excluded = 0
        if dataset != "noise":  # R16: filler-only references normalise to zero words; WER undefined
            kept = [r for r in rs if _int(r, "n_ref") > 0]
            n_excluded, rs = len(rs) - len(kept), kept
        if not rs:
            continue
        n_ref = [_int(r, "n_ref") for r in rs]
        summary = {"dataset": dataset, "language": language, "system": system, "condition": condition,
                   "n_segments": len(rs), "n_ref_words": sum(n_ref), "n_excluded_empty_ref": n_excluded}
        if sum(n_ref):
            est = cluster_bootstrap_wer([_errors(r) for r in rs], n_ref, [r["cluster"] for r in rs])
            summary |= {"wer": f"{est.estimate:.4f}", "ci_low": f"{est.ci_low:.4f}", "ci_high": f"{est.ci_high:.4f}",
                        "wer_num": f"{sum(_int(r, 'errors_num') for r in rs) / sum(_int(r, 'n_ref_num') for r in rs):.4f}",
                        "cer": f"{sum(_int(r, 'c_errors') for r in rs) / max(1, sum(_int(r, 'c_ref') for r in rs)):.4f}"}
        else:  # noise-only clips: report spurious words instead of WER
            summary |= {"wer": "", "ci_low": "", "ci_high": "", "wer_num": "", "cer": "",
                        "spurious_words_per_clip": f"{sum(_int(r, 'ins') for r in rs) / len(rs):.2f}"}
        terms_total = sum(_int(r, "term_total") for r in rs)
        summary |= {
            "term_recall": f"{sum(_int(r, 'term_hits') for r in rs) / terms_total:.3f}" if terms_total else "",
            "loop_rate": f"{sum(_int(r, 'repetition_loop') for r in rs) / len(rs):.3f}",
            "lang_mismatch_rate": f"{sum(r['detected_language'] != r['language'] for r in rs) / len(rs):.3f}",
            "median_rtf": f"{sorted(float(r['rtf']) for r in rs)[len(rs) // 2]:.4f}",
        }
        out.append(summary)
    return out


@dataclass(frozen=True)
class Selector:
    system: str
    condition: str
    datasets: tuple[str, ...]
    language: str | None = None

    def pick(self, rows):
        return [r for r in rows if r["split"] == "test" and r["system"] == self.system
                and not (r["dataset"] != "noise" and r["n_ref"] == "0")  # R16
                and r["condition"] == self.condition and r["dataset"] in self.datasets
                and (self.language is None or r["language"] == self.language)]


@dataclass(frozen=True)
class Comparison:
    key: str
    hypothesis: str
    a: Selector
    b: Selector
    paired_on: str | None  # "segment_id", "pair_key", or None for unpaired


L3 = "whisper-large-v3"
PRIMARY = [
    *[Comparison(f"P{i + 1}", "H1", Selector(L3, "forced-clean", ("agm",), lang),
                 Selector("conformer-ctc-large", "forced-clean", ("agm",), lang), "segment_id")
      for i, lang in enumerate(("de", "en", "fr"))],
    Comparison("P4", "H2", Selector(L3, "forced-snr10", ("agm",)), Selector(L3, "forced-clean", ("agm",)), "segment_id"),
    Comparison("P5", "H2", Selector(L3, "forced-clean", ("ami-sdm",)), Selector(L3, "forced-clean", ("ami-ihm",)), "pair_key"),
    Comparison("P6", "H3", Selector(L3, "forced-clean", ("ami-ihm",)), Selector(L3, "forced-clean", ("agm",), "en"), None),
    Comparison("P7", "H3", Selector(L3, "forced-clean", ("summre",)), Selector(L3, "forced-clean", ("agm",), "fr"), None),
    Comparison("P8", "H4a", Selector(L3, "auto-snr5", ("agm",)), Selector(L3, "forced-snr5", ("agm",)), "segment_id"),
    Comparison("P9", "H4d", Selector("hf-whisper-small-lora", "forced-clean", ("ami-ihm", "summre")),
               Selector("hf-whisper-small", "forced-clean", ("ami-ihm", "summre")), "segment_id"),
]
# P8 pools AGM snr5 with AMI-SDM and SUMM-RE "auto-clean vs forced-clean":
P8_EXTRA = (Selector(L3, "auto-clean", ("ami-sdm", "summre")), Selector(L3, "forced-clean", ("ami-sdm", "summre")))


def _paired(a_rows, b_rows, key):
    if key == "pair_key":  # IHM vs SDM live in different datasets: match on pair_key alone
        b_by = {r[key]: r for r in b_rows}
        return [(a, b_by[a[key]]) for a in a_rows if a[key] in b_by]
    b_by = {(r["dataset"], r[key]): r for r in b_rows}
    return [(a, b_by[(a["dataset"], a[key])]) for a in a_rows if (a["dataset"], a[key]) in b_by]


def primary_tests(rows: list[dict]) -> list[dict]:
    results = []
    for comp in PRIMARY:
        a_rows, b_rows = comp.a.pick(rows), comp.b.pick(rows)
        if comp.key == "P8":
            a_rows += P8_EXTRA[0].pick(rows)
            b_rows += P8_EXTRA[1].pick(rows)
        base = {"key": comp.key, "hypothesis": comp.hypothesis,
                "a": f"{comp.a.system}|{comp.a.condition}|{'+'.join(comp.a.datasets)}|{comp.a.language or 'all'}",
                "b": f"{comp.b.system}|{comp.b.condition}|{'+'.join(comp.b.datasets)}|{comp.b.language or 'all'}"}
        if not a_rows or not b_rows:
            results.append(base | {"status": "missing"})
            continue
        if comp.paired_on:
            pairs = _paired(a_rows, b_rows, comp.paired_on)
            if not pairs:
                results.append(base | {"status": "missing"})
                continue
            est = paired_wer_difference([_errors(a) for a, _ in pairs], [_errors(b) for _, b in pairs],
                                        [_int(a, "n_ref") for a, _ in pairs], [a["cluster"] for a, _ in pairs])
        else:
            est = unpaired_wer_difference([_errors(r) for r in a_rows], [_int(r, "n_ref") for r in a_rows],
                                          [r["cluster"] for r in a_rows], [_errors(r) for r in b_rows],
                                          [_int(r, "n_ref") for r in b_rows], [r["cluster"] for r in b_rows])
        results.append(base | {"status": "ok", "estimate": f"{est.estimate:.4f}", "ci_low": f"{est.ci_low:.4f}",
                               "ci_high": f"{est.ci_high:.4f}", "p_value": f"{est.p_value:.4f}",
                               "n_segments": est.n_segments, "n_clusters": est.n_clusters})
    # Fixed family: all nine pre-registered comparisons; missing ones enter with p = 1.0.
    ok_p = {r["key"]: float(r["p_value"]) for r in results if r["status"] == "ok"}
    adjusted = holm({comp.key: ok_p.get(comp.key, 1.0) for comp in PRIMARY})
    for r in results:
        r["holm_m"] = len(PRIMARY)
        if r["status"] == "ok":
            p, reject = adjusted[r["key"]]
            r |= {"p_holm": f"{p:.4f}", "reject_h0": int(reject)}
        else:
            r |= {"p_holm": "", "reject_h0": ""}
    return results


def _tex(value) -> str:
    text = str(value)
    for char, repl in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"), ("&", r"\&"), ("#", r"\#")):
        text = text.replace(char, repl)
    return text


def to_latex(rows: list[dict], columns: list[tuple[str, str]], caption: str, label: str) -> str:
    head = " & ".join(title for _, title in columns)  # titles are trusted LaTeX authored in code
    body = "\n".join(" & ".join(_tex(r.get(key, "")) for key, _ in columns) + r" \\" for r in rows)
    return (
        "% Generated by study_real_meetings/scripts/analyse.py. Do not edit by hand.\n"
        "\\begin{table}[htbp]\n\\centering\\small\n"
        f"\\begin{{tabular}}{{{'l' * len(columns)}}}\n\\toprule\n{head} \\\\\n\\midrule\n{body}\n"
        "\\bottomrule\n\\end{tabular}\n"
        f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\end{{table}}\n"
    )
