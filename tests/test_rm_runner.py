import numpy as np
import pytest
import soundfile as sf
from pathlib import Path

SAMPLE = Path(__file__).parent / "sample.wav"


@pytest.mark.gpu
@pytest.mark.parametrize("system", ["whisper-small", "mms-1b-all", "conformer-ctc-large",
                                    "hf-whisper-small", "hf-whisper-small-lora"])
def test_every_system_transcribes_the_sample(system):
    from study_real_meetings.transcribers import make_transcriber, release
    audio, sr = sf.read(str(SAMPLE), dtype="float32")
    assert sr == 16_000
    t = make_transcriber(system)
    out = t.transcribe(audio, language="en", prompt=None)
    assert isinstance(out.text, str) and out.seconds > 0
    release(t)
