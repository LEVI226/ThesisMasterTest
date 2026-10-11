"""Segment manifests: one JSON object per line, UTF-8."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from study_real_meetings.config import (
    DEV_SECONDS,
    SEGMENT_MAX_GAP_S,
    SEGMENT_MAX_S,
    SEGMENT_TARGET_S,
)


@dataclass(frozen=True)
class Unit:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Segment:
    segment_id: str
    dataset: str        # agm | ami-ihm | ami-sdm | summre | noise
    language: str       # en | fr | de
    audio_path: str     # 16 kHz mono wav, relative to config.DATA, forward slashes
    start: float
    end: float
    reference: str
    cluster: str        # resampling unit for the bootstrap
    split: str          # dev | test
    speaker: str = ""
    pair_key: str = ""  # pairs AMI IHM and SDM copies of the same utterance

    @property
    def duration(self) -> float:
        return self.end - self.start


def merge_units(
    units: list[Unit],
    *,
    target_s: float = SEGMENT_TARGET_S,
    max_s: float = SEGMENT_MAX_S,
    max_gap_s: float = SEGMENT_MAX_GAP_S,
) -> list[list[Unit]]:
    groups: list[list[Unit]] = []
    current: list[Unit] = []
    for unit in sorted(units, key=lambda u: u.start):
        if not unit.text.strip():
            continue
        if current:
            too_long = unit.end - current[0].start > max_s
            too_far = unit.start - current[-1].end > max_gap_s
            full = current[-1].end - current[0].start >= target_s
            if too_long or too_far or full:
                groups.append(current)
                current = []
        current.append(unit)
    if current:
        groups.append(current)
    return groups


def split_for(start_s: float, dev_seconds: float = DEV_SECONDS) -> str:
    return "dev" if start_s < dev_seconds else "test"


def write_manifest(path: Path, segments: list[Segment]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for segment in segments:
            handle.write(json.dumps(asdict(segment), ensure_ascii=False) + "\n")


def read_manifest(path: Path) -> list[Segment]:
    with open(path, encoding="utf-8") as handle:
        return [Segment(**json.loads(line)) for line in handle if line.strip()]
