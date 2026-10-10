"""Transcribe all audio in audioReunionréel/ and save one .txt per file."""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from stt.engine import TranscribeConfig, transcribe_file  # noqa: E402

AUDIO_DIR = next(p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith("audio"))
OUT_DIR = AUDIO_DIR / "transcripts"
EXTS = {".m4a", ".mp3", ".mp4", ".wav", ".flac", ".ogg"}
LOG_PATH = OUT_DIR / "_progress.jsonl"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    files = sorted(
        (f for f in AUDIO_DIR.iterdir() if f.suffix.lower() in EXTS),
        key=lambda p: p.stat().st_size,
    )
    config = TranscribeConfig(
        model_size="small",
        preprocessing=True,
        domain_prompt=True,
        vad=False,
    )

    for i, path in enumerate(files, 1):
        out_txt = OUT_DIR / f"{path.stem}.txt"
        out_json = OUT_DIR / f"{path.stem}.json"
        if out_txt.exists() and out_txt.stat().st_size > 0:
            print(f"[{i}/{len(files)}] SKIP (exists): {path.name}", flush=True)
            continue

        print(f"[{i}/{len(files)}] START: {path.name}", flush=True)
        t0 = time.time()
        try:
            result = transcribe_file(str(path), config=config)
            out_txt.write_text(result["text"], encoding="utf-8")
            out_json.write_text(
                json.dumps(
                    {
                        "file": path.name,
                        "language": result["language"],
                        "duration_s": result["duration"],
                        "processing_time_s": result["processing_time"],
                        "model": result["model"],
                        "segments_count": len(result["segments"]),
                        "transcribed_at": datetime.now().isoformat(),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            elapsed = time.time() - t0
            print(
                f"[{i}/{len(files)}] DONE: {path.name} "
                f"({result['duration']/60:.1f} min audio, {elapsed/60:.1f} min wall)",
                flush=True,
            )
            with LOG_PATH.open("a", encoding="utf-8") as log:
                log.write(
                    json.dumps(
                        {"file": path.name, "status": "ok", "elapsed_s": elapsed},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception as exc:
            print(f"[{i}/{len(files)}] ERROR: {path.name}: {exc}", flush=True)
            with LOG_PATH.open("a", encoding="utf-8") as log:
                log.write(
                    json.dumps(
                        {"file": path.name, "status": "error", "error": str(exc)},
                        ensure_ascii=False,
                    )
                    + "\n"
                )


if __name__ == "__main__":
    main()
