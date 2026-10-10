"""Recompute the headline contrasts. Pairs only for the noise effect."""
import csv, random, re, statistics as st
from pathlib import Path
from collections import defaultdict
ROOT = Path(__file__).resolve().parents[3]

def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f: return list(csv.DictReader(f))

pilot = load("results/stt_eval_pilot_results.csv")
def F(r,k):
    try: return float(r[k])
    except: return None

out = ["# Headline contrasts, recomputed\n"]

# ---- 1. noise, condition A (baseline, tiny) ----
A = [r for r in pilot if r["condition_tag"] == "A_baseline"]
clean = [r for r in A if r["noise_condition"] == "clean"]
noisy = [r for r in A if r["noise_condition"] == "noisy"]
out.append(f"## Noise effect, condition A_baseline (model tiny)\n")
out.append(f"- clean rows: {len(clean)}, noisy rows: {len(noisy)}")
out.append(f"- **Descriptive split** (different utterances): clean mean WER "
           f"= {100*st.mean(F(r,'wer') for r in clean):.1f}%, noisy = {100*st.mean(F(r,'wer') for r in noisy):.1f}%")

# pair by stem index: minds14_<lang>_noisy_NN <-> minds14_<lang>_clean_NN
def stem(fn): 
    m = re.match(r"minds14_(\w\w)_(clean|noisy)_(\d+)\.wav", fn); return (m.group(1), m.group(3)) if m else None
cmap = {stem(r["filename"]): r for r in clean}
pairs = [(cmap[stem(r["filename"])], r) for r in noisy if stem(r["filename"]) in cmap]
out.append(f"- **Matched pairs found: {len(pairs)}**")
pc = [F(c,'wer') for c,_ in pairs]; pn = [F(n,'wer') for _,n in pairs]
out.append(f"- **Paired** clean = {100*st.mean(pc):.1f}%, noisy = {100*st.mean(pn):.1f}%, "
           f"penalty = **{100*(st.mean(pn)-st.mean(pc)):.1f} points**")

# paired bootstrap, resampling PAIRS (keeps derivative with its source)
random.seed(42); B=10000
diffs = [n-c for c,n in zip(pc,pn)]
boots = sorted(st.mean(random.choices(diffs, k=len(diffs))) for _ in range(B))
lo, hi = boots[int(.025*B)], boots[int(.975*B)]
out.append(f"- Paired bootstrap 95% CI on the penalty (unit = pair, seed=42, B={B}): "
           f"**[{100*lo:.1f}, {100*hi:.1f}] points**")

# ---- 2. estimator: mean-of-WER vs aggregate ----
out.append("\n## Estimator sensitivity (condition A, all 36 files)\n")
import string as _s
PUNCT=_s.punctuation+"\u2018\u2019\u201c\u201d\u2014\u2013"
def norm(t): return re.sub(r"\s+"," ",t.lower().translate(str.maketrans("","",PUNCT))).strip()
def ed(a,b):
    if len(a)<len(b): a,b=b,a
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(prev[j-1] if ca==cb else 1+min(prev[j],cur[j-1],prev[j-1]))
        prev=cur
    return prev[-1]
errs=sum(ed(norm(r["reference_text"]).split(), norm(r["hypothesis_text"]).split()) for r in A)
words=sum(len(norm(r["reference_text"]).split()) for r in A)
out.append(f"- mean-of-per-file WER = **{100*st.mean(F(r,'wer') for r in A):.1f}%**")
out.append(f"- corpus-aggregate WER (total edits / total ref words) = **{100*errs/words:.1f}%**")
out.append(f"- rows with WER > 100%: {sum(1 for r in A if F(r,'wer')>1)} (unbounded, inflates the mean)")

# ---- 3. model ladder ----
out.append("\n## Model-size ladder (mean-of-per-file WER)\n| condition | model | n | backend | WER |\n|---|---|---:|---|---:|")
by = defaultdict(list)
for r in pilot: by[(r["condition_tag"], r["model"])].append(r)
for (tag, model), rs in sorted(by.items()):
    out.append(f"| {tag} | {model} | {len(rs)} | - | {100*st.mean(F(r,'wer') for r in rs):.1f}% |")

# ---- 4. cross-architecture + LoRA ----
out.append("\n## Cross-architecture and LoRA\n")
for rel, name in [("results/stt_eval_wav2vec_results.csv","wav2vec/MMS"),
                  ("results/stt_eval_conformer_results.csv","Conformer"),
                  ("results/stt_eval_lora_results.csv","LoRA study")]:
    rs = load(rel)
    b = defaultdict(list)
    for r in rs: b[r["condition_tag"]].append(r)
    for tag, g in sorted(b.items()):
        out.append(f"- {name} / `{tag}`: n={len(g)}, WER = **{100*st.mean(F(r,'wer') for r in g):.1f}%**")

txt="\n".join(out)+"\n"
(ROOT/"audits/pre_defense"/Path(__file__).parent.name/"03b_contrasts.md").write_text(txt,encoding="utf-8")
print(txt)
