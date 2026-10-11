"""Ingest the filled blind sheet -> versioned references_v2/ + change log + diff
against the originals. Then rescore every stored hypothesis of the canonical
campaign (clean AND noisy twins) against the revised references, with clustered
bootstrap intervals, into revision_v2/. Nothing under datasets/ or results/ is
modified. No new inference is needed: hypotheses are read from the CSVs.

Usage: python ingest_sheet.py            # ingest + diff + rescore what is filled
"""
import csv, json, random, re, statistics as st, string, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from backend.evaluation.metrics import wer, cer

PUNCT = string.punctuation + "‘’“”—–"
norm = lambda t: re.sub(r"\s+", " ", (t or "").lower().translate(str.maketrans("", "", PUNCT))).strip()

SHEET = HERE / "07b_transcription_sheet_BLIND.csv"
V2 = HERE / "references_v2"; V2.mkdir(exist_ok=True)
REV = HERE / "revision_v2"; REV.mkdir(exist_ok=True)
ORIG = ROOT / "datasets/stt_eval/references"

# ------------------------------------------------------------------ 1. ingest
log_path = HERE / "references_v2_CHANGELOG.csv"
log_rows = []
revised = {}          # clean stem -> revised normalised text
pending = []
with open(SHEET, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        stem = Path(r["file"]).stem
        text = (r["transcription_verbatim"] or "").strip()
        if not text:
            pending.append((stem, r["needs_other_person"] or "unfilled")); continue
        orig = norm((ORIG / f"{stem}.txt").read_text(encoding="utf-8"))
        new = norm(text)
        (V2 / f"{stem}.txt").write_text(text, encoding="utf-8")
        revised[stem] = new
        log_rows.append({"file": stem, "annotator": r["annotator"], "date": r["date"] or str(date.today()),
                         "changed": "yes" if new != orig else "no",
                         "reason": "blind re-annotation by listening" + (f"; uncertain: {r['uncertain_passages']}" if r["uncertain_passages"] else ""),
                         "original_normalised": orig, "revised_normalised": new, "notes": r["notes"]})
with open(log_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()) if log_rows else ["file"]); w.writeheader(); w.writerows(log_rows)
print(f"ingested {len(revised)} revised references -> {V2}; changed vs original: {sum(1 for l in log_rows if l['changed']=='yes')}")
print("pending:", len(pending), "->", ", ".join(f"{s} ({why})" for s, why in pending[:30]))
if not revised:
    sys.exit("nothing filled yet")

# ------------------------------------------------------------------ 2. rescore
def ref_for(fn):
    m = re.match(r"(minds14_\w\w)_(clean|noisy)_(\d+)\.wav", fn)
    return revised.get(f"{m.group(1)}_clean_{m.group(3)}")

CANON = ["results/stt_eval_pilot_results.csv", "results/stt_eval_lora_results.csv",
         "results/stt_eval_wav2vec_results.csv", "results/stt_eval_conformer_results.csv"]
rows = []
for rel in CANON:
    with open(ROOT / rel, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["_src"] = Path(rel).name; r["_wo"], r["_co"] = float(r["wer"]), float(r["cer"])
            rv = ref_for(r["filename"])
            r["_rev"] = rv is not None
            r["_wn"] = wer(rv, r["hypothesis_text"]) if rv is not None else r["_wo"]
            r["_cn"] = cer(rv, r["hypothesis_text"]) if rv is not None else r["_co"]
            rows.append(r)
with open(REV / "rescored_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["source", "filename", "condition_tag", "model", "reference_revised", "wer_old", "wer_new", "cer_old", "cer_new"])
    for r in rows: w.writerow([r["_src"], r["filename"], r.get("condition_tag", ""), r["model"], r["_rev"], r["_wo"], round(r["_wn"], 4), r["_co"], round(r["_cn"], 4)])

# clustered bootstrap: unit = source utterance (clean stem), noisy twin stays in its cluster
stem_of = lambda fn: re.sub(r"_(clean|noisy)_", "_clean_", fn).replace(".wav", "")
def boot_mean(vals_by_cluster, B=10000, seed=42):
    random.seed(seed); clusters = list(vals_by_cluster.values()); out = []
    for _ in range(B):
        s = random.choices(clusters, k=len(clusters)); out.append(st.mean(v for c in s for v in c))
    out.sort(); return out[int(.025 * B)], out[int(.975 * B)]
def boot_paired(diff_by_cluster, B=10000, seed=42):
    random.seed(seed); clusters = list(diff_by_cluster.values()); out = []
    for _ in range(B):
        s = random.choices(clusters, k=len(clusters)); out.append(st.mean(v for c in s for v in c))
    out.sort(); return out[int(.025 * B)], out[int(.975 * B)]

by = defaultdict(list)
for r in rows: by[r.get("condition_tag", "")].append(r)
L = [f"# revision_v2 — rescoring with {len(revised)} revised references (clean + noisy twins), originals untouched\n",
     f"Revised clips: {', '.join(sorted(revised))}. Unrevised clips keep their original reference.\n",
     "| condition | n | WER old | WER new | 95% CI new (clustered by source clip) | CER old | CER new |", "|---|---:|---:|---:|---|---:|---:|"]
agg = {}
for tag, g in sorted(by.items()):
    cl = defaultdict(list)
    for r in g: cl[stem_of(r["filename"])].append(r["_wn"])
    lo, hi = boot_mean(cl)
    wo, wn = st.mean(r["_wo"] for r in g), st.mean(r["_wn"] for r in g); agg[tag] = (wo, wn)
    L.append(f"| {tag} | {len(g)} | {100*wo:.1f} | {100*wn:.1f} | [{100*lo:.1f}, {100*hi:.1f}] | {100*st.mean(r['_co'] for r in g):.1f} | {100*st.mean(r['_cn'] for r in g):.1f} |")

L += ["\n## Paired contrasts with clustered 95% bootstrap CI (new references)\n"]
def paired(tag_a, tag_b, label):
    A = {r["filename"]: r["_wn"] for r in by[tag_a]}; Bm = {r["filename"]: r["_wn"] for r in by[tag_b]}
    cl = defaultdict(list)
    for fn in A:
        if fn in Bm: cl[stem_of(fn)].append(A[fn] - Bm[fn])
    lo, hi = boot_paired(cl); m = st.mean(v for c in cl.values() for v in c)
    L.append(f"- {label}: {100*m:+.1f} pts, CI [{100*lo:+.1f}, {100*hi:+.1f}]")
paired("B_noise_reduction", "I_model_large_v3", "size B(tiny) − I(large-v3)")
paired("J0_small_hf_vanilla", "J_lora_small", "LoRA J0 − J")
paired("B_noise_reduction", "D_domain_prompt", "prompt B − D")
paired("D_domain_prompt", "E_forced_language", "forced language D − E")
paired("K_wav2vec", "J0_small_hf_vanilla", "MMS − whisper-small(J0)")
# noise, condition A, matched pairs
A = by["A_baseline"]; cmap = {stem_of(r["filename"]): r for r in A if r["noise_condition"] == "clean"}
diffs = {stem_of(r["filename"]): [r["_wn"] - cmap[stem_of(r["filename"])]["_wn"]] for r in A if r["noise_condition"] == "noisy"}
lo, hi = boot_paired(diffs); L.append(f"- noise penalty A, 12 matched pairs: {100*st.mean(v[0] for v in diffs.values()):+.1f} pts, CI [{100*lo:+.1f}, {100*hi:+.1f}]")
L += ["\n## Status\n", f"- references revised so far: {len(revised)}/24; pending: {len(pending)} (German rows need another annotator).",
      "- Figures above are provisional until all 24 clips are re-annotated and, ideally, double-checked.",
      "- Originals (datasets/stt_eval/references, results/*.csv) unchanged."]
(REV / "REVISION_v2.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("rescored ->", REV / "REVISION_v2.md")
