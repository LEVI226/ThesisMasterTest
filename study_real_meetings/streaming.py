"""H5: fixed-chunk streaming. Each chunk is transcribed once it has fully arrived;
word latency ~ chunk length (buffering) + compute time for that chunk."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from study_real_meetings.config import SAMPLE_RATE

_MIN_TAIL_S = 0.1


@dataclass(frozen=True)
class ChunkResult:
    index: int
    start: float
    end: float
    text: str
    proc_s: float


def stream_chunks(audio: np.ndarray, transcriber, *, chunk_s: float, language: str) -> list[ChunkResult]:
    step = int(round(chunk_s * SAMPLE_RATE))
    results: list[ChunkResult] = []
    for index, offset in enumerate(range(0, len(audio), step)):
        chunk = audio[offset : offset + step]
        if len(chunk) < _MIN_TAIL_S * SAMPLE_RATE:
            break
        out = transcriber.transcribe(chunk, language=language, prompt=None)
        results.append(ChunkResult(index, offset / SAMPLE_RATE, (offset + len(chunk)) / SAMPLE_RATE,
                                   out.text, out.seconds))
    return results


def chunk_latencies(results: list[ChunkResult]) -> list[float]:
    return [(r.end - r.start) + r.proc_s for r in results]


def choose_operating_point(dev_wer: dict[float, float], tolerance: float) -> float:
    reference = dev_wer[max(dev_wer)]
    return min(c for c, w in dev_wer.items() if w <= reference + tolerance)
