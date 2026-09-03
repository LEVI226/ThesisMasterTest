"""
STT evaluation metrics: WER, CER, RTF.
Pure Python implementation using dynamic programming (Levenshtein distance).
No external NLP libraries required.
"""
import math
import re
import string

DEFAULT_PUNCTUATION = string.punctuation + "‘’“”—–"


def normalize_text(text: str, lowercase: bool = True, remove_punctuation: bool = True) -> str:
    """
    Normalize text for fair WER/CER comparison.
    - Lowercases
    - Removes punctuation
    - Collapses whitespace
    """
    if lowercase:
        text = text.lower()
    if remove_punctuation:
        text = text.translate(str.maketrans("", "", DEFAULT_PUNCTUATION))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _levenshtein(seq_ref: list, seq_hyp: list) -> tuple[int, int, int, int]:
    """
    Compute Levenshtein edit distance between two sequences.
    Returns (substitutions, deletions, insertions, reference_length).
    Uses Wagner-Fischer DP algorithm.
    """
    n, m = len(seq_ref), len(seq_hyp)
    # dp[i][j] = (edit_ops, s, d, i_count) — but we only need total edit cost
    # Use standard DP for edit distance with backtracking for S/D/I counts

    # Build cost matrix
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq_ref[i - 1] == seq_hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1],  # substitution
                )

    # Backtrack to count S/D/I
    i, j = n, m
    subs = dels = ins = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and seq_ref[i - 1] == seq_hyp[j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            subs += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            dels += 1
            i -= 1
        else:
            ins += 1
            j -= 1

    return subs, dels, ins, n


def wer(reference: str, hypothesis: str, normalize: bool = True) -> float:
    """
    Word Error Rate = (S + D + I) / N
    where N = number of words in reference.
    Returns value in [0, inf) — 0 is perfect, >1 possible when hypothesis is much longer.
    """
    if normalize:
        reference  = normalize_text(reference)
        hypothesis = normalize_text(hypothesis)
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    s, d, i, n = _levenshtein(ref_words, hyp_words)
    return (s + d + i) / n


def cer(reference: str, hypothesis: str, normalize: bool = True) -> float:
    """
    Character Error Rate = (S + D + I) / N at character level.
    Spaces are removed before comparison (standard convention).
    """
    if normalize:
        reference  = normalize_text(reference)
        hypothesis = normalize_text(hypothesis)
    ref_chars = list(reference.replace(" ", ""))
    hyp_chars = list(hypothesis.replace(" ", ""))
    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0
    s, d, i, n = _levenshtein(ref_chars, hyp_chars)
    return (s + d + i) / n


def rtf(audio_duration_seconds: float, processing_time_seconds: float) -> float:
    """
    Real-Time Factor = processing_time / audio_duration.
    RTF < 1 means faster than real-time (good for production).
    """
    if audio_duration_seconds <= 0:
        return float("inf")
    return processing_time_seconds / audio_duration_seconds


def summarize_metrics(results: list[dict]) -> dict:
    """
    Compute mean WER, CER, RTF across a list of result dicts.
    Each dict must have keys: wer, cer, real_time_factor.
    """
    if not results:
        return {}
    summary = {}
    for key in ("wer", "cer", "real_time_factor"):
        values = []
        for row in results:
            try:
                value = float(row[key])
            except (KeyError, TypeError, ValueError):
                continue
            if math.isfinite(value):
                values.append(value)
        summary[f"mean_{key}"] = (
            round(sum(values) / len(values), 4) if values else None
        )
    return summary
