"""
Evaluation Harness for AI News Voice Feed Pipeline.
Evaluates digest summaries across three rigorous layers:
1. Regex & Structural Check (header format, link hygiene, date presence)
2. HHH Guardrails (Helpful, Honest, Harmless) with 1-5 Rubric Scoring Matrix
3. LLM-as-a-Judge Factual Adherence & Multi-Run Pass@K / Pass Rate Metrics
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, NamedTuple

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


class RubricScore(NamedTuple):
    honest_score: float  # 1.0 to 5.0
    helpful_score: float  # 1.0 to 5.0
    harmless_score: float  # 1.0 to 5.0
    average_score: float  # Mean of the 3 scores
    reasoning: list[str]


class MultiRunResult(NamedTuple):
    case_id: str
    story_title: str
    total_runs: int
    passed_runs: int
    pass_rate: float  # passed_runs / total_runs
    pass_at_k: bool  # True if at least 1 run passed
    mean_rubric_score: float  # Average 1-5 rubric score across runs
    run_details: list[dict[str, Any]]


class EvaluationReport(NamedTuple):
    total_cases: int
    regex_pass_count: int
    hhh_pass_count: int
    llm_judge_pass_count: int
    overall_pass_rate: float
    mean_rubric_score: float
    details: list[dict[str, Any]]
    multi_run_summary: list[MultiRunResult]


def evaluate_regex_rules(
    digest_text: str, story: dict[str, Any], custom_regex: list[str] | None = None
) -> tuple[bool, list[str]]:
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
        sub_pattern = rf"##\s*\[.*?{re.escape(title[:20])}.*?\]\(\s*{re.escape(link[:20])}.*?\)"
        if not re.search(sub_pattern, digest_text, re.IGNORECASE):
            errors.append(f"Header does not match required markdown link format: `## [{title}]({link})`")

    # Check for unformatted raw URLs (bare http:// or https:// outside markdown brackets)
    bare_urls = re.findall(r"(?<!\()https?://\S+(?!\))", digest_text)
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


def evaluate_rubrics(digest_text: str, story: dict[str, Any], config: dict[str, Any] | None = None) -> RubricScore:
    """
    Calculates 1-5 Rubric Scores for Honest, Helpful, and Harmless axes.
    Score 5 = Excellent, Score 3 = Acceptable, Score 1 = Unacceptable.
    """
    source_text = f"{story.get('title', '')}\n{story.get('summary', '')}\n{story.get('link', '')}"
    reasons = []

    # Honest Rubric (1-5)
    fabrications = detect_fabrications(source_text, digest_text)
    overlap = compute_keyword_overlap(source_text, digest_text)

    if fabrications:
        honest_score = 1.0
        reasons.append(f"Honest Score 1.0: Fabrications detected ({', '.join(fabrications)})")
    elif overlap < 0.35:
        honest_score = 2.5
        reasons.append(f"Honest Score 2.5: Low keyword overlap ({overlap:.2f})")
    elif overlap < 0.60:
        honest_score = 4.0
        reasons.append(f"Honest Score 4.0: Acceptable factual accuracy ({overlap:.2f})")
    else:
        honest_score = 5.0
        reasons.append(f"Honest Score 5.0: High factual fidelity ({overlap:.2f})")

    # Helpful Rubric (1-5)
    words = len(digest_text.split())
    has_header = "## [" in digest_text
    if not has_header or words < 10:
        helpful_score = 1.0
        reasons.append("Helpful Score 1.0: Missing markdown title header link or empty content")
    elif words < 25:
        helpful_score = 3.0
        reasons.append("Helpful Score 3.0: Brief technical summary")
    else:
        helpful_score = 5.0
        reasons.append("Helpful Score 5.0: Rich technical breakdown with valid title link")

    # Harmless Rubric (1-5)
    hype_terms = ["guaranteed agi", "skyrocket valuation", "breakthrough hype", "game-changer"]
    found_hype = [t for t in hype_terms if t in digest_text.lower() and t not in source_text.lower()]
    if found_hype:
        harmless_score = 1.0
        reasons.append(f"Harmless Score 1.0: Hype terms present ({', '.join(found_hype)})")
    else:
        harmless_score = 5.0
        reasons.append("Harmless Score 5.0: Clean, objective engineering tone")

    avg_score = round((honest_score + helpful_score + harmless_score) / 3.0, 2)

    return RubricScore(
        honest_score=honest_score,
        helpful_score=helpful_score,
        harmless_score=harmless_score,
        average_score=avg_score,
        reasoning=reasons,
    )


def evaluate_llm_judge(digest_summary: str, story: dict[str, Any], config: dict[str, Any]) -> tuple[bool, float, str]:
    """
    Layer 3: LLM-as-a-Judge Factual Adherence Check.
    Returns (pass_boolean, score_float, reasoning_string).
    """
    validation_res = validate_story(story, digest_summary, config, run_llm_check=True)
    score = validation_res.keyword_overlap_score if validation_res.passed else 0.0
    return validation_res.passed, score, validation_res.llm_reasoning


def run_full_evaluation(
    golden_dataset_path: Path,
    config: dict[str, Any],
    generate_fn=None,
    eval_runs: int = 1,
) -> EvaluationReport:
    """
    Run evaluation across the full Golden Dataset over eval_runs (default 1).
    Calculates Pass Rate %, Pass@K, and Mean Rubric Scores across multi-run trials.
    """
    if not golden_dataset_path.exists():
        logger.error(f"Golden dataset file not found at {golden_dataset_path}")
        return EvaluationReport(0, 0, 0, 0, 0.0, 0.0, [], [])

    with open(golden_dataset_path, encoding="utf-8") as f:
        cases = json.load(f)

    regex_passes = 0
    hhh_passes = 0
    llm_passes = 0
    all_rubric_scores = []
    details = []
    multi_run_summaries = []

    for item in cases:
        story = item.get("story", {})
        custom_regex = item.get("required_regex", [])
        case_id = item.get("id", "unknown")

        run_details = []
        passed_runs = 0
        case_rubric_scores = []

        for run_idx in range(1, eval_runs + 1):
            if generate_fn:
                digest_text = generate_fn(story, item.get("theme", "practitioner_radar"))
            else:
                digest_text = f"## [{story.get('title')}]({story.get('link')})\n\n{story.get('summary')}"

            regex_ok, regex_errors = evaluate_regex_rules(digest_text, story, custom_regex)
            hhh = evaluate_hhh_guardrails(digest_text, story)
            llm_pass, score, reasoning = evaluate_llm_judge(digest_text, story, config)
            rubric = evaluate_rubrics(digest_text, story, config)

            run_passed = regex_ok and hhh.passed and llm_pass
            if run_passed:
                passed_runs += 1

            case_rubric_scores.append(rubric.average_score)
            all_rubric_scores.append(rubric.average_score)

            run_details.append(
                {
                    "run_idx": run_idx,
                    "regex_pass": regex_ok,
                    "hhh_pass": hhh.passed,
                    "llm_pass": llm_pass,
                    "rubric_score": rubric.average_score,
                    "reasoning": reasoning,
                }
            )

            # Use first run for primary summary counters
            if run_idx == 1:
                if regex_ok:
                    regex_passes += 1
                if hhh.passed:
                    hhh_passes += 1
                if llm_pass:
                    llm_passes += 1

                details.append(
                    {
                        "id": case_id,
                        "title": story.get("title"),
                        "regex_pass": regex_ok,
                        "regex_errors": regex_errors,
                        "hhh_pass": hhh.passed,
                        "hhh_verdict": hhh,
                        "llm_pass": llm_pass,
                        "llm_score": score,
                        "llm_reasoning": reasoning,
                        "rubric": rubric,
                    }
                )

        pass_rate = passed_runs / float(eval_runs)
        mean_case_rubric = round(sum(case_rubric_scores) / len(case_rubric_scores), 2)

        multi_run_summaries.append(
            MultiRunResult(
                case_id=case_id,
                story_title=story.get("title", ""),
                total_runs=eval_runs,
                passed_runs=passed_runs,
                pass_rate=pass_rate,
                pass_at_k=(passed_runs > 0),
                mean_rubric_score=mean_case_rubric,
                run_details=run_details,
            )
        )

    total = len(cases)
    overall_pass_rate = (llm_passes / total) if total > 0 else 0.0
    overall_mean_rubric = round(sum(all_rubric_scores) / len(all_rubric_scores), 2) if all_rubric_scores else 0.0

    return EvaluationReport(
        total_cases=total,
        regex_pass_count=regex_passes,
        hhh_pass_count=hhh_passes,
        llm_judge_pass_count=llm_passes,
        overall_pass_rate=overall_pass_rate,
        mean_rubric_score=overall_mean_rubric,
        details=details,
        multi_run_summary=multi_run_summaries,
    )
