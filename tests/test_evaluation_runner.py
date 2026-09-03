import csv

from backend.evaluation.dataset import EvalSample
from backend.evaluation.report import generate_report
from backend.evaluation.runner import EvalResult, SAMPLE_LANGUAGE, run_evaluation


def _result(sample, *, forced_language, preprocessing, domain_prompt, model_size, vad):
    return EvalResult(
        filename=sample.audio_filename,
        language=sample.language,
        noise_condition=sample.noise_condition,
        speaker_count=sample.speaker_count,
        model=model_size or "tiny",
        preprocessing_enabled=preprocessing,
        domain_prompt_enabled=domain_prompt,
        forced_language=forced_language,
        duration_audio_seconds=1.0,
        processing_time_seconds=0.1,
        real_time_factor=0.1,
        wer=0.0,
        cer=0.0,
        reference_text="bonjour",
        hypothesis_text="bonjour",
        vad_enabled=vad,
    )


def test_default_matrix_forces_each_samples_own_language(monkeypatch, tmp_path):
    calls = []

    def fake_run_single(sample, **kwargs):
        calls.append((sample.language, kwargs.copy()))
        return _result(sample, **kwargs)

    monkeypatch.setattr("backend.evaluation.runner.run_single", fake_run_single)
    samples = [
        EvalSample("en.wav", "en.txt", "en", "clean", 1),
        EvalSample("fr.wav", "fr.txt", "fr", "clean", 1),
        EvalSample("de.wav", "de.txt", "de", "clean", 1),
    ]

    run_evaluation(samples, str(tmp_path / "results.csv"), model_size="tiny")

    assert len(calls) == 12
    for index, expected_language in enumerate(("en", "fr", "de")):
        sample_calls = calls[index * 4 : (index + 1) * 4]
        assert [call[1]["forced_language"] for call in sample_calls] == [
            None,
            None,
            None,
            expected_language,
        ]


def test_custom_condition_forwards_vad_and_keeps_transcripts_in_csv(
    monkeypatch, tmp_path
):
    calls = []

    def fake_run_single(sample, **kwargs):
        calls.append(kwargs.copy())
        return _result(sample, **kwargs)

    monkeypatch.setattr("backend.evaluation.runner.run_single", fake_run_single)
    sample = EvalSample("fr.wav", "fr.txt", "fr", "noisy", 2)
    output = tmp_path / "results.csv"
    conditions = [
        {
            "preprocessing": False,
            "domain_prompt": False,
            "forced_language": SAMPLE_LANGUAGE,
            "vad": True,
        }
    ]

    run_evaluation([sample], str(output), conditions=conditions)

    assert calls[0]["forced_language"] == "fr"
    assert calls[0]["vad"] is True
    with output.open(encoding="utf-8", newline="") as stream:
        row = next(csv.DictReader(stream))
    assert row["reference_text"] == "bonjour"
    assert row["hypothesis_text"] == "bonjour"
    assert row["vad_enabled"] == "True"

    report = generate_report(str(output), str(tmp_path / "report.md"))
    assert "| C1 | tiny | No | No | Yes | fr |" in report
    assert "These aggregates are descriptive" in report
    assert "[improved/degraded]" not in report
