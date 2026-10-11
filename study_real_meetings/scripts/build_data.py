"""Download, convert and segment every study source.

Usage (from repo root):
  .venv/Scripts/python.exe -m study_real_meetings.scripts.build_data --agm-dir "<folder with AGM mp3+srt>"
Idempotent: existing converted files are reused.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import pyarrow.parquet as pq
import soundfile as sf
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download

from study_real_meetings import config as C
from study_real_meetings.audio import convert_to_wav16k, wav_duration, write_wav
from study_real_meetings.manifest import Segment, write_manifest
from study_real_meetings.noise import load_demand_bank, stable_rng
from study_real_meetings.sources import agm, ami, summre


def rel(path: Path) -> str:
    return path.relative_to(C.DATA).as_posix()


def build_agm(agm_dir: Path) -> list[Segment]:
    segments: list[Segment] = []
    for lang, (src, srt) in agm.find_agm_files(agm_dir).items():
        wav = C.AUDIO / "agm" / f"agm_{lang}.wav"
        if not wav.exists():
            convert_to_wav16k(src, wav)
        text = srt.read_text(encoding="utf-8-sig")
        (C.RAW / "agm").mkdir(parents=True, exist_ok=True)
        (C.RAW / "agm" / f"agm_{lang}.srt").write_text(text, encoding="utf-8")
        segments += agm.build_agm_segments(lang, text, rel(wav), wav_duration(wav))
    return segments


def _decode(audio_struct: dict) -> np.ndarray:
    audio, sr = sf.read(io.BytesIO(audio_struct["bytes"]), dtype="float32", always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != C.SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=C.SAMPLE_RATE)
    return audio.astype(np.float32)


def build_ami(token: str | None) -> dict[str, list[Segment]]:
    out: dict[str, list[Segment]] = {}
    files = HfApi(token=token).list_repo_files(C.AMI_REPO, repo_type="dataset")
    for mic in ("ihm", "sdm"):
        segments: list[Segment] = []
        for shard in sorted(f for f in files if f.startswith(f"{mic}/test-")):
            local = hf_hub_download(C.AMI_REPO, shard, repo_type="dataset", token=token)
            for batch in pq.ParquetFile(local).iter_batches(batch_size=256):
                for row in ami.select_rows(batch.to_pylist(), C.AMI_MEETINGS, C.AMI_MIN_S, C.AMI_MAX_S):
                    wav = C.AUDIO / f"ami-{mic}" / f"{ami.pair_key(row)}.wav"
                    if not wav.exists():
                        write_wav(wav, _decode(row["audio"]))
                    segments.append(ami.segment_for_row(row, mic, rel(wav)))
        out[f"ami-{mic}"] = sorted(segments, key=lambda s: s.segment_id)
    return out


def build_summre(token: str | None) -> list[Segment]:
    files = HfApi(token=token).list_repo_files(C.SUMMRE_REPO, repo_type="dataset")
    recordings = sorted({Path(f).name.split("_anon")[0] for f in files
                         if f.startswith("audio_anonymized/") and Path(f).name.startswith(C.SUMMRE_MEETINGS)})
    segments: list[Segment] = []
    by_meeting: dict[str, list[tuple[str, Path, list]]] = defaultdict(list)
    for rec in recordings:
        meeting, participant = rec.rsplit("_", 1)
        src = hf_hub_download(C.SUMMRE_REPO, f"audio_anonymized/{rec}_anon.wav", repo_type="dataset", token=token)
        gold = hf_hub_download(C.SUMMRE_REPO, f"gold_transcriptions/csv/{rec}_anon.csv", repo_type="dataset", token=token)
        ext = hf_hub_download(C.SUMMRE_REPO,
                              f"whisper_transcriptions/{C.SUMMRE_EXTERNAL_WHISPER}/csv/{rec}-palign_anon.csv",
                              repo_type="dataset", token=token)
        wav = C.AUDIO / "summre" / f"{rec}.wav"
        if not wav.exists():
            convert_to_wav16k(Path(src), wav)
        tokens = summre.parse_tokens(Path(gold).read_text(encoding="utf-8-sig"))
        external = summre.parse_tokens(Path(ext).read_text(encoding="utf-8-sig"))
        tok_dir = C.RAW / "summre" / "tokens"
        tok_dir.mkdir(parents=True, exist_ok=True)
        (tok_dir / f"{rec}.json").write_text(json.dumps({
            "gold": [[t.start, t.end, t.text] for t in tokens],
            "external_whisper": [[t.start, t.end, t.text] for t in external],
        }, ensure_ascii=False), encoding="utf-8")
        segments += summre.build_summre_segments(meeting, participant, tokens, rel(wav))
        by_meeting[meeting].append((participant, wav, tokens))
    for meeting, channels in by_meeting.items():  # D1: summed mix + reference RTTM
        audios = [sf.read(str(w), dtype="float32")[0] for _, w, _ in channels]
        mix = np.zeros(max(len(a) for a in audios), dtype=np.float32)
        for a in audios:
            mix[: len(a)] += a
        write_wav(C.AUDIO / "summre-mix" / f"{meeting}.wav", mix / len(audios))
        C.RTTM.mkdir(parents=True, exist_ok=True)
        lines = [f"SPEAKER {meeting} 1 {s:.3f} {e - s:.3f} <NA> <NA> {p} <NA> <NA>"
                 for p, _, toks in channels for s, e in summre.speech_regions(toks)]
        (C.RTTM / f"{meeting}.rttm").write_text("\n".join(sorted(lines, key=lambda l: float(l.split()[3]))) + "\n", encoding="utf-8")
    return segments


def build_noise() -> list[Segment]:
    demand_dir = C.RAW / "demand"
    for env in C.DEMAND_ENVS:
        if not any(p.parent.name == env for p in demand_dir.rglob("ch01.wav")):
            demand_dir.mkdir(parents=True, exist_ok=True)
            zpath = demand_dir / f"{env}_16k.zip"
            urllib.request.urlretrieve(C.DEMAND_URL.format(env=env), zpath)
            zipfile.ZipFile(zpath).extractall(demand_dir)
    bank = load_demand_bank(demand_dir)
    segments: list[Segment] = []
    n = int(C.NOISE_ONLY_SECONDS * C.SAMPLE_RATE)
    for k in range(C.NOISE_ONLY_CLIPS):
        rng = stable_rng(C.SEED, "noise-only", k)
        env = C.DEMAND_ENVS[k % len(C.DEMAND_ENVS)]
        offset = int(rng.integers(0, len(bank[env]) - n))
        wav = C.AUDIO / "noise" / f"noise_{k:02d}_{env}.wav"
        clip = bank[env][offset: offset + n]
        write_wav(wav, 0.1 * clip / max(float(np.sqrt(np.mean(clip ** 2))), 1e-9))
        segments.append(Segment(f"noise-{k:02d}", "noise", "en", rel(wav), 0.0, C.NOISE_ONLY_SECONDS,
                                "", f"noise-{env}", "test", pair_key=f"noise-{k:02d}"))
    return segments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agm-dir", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(C.ROOT / ".env")
    token = os.getenv("HF_TOKEN")
    manifests = {"agm": build_agm(args.agm_dir), **build_ami(token),
                 "summre": build_summre(token), "noise": build_noise()}
    for name, segments in manifests.items():
        write_manifest(C.MANIFESTS / f"{name}.jsonl", segments)
        hours = sum(s.duration for s in segments) / 3600
        test = sum(s.split == "test" for s in segments)
        print(f"{name:8} segments={len(segments):5} test={test:5} hours={hours:5.2f}")


if __name__ == "__main__":
    main()
