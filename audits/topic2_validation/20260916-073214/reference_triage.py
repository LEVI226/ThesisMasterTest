"""Triage the 24 clean references using hypotheses ALREADY in the canonical CSVs
from three independent architectures. Agreement between models is a signal for
where a human should listen first; it is never a verdict on the reference."""
import csv, re, string
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
PUNCT = string.punctuation + "‘’“”—–"
def norm(t): return re.sub(r"\s+", " ", (t or "").lower().translate(str.maketrans("", "", PUNCT))).strip()

SRC = {"whisper_large_v3": ("results/stt_eval_pilot_results.csv", "I_model_large_v3"),
       "mms":              ("results/stt_eval_wav2vec_results.csv", "K_wav2vec"),
       "conformer":        ("results/stt_eval_conformer_results.csv", None)}
hyp = defaultdict(dict); ref = {}
for name, (rel, tag) in SRC.items():
    with open(ROOT / rel, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["noise_condition"] != "clean": continue
            if tag and r["condition_tag"] != tag: continue
            hyp[r["filename"]][name] = norm(r["hypothesis_text"]); ref[r["filename"]] = norm(r["reference_text"])

rows = []
for fn in sorted(ref):
    rw = set(ref[fn].split())
    extra = {}   # model -> words in hypothesis not in reference
    for m, h in hyp[fn].items():
        extra[m] = [w for w in h.split() if w not in rw]
    # words missing from reference that at least 2 of 3 models produce
    counts = defaultdict(int)
    for m, ws in extra.items():
        for w in set(ws): counts[w] += 1
    agreed = sorted(w for w, c in counts.items() if c >= 2)
    n_models = len(hyp[fn]); longer = sum(1 for h in hyp[fn].values() if len(h.split()) > len(ref[fn].split()) + 2)
    if len(agreed) >= 3 or (longer >= 2 and len(agreed) >= 2): pri = "LISTEN FIRST"
    elif agreed: pri = "listen"
    else: pri = "low"
    rows.append({"file": fn, "language": fn.split("_")[1], "reference": ref[fn], "ref_words": len(rw),
                 "models_available": n_models, "models_longer_than_ref": longer,
                 "extra_words_agreed_by_2plus_models": " ".join(agreed), "priority": pri,
                 **{f"hyp_{m}": hyp[fn].get(m, "") for m in SRC}})
order = {"LISTEN FIRST": 0, "listen": 1, "low": 2}
rows.sort(key=lambda r: (order[r["priority"]], r["file"]))
with open(OUT / "07_reference_triage.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['priority']:12s} {r['file']:26s} {r['language']} agreed_extra=[{r['extra_words_agreed_by_2plus_models']}] longer={r['models_longer_than_ref']}/{r['models_available']}")
print("\nwritten:", OUT / "07_reference_triage.csv")
