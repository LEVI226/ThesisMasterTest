import numpy as np
import pytest

from study_real_meetings.streaming import ChunkResult, choose_operating_point, chunk_latencies, stream_chunks
from study_real_meetings.transcribers import Transcript


class Echo:
    def __init__(self):
        self.lengths = []

    def transcribe(self, audio, *, language, prompt):
        self.lengths.append(len(audio))
        return Transcript(f"w{len(self.lengths)}", language, 0.25)


def test_chunks_cover_audio_without_overlap_and_skip_tiny_tail():
    audio = np.zeros(16_000 * 4 + 800, dtype=np.float32)  # 4.05 s
    echo = Echo()
    out = stream_chunks(audio, echo, chunk_s=2.0, language="fr")
    assert echo.lengths == [32_000, 32_000]  # the 0.05 s tail (< 0.1 s) is dropped
    assert [(r.start, r.end) for r in out] == [(0.0, 2.0), (2.0, 4.0)]
    assert " ".join(r.text for r in out) == "w1 w2"


def test_short_final_chunk_is_kept():
    echo = Echo()
    out = stream_chunks(np.zeros(16_000 * 5, dtype=np.float32), echo, chunk_s=2.0, language="fr")
    assert echo.lengths == [32_000, 32_000, 16_000] and out[-1].end == 5.0


def test_latency_is_buffer_plus_compute():
    rs = [ChunkResult(0, 0.0, 2.0, "a", 0.25), ChunkResult(1, 2.0, 3.0, "b", 0.5)]
    assert chunk_latencies(rs) == pytest.approx([2.25, 1.5])


def test_operating_point_is_smallest_chunk_within_tolerance_of_20s():
    dev = {1.0: 0.30, 2.0: 0.22, 5.0: 0.205, 10.0: 0.20, 20.0: 0.20}
    assert choose_operating_point(dev, tolerance=0.01) == 5.0
