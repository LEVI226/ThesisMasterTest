"""
Pilot evaluation run for Topic 2 thesis -- Section 5.3 Experimental Conditions.

Covers Conditions A, B, D, E, F as defined in Topic2_Outline_Reference.md:
  A - Baseline: faster-whisper, no preprocessing, no domain prompt
  B - Noise reduction applied (noisereduce, via TranscribeConfig.preprocessing)
  D - Domain vocabulary prompt injected (Nestle brand/exec names)
  E - Forced language (per-sample true language) vs automatic language detection
  F - Model size comparison (tiny vs base; small/medium/large-v2 were judged too
      heavy to download/run within this sandbox's CPU-only, no-GPU environment --
      the comparison axis is preserved, the absolute sizes are substituted)

Condition C (VAD preprocessing with Silero) is INTENTIONALLY OMITTED:
  backend/stt/engine.py defines load_vad_model() but transcribe_file() never calls
  it -- VAD is not actually wired into the transcription path. This is reported as
  a methodological finding/limitation rather than silently faked.

Dataset: PolyAI/minds14 (CC-BY-4.0), real telephone-banking speech in en/fr/de,
24 clean clips + 12 synthetic-noisy variants (white noise @ 8dB SNR). See
datasets/stt_eval/metadata.csv and README.md for full provenance notes.

RESUMABLE DESIGN: this script is meant to be invoked repeatedly (each invocation
is time-boxed via --max-seconds). It appends completed rows to OUTPUT_CSV
immediately and on the next invocation skips any (condition_tag, filename) pair
already present in that file, so a long matrix can be completed across many
short process lifetimes without losing progress.
"""
import sys
import csv
import time
import argparse
from pathlib import Path
from dataclasses import asdict, fields

sys.path.insert(0, ".")

from backend.evaluation.dataset import load_metadata, validate_samples
from backend.evaluation.runner import EvalResult, SAMPLE_LANGUAGE, run_single

OUTPUT_CSV = Path("results/stt_eval_pilot_results.csv")
LOG_PATH = Path("results/pilot_run.log")

CONDITIONS = [
    dict(tag="A_baseline", model="tiny", preprocessing=False, domain_prompt=False, forced_language=None),
    dict(tag="B_noise_reduction", model="tiny", preprocessing=True, domain_prompt=False, forced_language=None),
    dict(tag="C_vad", model="tiny", preprocessing=True, domain_prompt=False, forced_language=None, vad=True),
    dict(tag="D_domain_prompt", model="tiny", preprocessing=True, domain_prompt=True, forced_language=None),
    dict(tag="E_forced_language", model="tiny", preprocessing=True, domain_prompt=True, forced_language=SAMPLE_LANGUAGE),
    dict(tag="F_model_base", model="base", preprocessing=True, domain_prompt=False, forced_language=None),
    dict(tag="G_model_small", model="small", preprocessing=True, domain_prompt=False, forced_language=None),
    dict(tag="H_model_medium", model="medium", preprocessing=True, domain_prompt=False, forced_language=None),
    dict(tag="I_model_large_v3", model="large-v3", preprocessing=True, domain_prompt=False, forced_language=None),
]

# Existing canonical pilot CSVs identify VAD through condition_tag. Keep their
# stable schema when resuming, while the generic runner records vad_enabled.
FIELDNAMES = [f.name for f in fields(EvalResult) if f.name != "vad_enabled"] + ["condition_tag"]


def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = "[" + ts + "] " + msg
    print(line, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_done_set():
    done = set()
    if OUTPUT_CSV.exists():
        with open(OUTPUT_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                done.add((row["condition_tag"], row["filename"]))
    return done


def append_row(row):
    new_file = not OUTPUT_CSV.exists()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerow(dict((k, row.get(k, "")) for k in FIELDNAMES))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-seconds", type=float, default=33.0)
    args = parser.parse_args()

    t_start = time.time()
    deadline = t_start + args.max_seconds

    samples = load_metadata("datasets/stt_eval/metadata.csv")
    for w in validate_samples(samples):
        log("WARNING: " + w)
    samples = [s for s in samples if s.audio_path.exists() and s.reference_path.exists()]

    done = load_done_set()
    total = len(samples) * len(CONDITIONS)
    log("Loaded " + str(len(samples)) + " valid samples | " + str(len(done)) + "/" + str(total) + " already done | budget=" + str(args.max_seconds) + "s")

    processed_this_call = 0
    stopped_early = False

    for cond in CONDITIONS:
        for sample in samples:
            key = (cond["tag"], sample.audio_filename)
            if key in done:
                continue
            if time.time() >= deadline:
                stopped_early = True
                break

            forced_lang = sample.language if cond["forced_language"] == SAMPLE_LANGUAGE else cond["forced_language"]
            try:
                result = run_single(
                    sample,
                    preprocessing=cond["preprocessing"],
                    domain_prompt=cond["domain_prompt"],
                    forced_language=forced_lang,
                    model_size=cond["model"],
                    vad=cond.get("vad", False),
                )
                row = asdict(result)
                row["condition_tag"] = cond["tag"]
                append_row(row)
                done.add(key)
                processed_this_call += 1
                log("  done " + cond["tag"] + "/" + sample.audio_filename + " | WER=%.3f CER=%.3f RTF=%.3f" % (result.wer, result.cer, result.real_time_factor))
            except Exception as e:
                log("  ERROR " + cond["tag"] + "/" + sample.audio_filename + ": " + str(e))
                append_row({
                    "filename": sample.audio_filename, "condition_tag": cond["tag"],
                    "language": sample.language, "noise_condition": sample.noise_condition,
                    "speaker_count": sample.speaker_count, "model": cond["model"],
                    "preprocessing_enabled": cond["preprocessing"], "domain_prompt_enabled": cond["domain_prompt"],
                    "forced_language": forced_lang, "duration_audio_seconds": 0, "processing_time_seconds": 0,
                    "real_time_factor": float("inf"), "wer": float("nan"), "cer": float("nan"),
                    "transcript_output_path": "", "reference_text": "", "hypothesis_text": "", "error": str(e),
                })
                done.add(key)
        if stopped_early:
            break

    elapsed = time.time() - t_start
    remaining = total - len(done)
    log("Call finished: processed " + str(processed_this_call) + " this call in %.1fs" % elapsed + " | " + str(len(done)) + "/" + str(total) + " total done | " + str(remaining) + " remaining")
    if remaining == 0:
        log("PILOT MATRIX COMPLETE.")


if __name__ == "__main__":
    main()
