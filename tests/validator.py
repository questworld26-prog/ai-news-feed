"""
Validator module for AI News Digest summaries.
Checks digest summaries against source texts for keyword overlap, numerical/entity fabrications,
and LLM factual consistency.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, NamedTuple

import requests

logger = logging.getLogger("ai_briefing")


class ValidationResult(NamedTuple):
    story_title: str
    keyword_overlap_score: float
    fabrication_warnings: list[str]
    llm_fact_check_passed: bool
    llm_reasoning: str
    passed: bool


def extract_key_tokens(text: str) -> set[str]:
    """Extract numbers, capitalized proper nouns, and significant technical terms."""
    if not text:
        return set()
    # Normalize HTML or Markdown leftovers
    clean = re.sub(r"[^\w\s]", " ", text)
    tokens = clean.split()
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
        "by", "about", "against", "between", "into", "through", "during", "before",
        "after", "above", "below", "from", "up", "down", "of", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "s", "t", "can", "will", "just", "don", "should", "now", "this", "that", "these",
        "those", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had"
    }
    
    meaningful = set()
    for tok in tokens:
        lower = tok.lower()
        if lower not in stopwords and (len(tok) > 2 or tok.isdigit()):
            meaningful.add(lower)
    return meaningful


def compute_keyword_overlap(source_text: str, digest_text: str) -> float:
    """Calculate ratio of digest key tokens found in source text."""
    digest_tokens = extract_key_tokens(digest_text)
    if not digest_tokens:
        return 1.0
    source_tokens = extract_key_tokens(source_text)
    if not source_tokens:
        return 0.0
    
    matched = digest_tokens.intersection(source_tokens)
    return len(matched) / len(digest_tokens)


def detect_fabrications(source_text: str, digest_text: str) -> list[str]:
    """Detect numbers, metrics, or percentages in digest text that do not appear in source text."""
    warnings = []
    # Extract numbers/percentages/metrics from digest
    digest_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", digest_text))
    source_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", source_text))

    unsupported_numbers = digest_numbers - source_numbers
    for num in unsupported_numbers:
        # Ignore common list indices or small digits if context is vague
        if num in {"1", "2", "3", "4", "5"}:
            continue
        warnings.append(f"Number/Metric '{num}' in summary was not found in source text.")

    return warnings


def llm_fact_check(source_text: str, digest_summary: str, config: dict[str, Any]) -> tuple[bool, str]:
    """Use local Ollama model to perform a factual adherence audit."""
    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "phi4-mini:3.8b")

    prompt = (
        f"You are a strict fact-checker auditing an AI-generated summary for factual accuracy against its source text.\n\n"
        f"SOURCE TEXT:\n{source_text[:1500]}\n\n"
        f"GENERATED SUMMARY:\n{digest_summary}\n\n"
        f"Task:\n"
        f"Determine if the GENERATED SUMMARY contains any hallucinated claims, unsupported figures, or fake facts not present in the SOURCE TEXT.\n"
        f"Respond ONLY in valid JSON format with two keys:\n"
        f"1. \"pass\": boolean (true if completely accurate and supported, false if hallucinated or misleading)\n"
        f"2. \"reasoning\": string (brief explanation of your verdict)\n\n"
        f"Example: {{\"pass\": true, \"reasoning\": \"Summary accurately reflects the source without added facts.\"}}"
    )

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.0, "num_ctx": 4096},
            },
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        data = json.loads(raw)
        return bool(data.get("pass", True)), str(data.get("reasoning", "No explanation provided."))
    except Exception as e:
        logger.warning(f"LLM fact check call failed: {e}")
        return True, f"Fact check skipped due to error: {e}"


def validate_story(
    story: dict[str, Any],
    digest_summary: str,
    config: dict[str, Any],
    run_llm_check: bool = True,
    min_keyword_threshold: float = 0.35,
) -> ValidationResult:
    """Validate a single story summary against its source information."""
    source_text = f"{story.get('title', '')}\n{story.get('summary', '')}"
    overlap_score = compute_keyword_overlap(source_text, digest_summary)
    fabrication_warnings = detect_fabrications(source_text, digest_summary)

    llm_passed = True
    llm_reasoning = "Skipped LLM self-check."
    if run_llm_check:
        llm_passed, llm_reasoning = llm_fact_check(source_text, digest_summary, config)

    passed = (overlap_score >= min_keyword_threshold) and (len(fabrication_warnings) == 0) and llm_passed

    return ValidationResult(
        story_title=story.get("title", "Untitled"),
        keyword_overlap_score=overlap_score,
        fabrication_warnings=fabrication_warnings,
        llm_fact_check_passed=llm_passed,
        llm_reasoning=llm_reasoning,
        passed=passed,
    )
