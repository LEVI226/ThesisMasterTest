"""H5 on AGM (de/en/fr): dev window [0,180 s) chooses the chunk, test window [180 s, end) reports it."""
from __future__ import annotations

import csv
import subprocess

from backend.evaluation.statistics import latency_summary
from study_real_meetings import config as C
from study_real_meetings.audio import load_segment, wav_duration
from study_real_meetings.manifest import read_manifest
from study_real_meetings.runner import collect_provenance
from study_real_meetings.streaming import choose_operating_point, chunk_latencies, stream_chunks
from study_real_meetings.text import score_words
from study_real_meetings.transcribers import make_transcriber, release


def main() -> None:
    frozen = subprocess.run(["git", "tag", "-l", "protocol-frozen"], capture_output=True, text=True,
                            cwd=C.ROOT).stdout.strip()
    if not frozen:
        raise SystemExit("Protocol not frozen (git tag 'protocol-frozen' missing): H5 test windows are test-split results (Task 9).")
    segs = read_manifest(C.MANIFESTS / "agm.jsonl")
    prov = collect_provenance()
    out = C.RESULTS / "streaming.csv"
    fields = ["system", "language", "split", "chunk_s", "n_ref", "errors", "wer", "lat_n", "lat_median",
              "lat_p95", "realtime_ok_share", "operating_point", "git_commit", "gpu"]
    rows = []
    for system in ("whisper-small", "whisper-large-v3"):
        t = make_transcriber(system)
        for lang in C.AGM_LANGUAGES:
            wav = C.AUDIO / "agm" / f"agm_{lang}.wav"
            boundary = min(s.start for s in segs if s.language == lang and s.split == "test")
            windows = {"dev": (0.0, boundary), "test": (boundary, wav_duration(wav))}
            refs = {sp: " ".join(s.reference for s in segs if s.language == lang and s.split == sp) for sp in windows}
            dev_wer, per_split = {}, {}
            for split, (a, b) in windows.items():
                audio = load_segment(wav, a, b)
                for chunk in C.STREAM_CHUNKS_S:
                    res = stream_chunks(audio, t, chunk_s=chunk, language=lang)
                    counts = score_words(refs[split], " ".join(r.text for r in res), lang)
                    lat = latency_summary(chunk_latencies(res))
                    ok = sum(r.proc_s <= (r.end - r.start) for r in res) / len(res)
                    per_split[(split, chunk)] = (counts, lat, ok)
                    if split == "dev":
                        dev_wer[chunk] = counts.wer
            point = choose_operating_point(dev_wer, C.STREAM_TOLERANCE_WER)
            for (split, chunk), (counts, lat, ok) in per_split.items():
                rows.append({"system": system, "language": lang, "split": split, "chunk_s": chunk,
                             "n_ref": counts.n_ref, "errors": counts.errors, "wer": f"{counts.wer:.4f}",
                             "lat_n": lat["n"], "lat_median": f"{lat['median']:.3f}", "lat_p95": f"{lat['p95']:.3f}",
                             "realtime_ok_share": f"{ok:.3f}", "operating_point": int(chunk == point),
                             "git_commit": prov["git_commit"], "gpu": prov["gpu"]})
            print(system, lang, "operating point:", point)
        release(t)
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
