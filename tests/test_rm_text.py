import pytest

from backend.evaluation.metrics import wer as thesis_wer
from study_real_meetings.text import (
    Counts,
    has_repetition_loop,
    normalize_tokens,
    score_chars,
    score_words,
    term_hits,
)


def test_worked_example_from_the_learning_notes():
    # "the meeting starts at nine" vs "the meeting start at nine today": 1 S + 1 I over 5 words.
    c = score_words("the meeting starts at nine", "the meeting start at nine today", "en")
    assert (c.sub, c.dele, c.ins, c.n_ref) == (1, 0, 1, 5)
    assert c.wer == pytest.approx(0.4)


def test_matches_thesis_scorer_when_no_fillers_or_numbers():
    ref = "Nous lançons, aujourd'hui, la nouvelle stratégie."
    hyp = "nous lançons aujourdhui la nouvelle stratégies"
    assert score_words(ref, hyp, "fr").wer == pytest.approx(thesis_wer(ref, hyp))


def test_fillers_are_removed_on_both_sides():
    assert score_words("um so we start", "so we start", "en").errors == 0
    assert score_words("euh on commence", "on commence", "fr").errors == 0


def test_number_rule_is_optional_and_symmetric():
    ref, hyp = "founded 160 years ago", "founded one hundred and sixty years ago"
    assert score_words(ref, hyp, "en").errors > 0
    assert score_words(ref, hyp, "en", numbers_to_words=True).errors == 0
    assert normalize_tokens("160", "fr", numbers_to_words=True) == ["cent", "soixante"]


def test_char_counts_ignore_spaces_like_the_thesis():
    c = score_chars("ab cd", "abcd", "en")
    assert c.errors == 0 and c.n_ref == 4


def test_empty_reference_counts_insertions():
    c = score_words("", "thank you", "en")
    assert (c.n_ref, c.ins) == (0, 2)
    assert c.wer != c.wer  # NaN: WER undefined without reference words


def test_term_hits_need_exact_normalised_match():
    hits, total = term_hits("Nestlé and KitKat and Nestlé", "nestle and kitkat and nestlé", "en")
    assert (hits, total) == (2, 3)


def test_repetition_loop_detection():
    loop = "nescafé purina kitkat " * 4
    assert has_repetition_loop(loop, "fr")
    assert not has_repetition_loop("the board approved the plan for next year", "en")


def test_counts_dataclass_errors():
    assert Counts(1, 2, 3, 10).errors == 6
