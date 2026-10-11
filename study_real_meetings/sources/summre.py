"""SUMM-RE ASRU (French meetings, one channel per participant, gold word alignment)."""
from __future__ import annotations

import csv
import io

from study_real_meetings.config import IPU_MAX_GAP_S, SEGMENT_PAD_S
from study_real_meetings.manifest import Segment, Unit, merge_units, split_for

_TIER = "TokensAlign"


def _is_word(label: str) -> bool:
    label = label.strip()
    return bool(label) and label != "#" and "@" not in label and "*" not in label and label.lower() != "xxx"


def parse_tokens(csv_text: str) -> list[Unit]:
    rows = csv.reader(io.StringIO(csv_text.lstrip("﻿")))
    return [Unit(float(r[1]), float(r[2]), r[3].strip())
            for r in rows if len(r) >= 4 and r[0] == _TIER and _is_word(r[3])]


def ipus(tokens: list[Unit], max_gap_s: float = IPU_MAX_GAP_S) -> list[Unit]:
    out: list[Unit] = []
    for tok in sorted(tokens, key=lambda t: t.start):
        if out and tok.start - out[-1].end <= max_gap_s:
            last = out[-1]
            out[-1] = Unit(last.start, tok.end, f"{last.text} {tok.text}")
        else:
            out.append(tok)
    return out


def build_summre_segments(meeting: str, participant: str, tokens: list[Unit], audio_rel: str) -> list[Segment]:
    segments: list[Segment] = []
    for k, group in enumerate(merge_units(ipus(tokens))):
        start = max(group[0].start - SEGMENT_PAD_S, 0.0)
        end = group[-1].end + SEGMENT_PAD_S
        segment_id = f"summre-{meeting}-{participant}-{k:04d}"
        segments.append(Segment(
            segment_id=segment_id, dataset="summre", language="fr", audio_path=audio_rel,
            start=round(start, 3), end=round(end, 3),
            reference=" ".join(u.text for u in group),
            cluster=f"summre-{meeting}-{participant}", split=split_for(group[0].start),
            speaker=participant, pair_key=segment_id,
        ))
    return segments


def tokens_in_span(tokens: list[Unit], start: float, end: float) -> str:
    return " ".join(t.text for t in tokens if t.start >= start and t.end <= end)


def speech_regions(tokens: list[Unit], max_gap_s: float = 0.3) -> list[tuple[float, float]]:
    return [(u.start, u.end) for u in ipus(tokens, max_gap_s=max_gap_s)]
