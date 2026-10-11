"""(1) Spot-check sheet: 20 random AGM test segments per language (FR, EN), with clips to listen to.
(2) Automatic AGM-DE caption checks: speech rate per segment and coverage vs EN/FR."""
from __future__ import annotations

import csv

from study_real_meetings import config as C
from study_real_meetings.audio import load_segment, wav_duration, write_wav
from study_real_meetings.manifest import read_manifest
from study_real_meetings.noise import stable_rng


def main() -> None:
    segs = [s for s in read_manifest(C.MANIFESTS / "agm.jsonl") if s.split == "test"]
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    sheet = C.RESULTS / "agm_spotcheck.csv"
    if not sheet.exists():  # never overwrite the author's verdicts
        rows = []
        for lang in ("fr", "en"):
            pool = [s for s in segs if s.language == lang]
            picks = stable_rng(C.SEED, "spotcheck", lang).choice(len(pool), size=20, replace=False)
            for i in sorted(picks):
                s = pool[int(i)]
                write_wav(C.SPOTCHECK / f"{s.segment_id}.wav", load_segment(C.DATA / s.audio_path, s.start, s.end))
                rows.append({"segment_id": s.segment_id, "language": lang, "start": s.start, "end": s.end,
                             "reference": s.reference, "verdict": "", "notes": ""})
        with open(sheet, "w", encoding="utf-8", newline="") as h:
            w = csv.DictWriter(h, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    out = C.RESULTS / "agm_de_caption_checks.csv"
    with open(out, "w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["language", "segments", "words", "speech_s", "words_per_s", "coverage", "flagged_segments"])
        for lang in C.AGM_LANGUAGES:
            ls = [s for s in segs if s.language == lang]
            words = sum(len(s.reference.split()) for s in ls)
            speech = sum(s.duration for s in ls)
            flagged = sum(1 for s in ls if not 0.5 <= len(s.reference.split()) / s.duration <= 4.5)
            total = wav_duration(C.AUDIO / "agm" / f"agm_{lang}.wav") - C.DEV_SECONDS
            w.writerow([lang, len(ls), words, f"{speech:.1f}", f"{words / speech:.2f}", f"{speech / total:.3f}", flagged])
    print(f"Spot-check sheet: {sheet}\nClips: {C.SPOTCHECK}\nDE checks: {out}")


if __name__ == "__main__":
    main()
