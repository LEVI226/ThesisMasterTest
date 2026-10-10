"""D1: DER of pyannote on SUMM-RE meeting mixes against gold speaker turns."""
from __future__ import annotations

from pathlib import Path

from pyannote.core import Annotation, Segment as Turn
from pyannote.metrics.diarization import DiarizationErrorRate


def read_rttm(path: Path) -> Annotation:
    annotation = Annotation()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0] == "SPEAKER":
            start, duration = float(parts[3]), float(parts[4])
            annotation[Turn(start, start + duration)] = parts[7]
    return annotation


def der(reference: Annotation, hypothesis: Annotation, collar: float = 0.25) -> float:
    return float(DiarizationErrorRate(collar=collar, skip_overlap=False)(reference, hypothesis))
