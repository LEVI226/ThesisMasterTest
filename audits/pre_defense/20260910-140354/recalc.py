"""Independent recalculation of the canonical STT campaign.
Does NOT import backend.evaluation.metrics: the scorer is reimplemented here
(two-row DP) so that a bug in the canonical scorer cannot validate itself.
Reads only; writes nothing outside the audit directory.
"""
import csv, hashlib, re, string, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[3]
PUNCT = string.punctuation + "\u2018\u2019\u201c\u201d\u2014\u2013"

def norm(t):
    t = t.lower().translate(str.maketrans("", "", PUNCT))
    return re.sub(r"\s+", " ", t).strip()

def edit_distance(a, b):
    """Two-row Wagner-Fischer. Returns total edit distance only."""
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(prev[j - 1] if ca == cb else 1 + min(prev[j], cur[j - 1], prev[j - 1]))
        prev = cur
    return prev[-1]

def wer_of(ref, hyp):
    r, h = norm(ref).split(), norm(hyp).split()
    if not r: return None            # empty reference: undefined, NOT zero
    return edit_distance(r, h) / len(r)

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

CANONICAL = {
    "results/stt_eval_pilot_results.csv": "pilot+ladder+VAD",
    "results/stt_eval_lora_results.csv": "LoRA paired",
    "results/stt_eval_wav2vec_results.csv": "wav2vec/MMS",
    "results/stt_eval_conformer_results.csv": "Conformer",
}

rows, report = [], []
report.append("# 03 Results recalculation (independent scorer)\n")
report.append("## File inventory and hashes\n")
report.append("| file | rows | sha256 (first 16) | role |")
report.append("|---|---:|---|---|")

total = 0
for rel, role in CANONICAL.items():
    p = ROOT / rel
    with open(p, encoding="utf-8") as f:
        rr = list(csv.DictReader(f))
    for r in rr: r["_src"] = rel
    rows += rr
    total += len(rr)
    report.append(f"| `{rel}` | {len(rr)} | `{sha256(p)[:16]}` | {role} |")
report.append(f"\n**Canonical total: {total} runs** (claimed 468: "
              f"{'MATCH' if total == 468 else 'MISMATCH'}).\n")

# non-canonical files present in results/ must not be summed in
report.append("Excluded from the canonical total (present but out of campaign):\n")
for p in sorted((ROOT / "results").glob("*.csv")):
    rel = f"results/{p.name}"
    if rel not in CANONICAL:
        with open(p, encoding="utf-8") as f:
            n = sum(1 for _ in csv.reader(f)) - 1
        report.append(f"- `{rel}` ({n} rows)")

# duplicates
report.append("\n## Duplicate / error / empty checks\n")
key = lambda r: (r["_src"], r.get("filename",""), r.get("model",""), r.get("condition_tag",""),
                 r.get("preprocessing_enabled",""), r.get("domain_prompt_enabled",""),
                 r.get("forced_language",""))
seen = defaultdict(int)
for r in rows: seen[key(r)] += 1
dups = {k: v for k, v in seen.items() if v > 1}
report.append(f"- Duplicate (source, file, model, condition, flags) keys: **{len(dups)}**")
for k, v in list(dups.items())[:10]:
    report.append(f"  - {v}x {k}")

errs = [r for r in rows if (r.get("error") or "").strip()]
report.append(f"- Rows carrying a non-empty `error` field: **{len(errs)}**")
empty_ref = [r for r in rows if not norm(r.get("reference_text") or "")]
empty_hyp = [r for r in rows if not norm(r.get("hypothesis_text") or "")]
report.append(f"- Rows with EMPTY reference (WER undefined, must not score 0): **{len(empty_ref)}**")
report.append(f"- Rows with EMPTY hypothesis (real failure, must score 1.0): **{len(empty_hyp)}**")

# recompute
report.append("\n## Stored vs recomputed WER\n")
diffs, undef, big = [], 0, []
for r in rows:
    rec = wer_of(r.get("reference_text") or "", r.get("hypothesis_text") or "")
    if rec is None:
        undef += 1; continue
    try: stored = float(r["wer"])
    except (TypeError, ValueError): continue
    d = abs(rec - stored)
    diffs.append(d)
    if d > 1e-6:
        big.append((r["_src"], r.get("filename"), r.get("model"), r.get("condition_tag"), stored, rec))
report.append(f"- Rows recomputed: **{len(diffs)}** (undefined refs skipped: {undef})")
report.append(f"- Max |stored - recomputed|: **{max(diffs) if diffs else 0:.2e}**")
report.append(f"- Rows disagreeing beyond 1e-6: **{len(big)}**")
for b in big[:15]:
    report.append(f"  - {b[0]} {b[1]} {b[2]} {b[3]}: stored={b[4]:.4f} recomputed={b[5]:.4f}")

over = [r for r in rows if _f(r) is not None and _f(r) > 1.0] if False else []
def _f(r):
    try: return float(r["wer"])
    except: return None
over = [r for r in rows if (_f(r) or 0) > 1.0]
report.append(f"- Rows with WER > 100%: **{len(over)}**")

Path(ROOT / sys.argv[1]).write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
