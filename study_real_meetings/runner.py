"""Apply one condition and one transcriber to segments; append one row per segment."""
from __future__ import annotations

import csv
import importlib.metadata
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from study_real_meetings.audio import load_segment
from study_real_meetings.config import DATA, DOMAIN_PROMPT, ROOT, SAMPLE_RATE, SEED
from study_real_meetings.manifest import Segment
from study_real_meetings.noise import mix_at_snr, pick_noise
from study_real_meetings.text import has_repetition_loop, score_chars, score_words, term_hits

FIELDS = [
    "hypothesis_id", "dataset", "language", "segment_id", "pair_key", "cluster", "split", "speaker",
    "duration_s", "system", "model_id", "compute_type", "condition", "forced_language", "snr_db",
    "noise_type", "prompt", "denoise", "reference", "hypothesis", "detected_language",
    "n_ref", "sub", "del", "ins", "n_ref_num", "errors_num", "c_ref", "c_errors",
    "term_hits", "term_total", "repetition_loop", "proc_s", "rtf",
    "git_commit", "packages", "gpu", "timestamp",
]


@dataclass(frozen=True)
class Condition:
    forced_language: bool = True
    snr_db: float | None = None
    prompt: bool = False
    denoise: bool = False

    @property
    def name(self) -> str:
        parts = ["forced" if self.forced_language else "auto",
                 "clean" if self.snr_db is None else f"snr{self.snr_db:g}"]
        if self.prompt:
            parts.append("prompt")
        if self.denoise:
            parts.append("denoise")
        return "-".join(parts)


def prepare_audio(segment: Segment, condition: Condition, bank, seed: int = SEED,
                  data_root: Path = DATA) -> tuple[np.ndarray, str]:
    audio = load_segment(data_root / segment.audio_path, segment.start, segment.end)
    noise_type = ""
    if condition.snr_db is not None:
        noise_type, noise = pick_noise(bank, segment.segment_id, condition.snr_db, len(audio), seed)
        audio = mix_at_snr(audio, noise, condition.snr_db)
    if condition.denoise:
        import noisereduce as nr
        audio = nr.reduce_noise(y=audio, sr=SAMPLE_RATE).astype(np.float32)
    return audio, noise_type


def collect_provenance() -> dict[str, str]:
    def git(*args):
        return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout.strip()

    dirty = bool(git("status", "--porcelain", "--", "study_real_meetings", "backend"))
    versions = {}
    for pkg in ("torch", "faster-whisper", "ctranslate2", "transformers", "nemo-toolkit",
                "peft", "noisereduce", "num2words", "pyannote.audio"):
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "absent"
    import torch
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    return {"git_commit": git("rev-parse", "HEAD") + ("-dirty" if dirty else ""),
            "packages": json.dumps(versions, sort_keys=True), "gpu": gpu}


def read_rows(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run(segments, transcriber, condition: Condition, *, hypothesis_id: str, out_csv: Path,
        bank=None, provenance: dict[str, str], seed: int = SEED, data_root: Path = DATA) -> int:
    out_csv = Path(out_csv)
    done = {(r["segment_id"], r["system"], r["condition"]) for r in read_rows(out_csv)}
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    new_file = not out_csv.exists()
    written = 0
    with open(out_csv, "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for seg in segments:
            if (seg.segment_id, transcriber.system, condition.name) in done:
                continue
            audio, noise_type = prepare_audio(seg, condition, bank, seed, data_root)
            result = transcriber.transcribe(
                audio, language=seg.language if condition.forced_language else None,
                prompt=DOMAIN_PROMPT if condition.prompt else None)
            words = score_words(seg.reference, result.text, seg.language)
            words_num = score_words(seg.reference, result.text, seg.language, numbers_to_words=True)
            chars = score_chars(seg.reference, result.text, seg.language)
            hits, total = term_hits(seg.reference, result.text, seg.language)
            duration = len(audio) / SAMPLE_RATE
            writer.writerow({
                "hypothesis_id": hypothesis_id, "dataset": seg.dataset, "language": seg.language,
                "segment_id": seg.segment_id, "pair_key": seg.pair_key, "cluster": seg.cluster,
                "split": seg.split, "speaker": seg.speaker, "duration_s": f"{duration:.3f}",
                "system": transcriber.system, "model_id": transcriber.model_id,
                "compute_type": transcriber.compute_type, "condition": condition.name,
                "forced_language": int(condition.forced_language),
                "snr_db": "" if condition.snr_db is None else f"{condition.snr_db:g}",
                "noise_type": noise_type, "prompt": int(condition.prompt), "denoise": int(condition.denoise),
                "reference": seg.reference, "hypothesis": result.text,
                "detected_language": result.detected_language or "",
                "n_ref": words.n_ref, "sub": words.sub, "del": words.dele, "ins": words.ins,
                "n_ref_num": words_num.n_ref, "errors_num": words_num.errors,
                "c_ref": chars.n_ref, "c_errors": chars.errors,
                "term_hits": hits, "term_total": total,
                "repetition_loop": int(has_repetition_loop(result.text, seg.language)),
                "proc_s": f"{result.seconds:.4f}",
                "rtf": f"{result.seconds / duration:.4f}" if duration else "",
                **provenance, "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            handle.flush()
            written += 1
    return written
