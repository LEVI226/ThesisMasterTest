"""Bounded REAL inference through the file path that /transcribe uses.

Calls transcribe_file(path, forced_language=...) — the exact call the fixed
endpoint makes — with the application's default config (preprocessing on,
Nestlé domain prompt on, VAD off). Device/precision are taken from the
environment (STT_DEVICE / STT_COMPUTE_TYPE) so a caller can force cpu/int8.
Scores with the canonical scorer. Writes only into this run folder.

RTF scope: ``engine_processing_s`` is transcribe_file's own timer (after model
load, includes preprocessing and decoding); ``wall_s`` wraps the whole call
from this script. Neither includes model loading, which is reported once.
"""
import csv, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).parent
LABEL = sys.argv[1] if len(sys.argv) > 1 else "default"
os.environ.setdefault("TRANSCRIPT_DIR", str(OUT / "transcripts" / LABEL))

from backend.evaluation.metrics import wer, cer
from backend.stt.engine import transcribe_file, load_model, get_model_info, get_audio_duration

SAMPLES = [  # (audio, reference, true language)
    ("minds14_en_clean_01", "en"), ("minds14_fr_clean_01", "fr"), ("minds14_de_clean_01", "de"),
    ("minds14_fr_noisy_01", "fr"), ("minds14_de_noisy_01", "de"),
]
AUDIO = ROOT / "datasets/stt_eval/audio"
REFS = ROOT / "datasets/stt_eval/references"

t0 = time.perf_counter()
load_model("small")
load_s = round(time.perf_counter() - t0, 3)
info = get_model_info()
print("loaded:", info, "in", load_s, "s")

rows = []
for stem, lang in SAMPLES:
    audio = AUDIO / f"{stem}.wav"
    ref_name = stem.replace("_noisy_", "_clean_")  # noisy variants reuse the clean reference
    ref = (REFS / f"{ref_name}.txt").read_text(encoding="utf-8").strip()
    dur = get_audio_duration(str(audio))
    for mode, forced in (("auto", None), ("forced", lang)):
        t1 = time.perf_counter()
        err = None
        try:
            res = transcribe_file(str(audio), forced_language=forced)
        except Exception as e:
            res, err = {}, repr(e)
        wall = round(time.perf_counter() - t1, 3)
        hyp = (res.get("text") or "").strip()
        row = {
            "label": LABEL, "file": stem, "true_language": lang, "mode": mode,
            "forced_language": forced, "detected_language": res.get("language"),
            "model": info["model"], "device": info["device"], "compute_type": info["compute_type"],
            "reference": ref, "hypothesis": hyp,
            "wer": round(wer(ref, hyp), 4) if hyp or not err else None,
            "cer": round(cer(ref, hyp), 4) if hyp or not err else None,
            "audio_s": round(dur, 3), "engine_processing_s": res.get("processing_time"),
            "wall_s": wall, "rtf_wall": round(wall / dur, 3) if dur else None,
            "error": err,
        }
        rows.append(row)
        print(f"  {stem:22s} {mode:6s} det={row['detected_language']!s:5s} "
              f"WER={row['wer']!s:7s} wall={wall:6.2f}s  {hyp[:60]!r}")

report = {
    "scope": "real inference via transcribe_file (the /transcribe call); app default config: "
             "preprocessing=True, domain_prompt=True (Nestlé), vad=False, word_timestamps=True; "
             "no HTTP, no diarization, no browser",
    "model_loaded": info, "model_load_s": load_s,
    "env": {k: os.environ.get(k) for k in ("STT_DEVICE", "STT_COMPUTE_TYPE", "CUDA_VISIBLE_DEVICES", "WHISPER_MODEL")},
    "rtf_scope": "rtf_wall = wall_s / audio_s around the whole transcribe_file call, excluding model load",
    "rows": rows,
}
(OUT / f"04_file_smoke_{LABEL}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
with open(OUT / f"04_file_smoke_{LABEL}.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print("written:", OUT / f"04_file_smoke_{LABEL}.json")
