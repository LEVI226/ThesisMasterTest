"""Scoring helpers for the real-meetings study.

Word and character alignment reuse the audited thesis scorer
(backend.evaluation.metrics) so that "WER" means the same thing in every chapter.
Two documented additions: filler-word removal (both sides) and an optional
digits-to-words rule (both sides), reported with and without.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from num2words import num2words

from backend.evaluation.metrics import _levenshtein, normalize_text
from study_real_meetings.config import FILLERS, NESTLE_TERMS

_DIGITS = re.compile(r"^\d+$")


@dataclass(frozen=True)
class Counts:
    sub: int
    dele: int
    ins: int
    n_ref: int

    @property
    def errors(self) -> int:
        return self.sub + self.dele + self.ins

    @property
    def wer(self) -> float:
        return self.errors / self.n_ref if self.n_ref else float("nan")


def normalize_tokens(text: str, language: str, *, numbers_to_words: bool = False) -> list[str]:
    fillers = FILLERS.get(language, frozenset())
    out: list[str] = []
    for token in normalize_text(text).split():
        if token in fillers:
            continue
        if numbers_to_words and _DIGITS.match(token):
            out.extend(normalize_text(num2words(int(token), lang=language)).split())
        else:
            out.append(token)
    return out


def _counts(ref: list, hyp: list) -> Counts:
    if not ref:
        return Counts(0, 0, len(hyp), 0)
    s, d, i, n = _levenshtein(ref, hyp)
    return Counts(s, d, i, n)


def score_words(reference: str, hypothesis: str, language: str, *, numbers_to_words: bool = False) -> Counts:
    return _counts(
        normalize_tokens(reference, language, numbers_to_words=numbers_to_words),
        normalize_tokens(hypothesis, language, numbers_to_words=numbers_to_words),
    )


def score_chars(reference: str, hypothesis: str, language: str) -> Counts:
    ref = list("".join(normalize_tokens(reference, language)))
    hyp = list("".join(normalize_tokens(hypothesis, language)))
    return _counts(ref, hyp)


def term_hits(reference: str, hypothesis: str, language: str, terms=NESTLE_TERMS) -> tuple[int, int]:
    ref = Counter(normalize_tokens(reference, language))
    hyp = Counter(normalize_tokens(hypothesis, language))
    total = sum(ref[t] for t in terms)
    hits = sum(min(ref[t], hyp[t]) for t in terms)
    return hits, total


def has_repetition_loop(hypothesis: str, language: str, n: int = 4, min_repeats: int = 3) -> bool:
    tokens = normalize_tokens(hypothesis, language)
    grams = Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
    return any(count >= min_repeats for count in grams.values())
