"""AMI Meeting Corpus (HF edinburghcstr/ami, parquet): one wav per official utterance."""
from __future__ import annotations

from study_real_meetings.manifest import Segment, split_for


def select_rows(rows: list[dict], meetings, min_s: float, max_s: float) -> list[dict]:
    keep = set(meetings)
    return [r for r in rows
            if r["meeting_id"] in keep and min_s <= r["end_time"] - r["begin_time"] <= max_s]


def pair_key(row: dict) -> str:
    return f"{row['meeting_id']}-{row['speaker_id']}-{int(round(row['begin_time'] * 100)):07d}"


def segment_for_row(row: dict, mic: str, audio_rel: str) -> Segment:
    key = pair_key(row)
    return Segment(
        segment_id=f"ami-{mic}-{key}", dataset=f"ami-{mic}", language="en",
        audio_path=audio_rel, start=0.0,
        end=round(row["end_time"] - row["begin_time"], 3),
        reference=row["text"],
        cluster=f"ami-{row['meeting_id']}-{row['speaker_id']}",
        split=split_for(row["begin_time"]), speaker=row["speaker_id"], pair_key=key,
    )
