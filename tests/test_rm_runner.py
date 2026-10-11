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

from study_real_meetings.audio import write_wav
from study_real_meetings.manifest import Segment
from study_real_meetings.runner import FIELDS, Condition, read_rows, run
from study_real_meetings.transcribers import Transcript


class FakeTranscriber:
    system, model_id, compute_type = "fake", "fake-1", "none"

    def __init__(self, text="the meeting start at nine today"):
        self.text, self.calls = text, []

    def transcribe(self, audio, *, language, prompt):
        self.calls.append((len(audio), language, prompt))
        return Transcript(self.text, language or "en", 0.5)


def _setup(tmp_path):
    write_wav(tmp_path / "audio" / "a.wav", 0.1 * np.sin(np.arange(48_000) / 5).astype(np.float32))
    seg = Segment("s1", "agm", "en", "audio/a.wav", 0.5, 2.5, "the meeting starts at nine", "c1", "test")
    bank = {"OMEETING": np.random.default_rng(0).standard_normal(64_000).astype(np.float32)}
    return seg, bank


PROV = {"git_commit": "abc", "packages": "{}", "gpu": "none"}


def test_condition_names_are_unique_and_readable():
    assert Condition().name == "forced-clean"
    assert Condition(forced_language=False, snr_db=5.0).name == "auto-snr5"
    assert Condition(snr_db=10.0, denoise=True).name == "forced-snr10-denoise"
    assert Condition(prompt=True).name == "forced-clean-prompt"


def test_run_writes_scored_row_and_resumes(tmp_path):
    seg, bank = _setup(tmp_path)
    out = tmp_path / "runs.csv"
    fake = FakeTranscriber()
    n = run([seg], fake, Condition(snr_db=10.0), hypothesis_id="H2", out_csv=out,
            bank=bank, provenance=PROV, data_root=tmp_path)
    assert n == 1 and fake.calls == [(32_000, "en", None)]
    row = read_rows(out)[0]
    assert list(row) == FIELDS
    assert (row["sub"], row["del"], row["ins"], row["n_ref"]) == ("1", "0", "1", "5")
    assert row["condition"] == "forced-snr10" and row["noise_type"] == "OMEETING"
    assert row["git_commit"] == "abc" and row["split"] == "test"
    again = run([seg], fake, Condition(snr_db=10.0), hypothesis_id="H2", out_csv=out,
                bank=bank, provenance=PROV, data_root=tmp_path)
    assert again == 0 and len(read_rows(out)) == 1


def test_auto_condition_passes_no_language_and_prompt_is_injected(tmp_path):
    seg, bank = _setup(tmp_path)
    fake = FakeTranscriber()
    run([seg], fake, Condition(forced_language=False, prompt=True), hypothesis_id="H4", out_csv=tmp_path / "r.csv",
        bank=bank, provenance=PROV, data_root=tmp_path)
    _, language, prompt = fake.calls[0]
    assert language is None and prompt.startswith("Nestlé")
