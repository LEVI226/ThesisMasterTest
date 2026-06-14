"""
Unit tests for the STT evaluation module.
Does NOT require downloading Whisper or running actual transcription.
"""
import csv
import math
import tempfile
from pathlib import Path

import pytest

from backend.evaluation.metrics import normalize_text, wer, cer, rtf, summarize_metrics
from backend.evaluation.dataset import load_metadata, EvalSample, validate_samples


# ── normalize_text ───────────────────────────────────────────────────────────

class TestNormalizeText:
    def test_lowercase(self):
        assert normalize_text("Hello World") == "hello world"

    def test_removes_punctuation(self):
        assert normalize_text("Hello, world!") == "hello world"

    def test_collapses_whitespace(self):
        assert normalize_text("  hello   world  ") == "hello world"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_only_punctuation(self):
        assert normalize_text("!!!") == ""

    def test_unicode_punctuation(self):
        result = normalize_text("it's a test")
        assert "'" not in result


# ── WER ──────────────────────────────────────────────────────────────────────

class TestWER:
    def test_perfect_match(self):
        assert wer("hello world", "hello world") == 0.0

    def test_one_substitution(self):
        # "hello world" vs "hello earth" → 1 sub / 2 words = 0.5
        assert wer("hello world", "hello earth") == pytest.approx(0.5)

    def test_one_deletion(self):
        # ref: "hello world" (2), hyp: "hello" (1) → 1 deletion / 2 = 0.5
        assert wer("hello world", "hello") == pytest.approx(0.5)

    def test_one_insertion(self):
        # ref: "hello" (1), hyp: "hello world" → 1 insertion / 1 = 1.0
        assert wer("hello", "hello world") == pytest.approx(1.0)

    def test_completely_wrong(self):
        assert wer("one two three", "four five six") == pytest.approx(1.0)

    def test_empty_reference_empty_hypothesis(self):
        assert wer("", "") == 0.0

    def test_empty_reference_non_empty_hypothesis(self):
        assert wer("", "some words") == 1.0

    def test_normalization_applied(self):
        # Punctuation should be stripped before comparison
        assert wer("Hello, world!", "hello world") == 0.0

    def test_wer_is_float(self):
        result = wer("hello world", "hello earth")
        assert isinstance(result, float)


# ── CER ──────────────────────────────────────────────────────────────────────

class TestCER:
    def test_perfect_match(self):
        assert cer("hello", "hello") == 0.0

    def test_one_char_substitution(self):
        # "hello" vs "helo" → 1 deletion / 5 chars = 0.2
        assert cer("hello", "helo") == pytest.approx(0.2)

    def test_empty_both(self):
        assert cer("", "") == 0.0

    def test_spaces_ignored(self):
        # Spaces are removed before CER comparison
        r = cer("hello world", "hello world")
        assert r == 0.0

    def test_cer_less_than_or_equal_wer_on_single_word_error(self):
        # CER should generally be <= WER for word-level errors
        w = wer("nestle nespresso", "nestle nescafe")
        c = cer("nestle nespresso", "nestle nescafe")
        # Not always true but for this case: WER=0.5, CER should be smaller
        assert c <= w + 0.01  # small tolerance


# ── RTF ──────────────────────────────────────────────────────────────────────

class TestRTF:
    def test_faster_than_realtime(self):
        # 10s audio processed in 2s → RTF = 0.2 (good)
        assert rtf(10.0, 2.0) == pytest.approx(0.2)

    def test_realtime(self):
        assert rtf(10.0, 10.0) == pytest.approx(1.0)

    def test_zero_audio_duration(self):
        assert rtf(0.0, 1.0) == float("inf")

    def test_rtf_returns_float(self):
        assert isinstance(rtf(5.0, 1.0), float)


# ── summarize_metrics ────────────────────────────────────────────────────────

class TestSummarizeMetrics:
    def test_basic_average(self):
        results = [
            {"wer": 0.2, "cer": 0.1, "real_time_factor": 0.3},
            {"wer": 0.4, "cer": 0.2, "real_time_factor": 0.5},
        ]
        summary = summarize_metrics(results)
        assert summary["mean_wer"] == pytest.approx(0.3)
        assert summary["mean_cer"] == pytest.approx(0.15)
        assert summary["mean_real_time_factor"] == pytest.approx(0.4)

    def test_empty_list(self):
        assert summarize_metrics([]) == {}


# ── load_metadata ────────────────────────────────────────────────────────────

class TestLoadMetadata:
    def _make_csv(self, tmp_path: Path, rows: list[dict]) -> Path:
        csv_file = tmp_path / "metadata.csv"
        if rows:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        else:
            csv_file.write_text("audio_filename,reference_filename,language,noise_condition,speaker_count,notes\n")
        return csv_file

    def test_loads_valid_csv(self, tmp_path):
        csv_file = self._make_csv(tmp_path, [
            {
                "audio_filename": "test.wav",
                "reference_filename": "test.txt",
                "language": "en",
                "noise_condition": "clean",
                "speaker_count": "1",
                "notes": "test",
            }
        ])
        samples = load_metadata(str(csv_file))
        assert len(samples) == 1
        assert samples[0].audio_filename == "test.wav"
        assert samples[0].language == "en"
        assert samples[0].speaker_count == 1

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_metadata(str(tmp_path / "nonexistent.csv"))

    def test_missing_column_raises(self, tmp_path):
        csv_file = tmp_path / "metadata.csv"
        csv_file.write_text("audio_filename,language\ntest.wav,en\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing required columns"):
            load_metadata(str(csv_file))

    def test_empty_csv_raises(self, tmp_path):
        csv_file = tmp_path / "metadata.csv"
        csv_file.write_text("", encoding="utf-8")
        with pytest.raises(ValueError):
            load_metadata(str(csv_file))

    def test_resolves_paths(self, tmp_path):
        csv_file = self._make_csv(tmp_path, [
            {
                "audio_filename": "audio.wav",
                "reference_filename": "ref.txt",
                "language": "fr",
                "noise_condition": "noisy",
                "speaker_count": "2",
                "notes": "",
            }
        ])
        samples = load_metadata(str(csv_file))
        assert samples[0].audio_path is not None
        assert samples[0].reference_path is not None

    def test_validate_missing_files(self, tmp_path):
        csv_file = self._make_csv(tmp_path, [
            {
                "audio_filename": "missing.wav",
                "reference_filename": "missing.txt",
                "language": "en",
                "noise_condition": "clean",
                "speaker_count": "1",
                "notes": "",
            }
        ])
        samples = load_metadata(str(csv_file))
        warnings = validate_samples(samples)
        assert len(warnings) == 2  # both audio and reference missing
