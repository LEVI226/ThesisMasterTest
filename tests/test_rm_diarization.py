import pytest
from pyannote.core import Annotation, Segment

from study_real_meetings.diarization import der, read_rttm


def test_read_rttm_and_perfect_der(tmp_path):
    p = tmp_path / "m.rttm"
    p.write_text("SPEAKER m 1 0.000 2.000 <NA> <NA> A <NA> <NA>\n"
                 "SPEAKER m 1 3.000 1.500 <NA> <NA> B <NA> <NA>\n", encoding="utf-8")
    ref = read_rttm(p)
    assert set(ref.labels()) == {"A", "B"}
    hyp = Annotation()
    hyp[Segment(0, 2)] = "spk0"  # labels differ: DER uses optimal mapping
    hyp[Segment(3, 4.5)] = "spk1"
    assert der(ref, hyp, collar=0.0) == pytest.approx(0.0)


def test_missed_speech_counts():
    ref = Annotation()
    ref[Segment(0, 4)] = "A"
    hyp = Annotation()
    hyp[Segment(0, 2)] = "x"
    assert der(ref, hyp, collar=0.0) == pytest.approx(0.5)
