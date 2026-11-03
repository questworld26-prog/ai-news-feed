"""
Lexical and Heuristic Evaluation Metrics.
Calculates ROUGE-L F1, fact keyword overlap, hallucination detection, and length metrics.
"""

from __future__ import annotations

import re

from rouge_score import rouge_scorer

_rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)


# [spec: COMPARE-002]
def compute_rouge_l(source_text: str, summary: str) -> float:
    """Compute ROUGE-L F1 between source text and generated summary."""
    if not summary:
        return 0.0
    scores = _rouge.score(source_text, summary)
    return round(scores["rougeL"].fmeasure, 4)


def compute_keyword_overlap(source_text: str, summary: str, expected_facts: list[str]) -> float:
    """Fraction of expected_facts that appear in the summary."""
    if not expected_facts or not summary:
        return 0.0
    summary_lower = summary.lower()
    hits = sum(1 for fact in expected_facts if fact.lower() in summary_lower)
    return round(hits / len(expected_facts), 4)


def detect_hallucinations(source_text: str, summary: str) -> list[str]:
    """Flags capitalized multi-word tokens/numbers not in source text."""
    if not summary:
        return []
    candidate_patterns = [
        r"\b\d+(?:\.\d+)?%\b",
        r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
        r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]+)+\b",
    ]
    source_lower = source_text.lower()
    hallucinations = []
    for pattern in candidate_patterns:
        for match in re.finditer(pattern, summary):
            token = match.group()
            if token.lower() not in source_lower:
                hallucinations.append(token)
    return list(set(hallucinations))


def compute_length_metrics(summary: str) -> dict[str, int]:
    """Return word count and sentence count for the text."""
    words = len(summary.split()) if summary else 0
    sentences = len([s for s in re.split(r"[.!?]+", summary) if s.strip()]) if summary else 0
    return {"word_count": words, "sentence_count": sentences}
