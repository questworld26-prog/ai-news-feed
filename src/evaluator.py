"""
Evaluation Harness for AI News Voice Feed Pipeline.
Evaluates digest summaries across three rigorous layers:
1. Regex & Structural Check (header format, link hygiene, date presence)
2. HHH Guardrails (Helpful, Honest, Harmless)
3. LLM-as-a-Judge Factual Adherence & Pass Rate Metrics
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Any, NamedTuple

import requests

from validator import compute_keyword_overlap, detect_fabrications, validate_story

logger = logging.getLogger("ai_briefing")


class HHHVerdict(NamedTuple):
    honest_pass: bool
    honest_reasons: list[str]
    helpful_pass: bool
    helpful_reasons: list[str]
    harmless_pass: bool
    harmless_reasons: list[str]
    passed: bool


class EvaluationReport(NamedTuple):
    total_cases: int
    regex_pass_count: int
    hhh_pass_count: int
    llm_judge_pass_count: int
    overall_pass_rate: float
    details: list[dict[str, Any]]


def evaluate_regex_rules(digest_text: str, story: dict[str, Any], custom_regex: list[str] = None) -> tuple[bool, list[str]]:
    """
    Layer 1: Structural & Regex Checks.
    Validates markdown link format `## [Title](URL)`, date header, and link hygiene.
    """
    errors = []
    title = story.get("title", "")
    link = story.get("link", "")

    # Check header link format: ## [Title](URL)
    expected_header_pattern = rf"##\s*\[{re.escape(title)}\]\({re.escape(link)}\)"
    if not re.search(expected_header_pattern, digest_text):
        # Fallback check: title inside brackets and link inside parenthesised URL
        sub_pattern = rf"##\s*\[.*?{re.escape(title[:20])}.*?\]\(\s*{re.escape(link[:20])}.*?\)"
        if not re.search(sub_pattern, digest_text, re.IGNORECASE):
            errors.append(f"Header does not match required markdown link format: `## [{title}]({link})`")

    # Check for unformatted raw URLs (bare http:// or https:// outside markdown brackets)
    bare_urls = re.findall(r"(?<!\()https?://\S+(?!\))", digest_text)
    # Exclude links enclosed in markdown links
    for bu in bare_urls:
        if not re.search(rf"\]\({re.escape(bu)}\)", digest_text):
            errors.append(f"Bare URL found outside markdown link brackets: {bu}")

    # Custom regex validation
    if custom_regex:
        for pattern in custom_regex:
            if not re.search(pattern, digest_text, re.MULTILINE):
                errors.append(f"Failed required regex pattern match: {pattern}")

    return len(errors) == 0, errors


def evaluate_hhh_guardrails(digest_text: str, story: dict[str, Any]) -> HHHVerdict:
    """
    Layer 2: HHH Guardrails Evaluation (Helpful, Honest, Harmless).
    """
    source_text = f"{story.get('title', '')}\n{story.get('summary', '')}\n{story.get('link', '')}"
    
    # 1. Honest (Factual accuracy & zero unsupported fabrications)
    honest_reasons = []
    fabrications = detect_fabrications(source_text, digest_text)
    if fabrications:
        honest_reasons.extend(fabrications)

    overlap = compute_keyword_overlap(source_text, digest_text)
    if overlap < 0.35:
        honest_reasons.append(f"Low keyword overlap ({overlap:.2f} < 0.35) indicates potential hallucination.")

    honest_pass = len(honest_reasons) == 0

    # 2. Helpful (Formatted properly, non-empty, provides technical context)
    helpful_reasons = []
    words = len(digest_text.split())
    if words < 15:
        helpful_reasons.append(f"Digest summary too brief ({words} words < 15 words).")

    if "## [" not in digest_text:
        helpful_reasons.append("Missing structured heading link format.")

    helpful_pass = len(helpful_reasons) == 0

    # 3. Harmless (No hype, no speculative financial claims unless present in source)
    harmless_reasons = []
    hype_terms = ["guaranteed agi", "skyrocket valuation", "breakthrough hype", "game-changer"]
    for term in hype_terms:
        if term in digest_text.lower() and term not in source_text.lower():
            harmless_reasons.append(f"Unsubstantiated hype term detected: '{term}'")

    harmless_pass = len(harmless_reasons) == 0

    overall_pass = honest_pass and helpful_pass and harmless_pass

    return HHHVerdict(
        honest_pass=honest_pass,
        honest_reasons=honest_reasons,
        helpful_pass=helpful_pass,
        helpful_reasons=helpful_reasons,
        harmless_pass=harmless_pass,
        harmless_reasons=harmless_reasons,
        passed=overall_pass,
    )


def evaluate_llm_judge(digest_summary: str, story: dict[str, Any], config: dict[str, Any]) -> tuple[bool, float, str]:
    """
    Layer 3: LLM-as-a-Judge Factual Adherence Check.
    Returns (pass_boolean, score_float, reasoning_string).
    """
    source_text = f"{story.get('title', '')}\n{story.get('summary', '')}"
    validation_res = validate_story(story, digest_summary, config, run_llm_check=True)
    score = validation_res.keyword_overlap_score if validation_res.passed else 0.0
    return validation_res.passed, score, validation_res.llm_reasoning


def run_full_evaluation(golden_dataset_path: Path, config: dict[str, Any], generate_fn=None) -> EvaluationReport:
    """
    Run evaluation across the full Golden Dataset.
    If generate_fn is provided, it generates a digest for each story dynamically.
    Otherwise, it checks pre-generated digests or fallback mock digest format.
    """
    if not golden_dataset_path.exists():
        logger.error(f"Golden dataset file not found at {golden_dataset_path}")
        return EvaluationReport(0, 0, 0, 0, 0.0, [])

    with open(golden_dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    regex_passes = 0
    hhh_passes = 0
    llm_passes = 0
    details = []

    for item in cases:
        story = item.get("story", {})
        custom_regex = item.get("required_regex", [])

        if generate_fn:
            digest_text = generate_fn(story, item.get("theme", "practitioner_radar"))
        else:
            # Create standard formatted digest text for static checking
            digest_text = f"## [{story.get('title')}]({story.get('link')})\n\n{story.get('summary')}"

        regex_ok, regex_errors = evaluate_regex_rules(digest_text, story, custom_regex)
        if regex_ok:
            regex_passes += 1

        hhh = evaluate_hhh_guardrails(digest_text, story)
        if hhh.passed:
            hhh_passes += 1

        llm_pass, score, reasoning = evaluate_llm_judge(digest_text, story, config)
        if llm_pass:
            llm_passes += 1

        details.append({
            "id": item.get("id"),
            "title": story.get("title"),
            "regex_pass": regex_ok,
            "regex_errors": regex_errors,
            "hhh_pass": hhh.passed,
            "hhh_verdict": hhh,
            "llm_pass": llm_pass,
            "llm_score": score,
            "llm_reasoning": reasoning,
        })

    total = len(cases)
    overall_pass_rate = (llm_passes / total) if total > 0 else 0.0

    return EvaluationReport(
        total_cases=total,
        regex_pass_count=regex_passes,
        hhh_pass_count=hhh_passes,
        llm_judge_pass_count=llm_passes,
        overall_pass_rate=overall_pass_rate,
        details=details,
    )
