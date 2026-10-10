"""Minimal SRT parser (cue index, time line, one or more text lines)."""
from __future__ import annotations

import re

from study_real_meetings.manifest import Unit

_TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{3})")


def _seconds(stamp: str) -> float:
    h, m, s, ms = map(int, _TIME.match(stamp.strip()).groups())
    return round(h * 3600 + m * 60 + s + ms / 1000, 3)


def parse_srt(text: str) -> list[Unit]:
    units: list[Unit] = []
    for block in re.split(r"\r?\n\s*\r?\n", text.strip().lstrip("﻿")):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing is None:
            continue
        start, end = (part.strip() for part in lines[timing].split("-->"))
        body = " ".join(lines[timing + 1 :])
        units.append(Unit(_seconds(start), _seconds(end), body))
    return units
