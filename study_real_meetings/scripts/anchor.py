"""External sanity anchor (plan Task 13 Step 3): published ASRU whisper vs our large-v3 on SUMM-RE test.

Post-freeze, presentation only (PROTOCOL §9, 2026-10-11). Applies R16 (segments whose normalised
reference is empty are excluded) to both rows, consistently.
"""
from __future__ import annotations

import csv
import json

from study_real_meetings import config as C
from study_real_meetings.analysis import L3, Selector, _errors, _int
from study_real_meetings.manifest import Unit, read_manifest
from study_real_meetings.runner import read_rows
from study_real_meetings.sources.summre import tokens_in_span
from study_real_meetings.text import score_words


def published_asru_wer() -> tuple[float, int, int]:
    segs = [s for s in read_manifest(C.MANIFESTS / "summre.jsonl") if s.split == "test"]
    errors = n_ref = n_seg = 0
    for s in segs:
        rec = s.audio_path.split("/")[-1][:-4]
        ext = [Unit(*t) for t in json.loads(
            (C.RAW / "summre" / "tokens" / f"{rec}.json").read_text(encoding="utf-8"))["external_whisper"]]
        c = score_words(s.reference, tokens_in_span(ext, s.start, s.end), "fr")
        if c.n_ref == 0:  # R16
            continue
        errors, n_ref, n_seg = errors + c.errors, n_ref + c.n_ref, n_seg + 1
    return errors / n_ref, n_ref, n_seg


def main() -> None:
    wer_ext, n_ext, seg_ext = published_asru_wer()
    ours = Selector(L3, "forced-clean", ("summre",)).pick(read_rows(C.RESULTS / "runs.csv"))
    wer_ours, n_ours = sum(_errors(r) for r in ours) / sum(_int(r, "n_ref") for r in ours), sum(_int(r, "n_ref") for r in ours)
    rows = [{"system": f"asru-published-whisper ({C.SUMMRE_EXTERNAL_WHISPER})", "wer": f"{wer_ext:.4f}",
             "n_ref_words": n_ext, "n_segments": seg_ext},
            {"system": "whisper-large-v3 forced-clean (ours)", "wer": f"{wer_ours:.4f}",
             "n_ref_words": n_ours, "n_segments": len(ours)}]
    with open(C.RESULTS / "anchor.csv", "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["system", "wer", "n_ref_words", "n_segments"])
        w.writeheader()
        w.writerows(rows)
    print(rows, f"ratio={wer_ours / wer_ext:.3f}")


if __name__ == "__main__":
    main()
