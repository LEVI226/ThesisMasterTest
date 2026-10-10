"""Write summary.csv, primary.csv, LaTeX tables and the WER-vs-SNR figure."""
from __future__ import annotations

import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from study_real_meetings import config as C  # noqa: E402
from study_real_meetings.analysis import primary_tests, summarise, to_latex  # noqa: E402
from study_real_meetings.runner import read_rows  # noqa: E402


def _write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows = read_rows(C.RESULTS / "runs.csv")
    summary, primary = summarise(rows), primary_tests(rows)
    _write_csv(C.RESULTS / "summary.csv", summary)
    _write_csv(C.RESULTS / "primary.csv", primary)
    C.GENERATED_TEX.mkdir(parents=True, exist_ok=True)
    pct = lambda v: f"{100 * float(v):.1f}" if v not in ("", None) else "--"  # noqa: E731
    main_rows = [r | {"wer_pct": pct(r["wer"]), "ci": f"[{pct(r['ci_low'])}, {pct(r['ci_high'])}]"}
                 for r in summary if r["condition"] == "forced-clean" and r["dataset"] != "noise"]
    (C.GENERATED_TEX / "real_meetings_summary.tex").write_text(to_latex(
        main_rows, [("dataset", "Data"), ("language", "Lang."), ("system", "System"), ("n_segments", "Seg."),
                    ("wer_pct", "WER (\\%)"), ("ci", "95\\% CI")],
        "Corpus WER on real meeting and corporate audio (test split, forced language, clean).",
        "tab:rm_summary"), encoding="utf-8")
    prim_rows = [r | {"est_pct": pct(r.get("estimate", "")),
                      "ci": f"[{pct(r.get('ci_low', ''))}, {pct(r.get('ci_high', ''))}]"} for r in primary]
    (C.GENERATED_TEX / "real_meetings_primary.tex").write_text(to_latex(
        prim_rows, [("key", "Test"), ("hypothesis", "H"), ("est_pct", "$\\Delta$WER (pts)"), ("ci", "95\\% CI"),
                    ("p_holm", "$p_{\\text{Holm}}$"), ("status", "Status")],
        "Pre-registered primary comparisons (A $-$ B, cluster bootstrap, Holm-corrected).",
        "tab:rm_primary"), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for system in ("whisper-small", "whisper-large-v3", "mms-1b-all", "conformer-ctc-large"):
        pts = []
        for label, x in (("forced-clean", 30), ("forced-snr20", 20), ("forced-snr10", 10), ("forced-snr5", 5)):
            vals = [r for r in summary if r["dataset"] == "agm" and r["system"] == system and r["condition"] == label]
            if vals:
                n = sum(int(v["n_ref_words"]) for v in vals)
                pts.append((x, 100 * sum(float(v["wer"]) * int(v["n_ref_words"]) for v in vals) / n))
        if pts:
            ax.plot(*zip(*pts), marker="o", label=system)
    ax.set_xlabel("SNR (dB); 30 = clean")
    ax.set_ylabel("WER (%)")
    ax.invert_xaxis()
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(C.GENERATED_TEX / "real_meetings_snr.pdf")
    print(f"summary: {len(summary)} groups; primary: {sum(r['status'] == 'ok' for r in primary)}/9 computed")


if __name__ == "__main__":
    main()
