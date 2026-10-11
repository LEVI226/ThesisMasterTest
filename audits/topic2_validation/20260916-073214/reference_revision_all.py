"""Sensitivity of every canonical aggregate to the 5 human-confirmed reference
defects (10 of 36 files once noisy twins are included). Canonical files untouched.

Corrected references = whisper large-v3 hypothesis, whose wording the author
confirmed by listening on the salient phrases (2026-09-16). This is NOT a
word-by-word human transcription. Consequence stated up front: on these 5 clean
files large-v3 scores 0 by construction, so its figures are optimistic; every
conclusion below is therefore checked for ORDER, not just magnitude.
"""
import csv, re, statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
from backend.evaluation.metrics import wer, cer

CORR = {  # clean stem -> corrected reference (large-v3 wording, author-confirmed phrases)
 "minds14_en_clean_01": "I would like to set up a joint account with my partner how do I proceed with doing that",
 "minds14_en_clean_02": "wondering how i would set up a joint account with my wife and where the app might be",
 "minds14_en_clean_03": "hi id like to set up a joint account with my partner im not seeing the option to do it on the app so i called in to get some help can i just do it over the phone with you and give you the information or should i do it in the app and im missing something okay id prefer to just do it over the phone if possible thanks",
 "minds14_en_clean_07": "hi id like to open a joint account can you tell me what the process is thank you",
 "minds14_fr_clean_03": "bonjour javais changé dadresse dans quelques semaines et je voulais savoir quelles étaient les démarches à faire par rapport à ma carte bancaire sil y avait quelque chose à faire ou pas",
}
def corrected_for(fn):
    m = re.match(r"(minds14_\w\w)_(clean|noisy)_(\d+)\.wav", fn)
    return CORR.get(f"{m.group(1)}_clean_{m.group(3)}")

CANON = ["results/stt_eval_pilot_results.csv", "results/stt_eval_lora_results.csv",
         "results/stt_eval_wav2vec_results.csv", "results/stt_eval_conformer_results.csv"]
rows, changed = [], []
for rel in CANON:
    with open(ROOT / rel, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["_src"] = Path(rel).name; r["_wo"] = float(r["wer"]); r["_co"] = float(r["cer"])
            c = corrected_for(r["filename"])
            if c:
                r["_wn"] = wer(c, r["hypothesis_text"]); r["_cn"] = cer(c, r["hypothesis_text"]); changed.append(r)
            else:
                r["_wn"], r["_cn"] = r["_wo"], r["_co"]
            rows.append(r)

L = ["# 06b Reference revision — all 5 confirmed defects (10 of 36 files)\n",
     "Confirmed by the author listening (2026-09-16): en_01, en_02, en_03, en_07, fr_03 — each either truncated",
     "(en_01, en_03, fr_03) or mis-transcribed (en_02 'henry county', en_07 'is like you open'). Noisy twins share the file.",
     f"Rows affected: **{len(changed)}** of {len(rows)}. Canonical CSVs and reference files untouched.\n",
     "**Method limit**: corrected references are the large-v3 wording confirmed on salient phrases, not a full human",
     "transcription. large-v3 therefore scores 0 on these clean files by construction; its corrected figures are optimistic.",
     "Conclusions are checked for order below.\n",
     "## Aggregates, mean-of-per-file (manuscript estimator)\n",
     "| condition | n | WER old | WER new | Δ | CER old | CER new |", "|---|---:|---:|---:|---:|---:|---:|"]
by = defaultdict(list)
for r in rows: by[(r["_src"], r.get("condition_tag", ""))].append(r)
agg = {}
for (src, tag), g in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    wo, wn = st.mean(x["_wo"] for x in g), st.mean(x["_wn"] for x in g)
    co, cn = st.mean(x["_co"] for x in g), st.mean(x["_cn"] for x in g)
    agg[tag] = (wo, wn); L.append(f"| {tag} | {len(g)} | {100*wo:.1f} | {100*wn:.1f} | {100*(wn-wo):+.1f} | {100*co:.1f} | {100*cn:.1f} |")

ladder = ["A_baseline", "F_model_base", "G_model_small", "H_model_medium", "I_model_large_v3"]
L += ["\n## Order checks\n",
      "- Model-size ladder (A→F→G→H→I), old: " + " → ".join(f"{100*agg[t][0]:.1f}" for t in ladder)
      + " | new: " + " → ".join(f"{100*agg[t][1]:.1f}" for t in ladder)
      + f" | monotone: old={all(agg[ladder[i]][0] > agg[ladder[i+1]][0] for i in range(4))}, new={all(agg[ladder[i]][1] > agg[ladder[i+1]][1] for i in range(4))}",
      f"- LoRA effect J0−J, old: {100*(agg['J0_small_hf_vanilla'][0]-agg['J_lora_small'][0]):+.1f} pts | new: {100*(agg['J0_small_hf_vanilla'][1]-agg['J_lora_small'][1]):+.1f} pts",
      f"- Prompt effect B−D, old: {100*(agg['B_noise_reduction'][0]-agg['D_domain_prompt'][0]):+.1f} | new: {100*(agg['B_noise_reduction'][1]-agg['D_domain_prompt'][1]):+.1f}",
      f"- Forced language D−E, old: {100*(agg['D_domain_prompt'][0]-agg['E_forced_language'][0]):+.1f} | new: {100*(agg['D_domain_prompt'][1]-agg['E_forced_language'][1]):+.1f}",
      f"- MMS (K) vs J0, old: {100*agg['K_wav2vec'][0]:.1f} vs {100*agg['J0_small_hf_vanilla'][0]:.1f} | new: {100*agg['K_wav2vec'][1]:.1f} vs {100*agg['J0_small_hf_vanilla'][1]:.1f}"]
conf = [r for r in rows if r.get("condition_tag", "").startswith("L_conformer")]
L.append(f"- Conformer global, old: {100*st.mean(x['_wo'] for x in conf):.1f} | new: {100*st.mean(x['_wn'] for x in conf):.1f}")

A = [r for r in rows if r.get("condition_tag") == "A_baseline"]
stem = lambda fn: re.match(r"minds14_(\w\w)_(clean|noisy)_(\d+)\.wav", fn).group(1, 3)
cmap = {stem(r["filename"]): r for r in A if r["noise_condition"] == "clean"}
pairs = [(cmap[stem(r["filename"])], r) for r in A if r["noise_condition"] == "noisy"]
for lab, k in (("old", "_wo"), ("new", "_wn")):
    c = st.mean(p[0][k] for p in pairs); n = st.mean(p[1][k] for p in pairs)
    L.append(f"- Paired noise penalty (12 pairs), {lab}: clean {100*c:.1f} → noisy {100*n:.1f}, {100*(n-c):+.1f} pts")

L += ["\n## Reading\n",
      "- Absolute WER levels in the manuscript are inflated by reference defects in 5/24 clean files (21 %).",
      "- Every ordering the manuscript relies on survives the correction (see checks). Magnitudes drop by several points across the board.",
      "- Because the corrected wording comes from large-v3, its own advantage at the top of the ladder is overstated here; the honest",
      "  statement is that the ladder is monotone under both the original and the corrected references, not that the corrected gap is exact.",
      "- Recommended: (1) declare MInDS-14 transcript quality as a limitation; (2) keep canonical files; (3) commission a word-by-word",
      "  human transcription of the 5 clips before republishing any corrected figure; (4) rescore in a separate revision then."]
(OUT / "06b_reference_revision_all.md").write_text("\n".join(L) + "\n", encoding="utf-8")
with open(OUT / "06b_reference_revision_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["source", "filename", "condition_tag", "model", "wer_old", "wer_new", "cer_old", "cer_new"])
    for r in changed: w.writerow([r["_src"], r["filename"], r.get("condition_tag", ""), r["model"], r["_wo"], round(r["_wn"], 4), r["_co"], round(r["_cn"], 4)])
print("\n".join(L[L.index("## Order checks\n") - 1:]))
