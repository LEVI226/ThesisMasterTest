"""Impact of the human-confirmed reference correction for minds14_en_clean_01.

Human check (2026-09-16, the author, by listening): after "with my partner" the
recording says "how do I proceed with doing that". The canonical reference stops
at "partner". minds14_en_noisy_01 reuses the same reference file.

Nothing canonical is modified. This script re-scores the affected rows with the
corrected reference and reports the aggregate deltas, into this run folder only.
"""
import csv, json, statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
from backend.evaluation.metrics import wer, cer

ORIG_REF = (ROOT / "datasets/stt_eval/references/minds14_en_clean_01.txt").read_text(encoding="utf-8").strip()
CORRECTED = ORIG_REF + " how do I proceed with doing that"
AFFECTED = {"minds14_en_clean_01.wav", "minds14_en_noisy_01.wav"}

CANON = ["results/stt_eval_pilot_results.csv", "results/stt_eval_lora_results.csv",
         "results/stt_eval_wav2vec_results.csv", "results/stt_eval_conformer_results.csv"]

rows, changed = [], []
for rel in CANON:
    with open(ROOT / rel, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["_src"] = rel
            r["_wer_old"] = float(r["wer"]); r["_cer_old"] = float(r["cer"])
            if r["filename"] in AFFECTED:
                assert r["reference_text"].strip() == ORIG_REF, r["filename"]
                r["_wer_new"] = wer(CORRECTED, r["hypothesis_text"]); r["_cer_new"] = cer(CORRECTED, r["hypothesis_text"])
                changed.append(r)
            else:
                r["_wer_new"] = r["_wer_old"]; r["_cer_new"] = r["_cer_old"]
            rows.append(r)

lines = ["# 06 Reference revision — minds14_en_clean_01 (and its noisy twin)\n",
         f"Original reference : `{ORIG_REF}`",
         f"Corrected reference: `{CORRECTED}`  (phrase confirmed by listening; punctuation irrelevant under normalisation)",
         f"Affected canonical rows: **{len(changed)}** of {len(rows)} (two files across every condition).",
         "Canonical files untouched; this is a separate revision.\n",
         "## Per-row impact\n", "| source | file | condition | model | WER old | WER new | CER old | CER new |", "|---|---|---|---|---:|---:|---:|---:|"]
for r in changed:
    lines.append(f"| {Path(r['_src']).name} | {r['filename']} | {r.get('condition_tag','')} | {r['model']} | "
                 f"{r['_wer_old']:.4f} | {r['_wer_new']:.4f} | {r['_cer_old']:.4f} | {r['_cer_new']:.4f} |")

lines += ["\n## Aggregate impact (mean-of-per-file WER, the manuscript's estimator)\n",
          "| condition | n | WER old | WER new | Δ pts | CER old | CER new |", "|---|---:|---:|---:|---:|---:|---:|"]
by = defaultdict(list)
for r in rows: by[(Path(r["_src"]).name, r.get("condition_tag", ""))].append(r)
agg = {}
for (src, tag), g in sorted(by.items()):
    wo, wn = st.mean(x["_wer_old"] for x in g), st.mean(x["_wer_new"] for x in g)
    co, cn = st.mean(x["_cer_old"] for x in g), st.mean(x["_cer_new"] for x in g)
    agg[tag or src] = (len(g), wo, wn, co, cn)
    lines.append(f"| {tag or src} | {len(g)} | {100*wo:.1f} % | {100*wn:.1f} % | {100*(wn-wo):+.1f} | {100*co:.1f} % | {100*cn:.1f} % |")

# headline figures quoted in the manuscript
lines += ["\n## Headline figures in the manuscript, before → after\n"]
def a(tag): return agg[tag]
for label, tag in [("A tiny baseline 63.4", "A_baseline"), ("B 62.2", "B_noise_reduction"), ("F base 48.3", "F_model_base"),
                   ("G small 33.3", "G_model_small"), ("H medium 25.9", "H_model_medium"), ("I large-v3 24.6", "I_model_large_v3"),
                   ("J0 whisper-small HF 31.2", "J0_small_hf_vanilla"), ("J LoRA 30.2", "J_lora_small"), ("K MMS 35.4", "K_wav2vec")]:
    n, wo, wn, _, _ = a(tag)
    lines.append(f"- {label}: {100*wo:.1f} % → **{100*wn:.1f} %** ({100*(wn-wo):+.1f} pts)")
conf = [r for r in rows if r.get("condition_tag", "").startswith("L_conformer")]
lines.append(f"- L Conformer global 26.3: {100*st.mean(x['_wer_old'] for x in conf):.1f} % → **{100*st.mean(x['_wer_new'] for x in conf):.1f} %**")

# paired noise effect, condition A (12 pairs)
A = [r for r in rows if r.get("condition_tag") == "A_baseline"]
import re
def stem(fn):
    m = re.match(r"minds14_(\w\w)_(clean|noisy)_(\d+)\.wav", fn); return (m.group(1), m.group(3))
cmap = {stem(r["filename"]): r for r in A if r["noise_condition"] == "clean"}
pairs = [(cmap[stem(r["filename"])], r) for r in A if r["noise_condition"] == "noisy"]
for k in ("_wer_old", "_wer_new"):
    c = st.mean(p[0][k] for p in pairs); nn = st.mean(p[1][k] for p in pairs)
    lines.append(f"- Paired noise effect ({k[5:]}): clean {100*c:.1f} % → noisy {100*nn:.1f} %, penalty {100*(nn-c):+.1f} pts")

lines += ["\n## Reading\n",
          "- Every affected hypothesis that was actually correct was charged 7 insertions (7/12 = 0.5833). The correction lowers WER for those rows and raises nothing.",
          "- The direction of every conclusion in the manuscript is unchanged; the magnitudes move by the amounts above.",
          "- Recommended handling: keep the canonical CSVs and reference file as the record of what was scored; add this revision as an erratum note with the corrected aggregates, and re-listen to the other 23 references before the defense (same risk class)."]
(OUT / "06_reference_revision_en_clean_01.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
with open(OUT / "06_reference_revision_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["source", "filename", "condition_tag", "model", "wer_old", "wer_new", "cer_old", "cer_new", "hypothesis"])
    for r in changed: w.writerow([r["_src"], r["filename"], r.get("condition_tag", ""), r["model"], r["_wer_old"], round(r["_wer_new"], 4), r["_cer_old"], round(r["_cer_new"], 4), r["hypothesis_text"]])
print("\n".join(lines[lines.index("## Headline figures in the manuscript, before → after\n") - 1:]))
