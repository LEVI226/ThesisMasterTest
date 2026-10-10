"""Read-only audit of stored evidence; no model inference or canonical writes."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.evaluation.metrics import wer, normalize_text
from backend.evaluation.dataset import load_metadata, validate_samples
import soundfile as sf
import numpy as np

OUT = Path(__file__).parent
def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

report = {"scope": "Stored evidence and local file checks; no inference"}
samples = load_metadata(str(ROOT / "datasets/stt_eval/metadata.csv"))
report["dataset"] = {"files": len(samples), "reference_files": len({s.reference_path for s in samples}),
                     "missing": validate_samples(samples), "languages": dict(Counter(s.language for s in samples))}
audio = {}
for s in samples:
    x, sr = sf.read(s.audio_path)
    audio[s.audio_filename] = (x, sr)
report["dataset"]["sample_rates"] = dict(Counter(sr for x, sr in audio.values()))
report["dataset"]["noise_snr_db_measured"] = []
for name, (x, sr) in audio.items():
    if "_noisy_" in name:
        clean, csr = audio[name.replace("_noisy_", "_clean_")]
        if x.shape == clean.shape and sr == csr:
            snr = 10 * np.log10(np.mean(clean ** 2) / np.mean((x-clean) ** 2))
            report["dataset"]["noise_snr_db_measured"].append({"file": name, "snr": float(snr)})

report["csvs"] = {}
paths = defaultdict(list)
for name in ["stt_eval_pilot_results.csv", "stt_eval_lora_results.csv", "stt_eval_wav2vec_results.csv", "stt_eval_conformer_results.csv"]:
    path = ROOT / "results" / name
    data = rows(path)
    groups = defaultdict(list)
    differences = []
    for r in data:
        groups[r["condition_tag"]].append(float(r["wer"]))
        differences.append(abs(wer(r["reference_text"], r["hypothesis_text"]) - float(r["wer"])))
        if r.get("transcript_output_path"):
            paths[r["transcript_output_path"]].append((name, r))
    report["csvs"][name] = {
        "rows": len(data), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "errors": sum(bool(r.get("error")) for r in data),
        "empty_references": sum(not r["reference_text"].strip() for r in data),
        "empty_hypotheses": sum(not r["hypothesis_text"].strip() for r in data),
        "duplicate_keys": len(data)-len({(r["filename"],r["condition_tag"]) for r in data}),
        "max_stored_wer_difference": max(differences),
        "groups": {tag: {"n": len(v), "mean_wer": sum(v)/len(v)} for tag,v in groups.items()}}
report["transcript_sidecars"] = {
    "paths_shared_by_multiple_rows": sum(len(v)>1 for v in paths.values()),
    "missing_paths": sum(not (ROOT / p).exists() for p in paths),
    "row_hypotheses_differing_from_current_sidecar": sum(
        (ROOT / p).read_text(encoding="utf-8").strip()!=r["hypothesis_text"].strip()
        for p, group in paths.items() if (ROOT / p).exists() for _,r in group)}
train = rows(ROOT / "datasets/lora_train/manifest.csv")
norm = lambda x: re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", x.lower().strip())).strip()
refs = {norm(s.reference_path.read_text(encoding="utf-8")) for s in samples}
eval_hashes = {hashlib.sha256(s.audio_path.read_bytes()).hexdigest() for s in samples}
report["training"] = {"rows": len(train), "languages": dict(Counter(r["language"] for r in train)),
    "missing_audio": sum(not (ROOT/r["audio_path"]).exists() for r in train),
    "exact_normalized_text_overlap": sum(norm(r["transcription"]) in refs for r in train),
    "identical_audio_file_overlap": sum(hashlib.sha256((ROOT/r["audio_path"]).read_bytes()).hexdigest() in eval_hashes for r in train if (ROOT/r["audio_path"]).exists()),
    "limitation": "Exact text/file checks do not prove independent speakers or absence of near duplicates."}
(OUT / "evidence_checks.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
