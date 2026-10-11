"""Nestlé AGM 2026: same speech in DE/EN/FR, with captions published by Nestlé."""
from __future__ import annotations

from pathlib import Path

from study_real_meetings.config import AGM_BLOCK_S, AGM_LANGUAGES, SEGMENT_PAD_S
from study_real_meetings.manifest import Segment, merge_units, split_for
from study_real_meetings.srt import parse_srt


def find_agm_files(agm_dir: Path) -> dict[str, tuple[Path, Path]]:
    found: dict[str, tuple[Path, Path]] = {}
    for lang in AGM_LANGUAGES:
        tag = f"({lang.upper()})"
        audio = [p for p in agm_dir.iterdir() if p.suffix.lower() in {".mp3", ".mp4", ".m4a", ".wav"} and tag in p.name]
        srt = [p for p in agm_dir.iterdir() if p.suffix.lower() == ".srt" and tag in p.name]
        if len(audio) != 1 or len(srt) != 1:
            raise FileNotFoundError(f"Expected one audio and one .srt for {tag} in {agm_dir}, got {audio} / {srt}")
        found[lang] = (audio[0], srt[0])
    return found


def build_agm_segments(language: str, srt_text: str, audio_rel: str, audio_duration: float) -> list[Segment]:
    groups = merge_units(parse_srt(srt_text))
    segments: list[Segment] = []
    for k, group in enumerate(groups):
        raw_start, raw_end = group[0].start, group[-1].end
        prev_end = groups[k - 1][-1].end if k > 0 else 0.0
        next_start = groups[k + 1][0].start if k + 1 < len(groups) else audio_duration
        start = max(raw_start - SEGMENT_PAD_S, (prev_end + raw_start) / 2, 0.0)
        end = min(raw_end + SEGMENT_PAD_S, (raw_end + next_start) / 2, audio_duration)
        segment_id = f"agm-{language}-{k:04d}"
        segments.append(Segment(
            segment_id=segment_id, dataset="agm", language=language, audio_path=audio_rel,
            start=round(start, 3), end=round(end, 3),
            reference=" ".join(u.text for u in group),
            cluster=f"agm-{language}-b{int(raw_start // AGM_BLOCK_S):02d}",
            split=split_for(raw_start), pair_key=segment_id,
        ))
    return segments
