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
from pydantic import AliasChoices, BaseModel, Field

from story import Story

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
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "with",
        "by",
        "about",
        "against",
        "between",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "from",
        "up",
        "down",
        "of",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "s",
        "t",
        "can",
        "will",
        "just",
        "don",
        "should",
        "now",
        "this",
        "that",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
    }

    meaningful = set()
    # Common short technical acronyms/models in AI
    known_ai_tokens = {"ai", "ml", "ci", "dl", "cv", "rl", "llm", "rag", "slm", "nlp", "gpu", "tpu", "vllm"}

    for tok in tokens:
        lower = tok.lower()
        if lower in stopwords:
            continue
        # Preserve:
        # 1. Standard words > 2 chars or pure numbers
        # 2. Known AI acronyms (ai, ml, ci, etc.)
        # 3. Uppercase 2-letter acronyms from original text (e.g. AI, ML, CI)
        # 4. Alphanumeric model identifiers (e.g. o1, o3, r1, v2, v3, 4o)
        is_model_or_acronym = (
            lower in known_ai_tokens
            or (len(tok) == 2 and tok.isupper())
            or bool(re.match(r"^[a-zA-Z]\d+$|^\d+[a-zA-Z]+$", tok))
        )
        if len(tok) > 2 or tok.isdigit() or is_model_or_acronym:
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
    # Extract semver/multi-part version numbers or float/percentage numbers
    digest_numbers = set(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", digest_text))
    source_numbers = set(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", source_text))

    for num in digest_numbers:
        if num in {"1", "2", "3", "4", "5"}:
            continue
        # Check if number appears in source numbers or as literal substring in source text
        if num not in source_numbers and num not in source_text:
            warnings.append(f"Number/Metric '{num}' in summary was not found in source text.")

    return warnings


class FactCheckResponse(BaseModel):
    reasoning: str = Field(
        description="Detailed step-by-step reasoning evaluating factual adherence and checking for fabrications or URLs"
    )
    passed: bool = Field(
        validation_alias=AliasChoices("passed", "pass"),
        description="True if the summary is factually grounded in the source text without hallucinated facts/figures/links, False otherwise",
    )


def llm_fact_check(source_text: str, digest_summary: str, config: dict[str, Any]) -> tuple[bool, str]:
    """Use local Ollama model to perform a factual adherence audit."""
    llm_cfg = config.get("llm", {})
    testing_cfg = config.get("testing", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = testing_cfg.get("test_model") or llm_cfg.get("model", "qwen2.5:3b")

    # Expanded to 4000 characters so multi-story scripts have complete source visibility
    prompt = (
        f"You are an auditing tool checking if an AI-generated summary is factually grounded in the source text.\n\n"
        f"SOURCE TEXT:\n{source_text[:4000]}\n\n"
        f"GENERATED SUMMARY:\n{digest_summary}\n\n"
        f"Task:\n"
        f"1. Write detailed 'reasoning' evaluating if the GENERATED SUMMARY contains:\n"
        f"   - Completely fabricated figures or statistics not present in SOURCE TEXT.\n"
        f"   - Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT.\n"
        f"   - Embedded markdown links/URLs.\n"
        f"2. Set 'passed': true if grounded in source text (reasonable paraphrasing is allowed), false otherwise."
    )

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": FactCheckResponse.model_json_schema(),
                "stream": False,
                "options": {"temperature": 0.0, "num_ctx": 4096},
            },
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        data = json.loads(raw)
        res_obj = FactCheckResponse.model_validate(data)
        return res_obj.passed, res_obj.reasoning.strip()
    except Exception as e:
        logger.warning(f"LLM fact check call failed: {e}")
        # Fail closed: do not silently pass unverified summaries
        return False, f"Fact check failed due to error: {e}"


def validate_story(
    story: Story | dict[str, Any],
    digest_summary: str,
    config: dict[str, Any],
    run_llm_check: bool = True,
    min_keyword_threshold: float = 0.35,
) -> ValidationResult:
    """Validate a single story summary against its source information."""
    s_obj = story if isinstance(story, Story) else Story.from_dict(story)

    source_text = f"{s_obj.title}\n{s_obj.summary}\n{s_obj.link}"

    # Isolate section for this specific story from full digest if possible
    story_title = s_obj.title
    target_digest = digest_summary
    if story_title and story_title in digest_summary:
        parts = digest_summary.split(story_title)
        if len(parts) > 1:
            target_digest = parts[1].split("\n\n##")[0][:600]

    overlap_score = compute_keyword_overlap(source_text, target_digest)
    fabrication_warnings = detect_fabrications(source_text, target_digest)

    llm_passed = True
    llm_reasoning = "Skipped LLM self-check."
    if run_llm_check:
        llm_passed, llm_reasoning = llm_fact_check(source_text, target_digest, config)

    passed = (overlap_score >= min_keyword_threshold) and (len(fabrication_warnings) == 0) and llm_passed

    return ValidationResult(
        story_title=s_obj.title,
        keyword_overlap_score=overlap_score,
        fabrication_warnings=fabrication_warnings,
        llm_fact_check_passed=llm_passed,
        llm_reasoning=llm_reasoning,
        passed=passed,
    )
