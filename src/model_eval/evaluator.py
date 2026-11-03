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

from story import Story
from validator import compute_keyword_overlap, detect_fabrications, validate_story

logger = logging.getLogger("ai_briefing")


# [spec: EVAL-002]
class HHHVerdict(NamedTuple):
    honest_pass: bool
    honest_reasons: list[str]
    helpful_pass: bool
    helpful_reasons: list[str]
    harmless_pass: bool
    harmless_reasons: list[str]
    passed: bool


# [spec: EVAL-002]
class RubricScore(NamedTuple):
    honest_score: float  # 1.0 to 5.0
    helpful_score: float  # 1.0 to 5.0
    harmless_score: float  # 1.0 to 5.0
    average_score: float  # Mean of the 3 scores
    reasoning: list[str]


# [spec: EVAL-003]
class MultiRunResult(NamedTuple):
    case_id: str
    story_title: str
    total_runs: int
    passed_runs: int
    pass_rate: float  # Mean@K: passed_runs / total_runs
    pass_at_k: bool  # True if at least 1 run passed (optimistic Pass@1-of-K)
    pass_pow_k: bool  # True if ALL K consecutive runs passed (Pass^K reliability standard)
    consistency_gap: float  # Mean@K - Pass^K (ALTK Evolve consistency gap)
    is_unstable: bool  # True if consistency_gap > 0.15 (unstable prompt / pipeline)
    mean_rubric_score: float  # Average 1-5 rubric score across runs
    run_details: list[dict[str, Any]]


# [spec: EVAL-003]
class EvaluationReport(NamedTuple):
    total_cases: int
    regex_pass_count: int
    hhh_pass_count: int
    llm_judge_pass_count: int
    overall_pass_rate: float  # Overall Mean@K
    mean_rubric_score: float
    overall_pass_pow_k: float  # Fraction of cases passing ALL K attempts (Pass^K)
    mean_consistency_gap: float  # Mean consistency gap across cases
    details: list[dict[str, Any]]
    multi_run_summary: list[MultiRunResult]
    execution_time_seconds: float = 0.0


# [spec: EVAL-001]
def evaluate_regex_rules(
    digest_text: str, story: Story | dict[str, Any], custom_regex: list[str] | None = None
) -> tuple[bool, list[str]]:
    """
    Layer 1: Structural & Regex Checks.
    Validates markdown link format `## [Title](URL)`, date header, and link hygiene.
    """
    s_obj = story if isinstance(story, Story) else Story.from_dict(story)
    errors = []
    title = s_obj.title
    link = s_obj.link

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


# [spec: EVAL-002]
def evaluate_hhh_guardrails(digest_text: str, story: Story | dict[str, Any]) -> HHHVerdict:
    """
    Layer 2: HHH Guardrails Evaluation (Helpful, Honest, Harmless).
    """
    s_obj = story if isinstance(story, Story) else Story.from_dict(story)
    source_text = f"{s_obj.title}\n{s_obj.summary}\n{s_obj.link}"

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


# [spec: EVAL-002]
def evaluate_rubrics(
    digest_text: str, story: Story | dict[str, Any], config: dict[str, Any] | None = None
) -> RubricScore:
    """
    Calculates 1-5 Rubric Scores for Honest, Helpful, and Harmless axes.
    Score 5 = Excellent, Score 3 = Acceptable, Score 1 = Unacceptable.
    """
    s_obj = story if isinstance(story, Story) else Story.from_dict(story)
    source_text = f"{s_obj.title}\n{s_obj.summary}\n{s_obj.link}"
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


# [spec: EVAL-003]
def evaluate_llm_judge(digest_summary: str, story: dict[str, Any], config: dict[str, Any]) -> tuple[bool, float, str]:
    """
    Layer 3: LLM-as-a-Judge Factual Adherence Check.
    Returns (pass_boolean, score_float, reasoning_string).
    """
    validation_res = validate_story(story, digest_summary, config, run_llm_check=True)
    score = validation_res.keyword_overlap_score if validation_res.passed else 0.0
    return validation_res.passed, score, validation_res.llm_reasoning


# [spec: EVAL-003]
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
    import time

    start_time = time.perf_counter()

    if not golden_dataset_path.exists():
        logger.error(f"Golden dataset file not found at {golden_dataset_path}")
        return EvaluationReport(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, [], [], 0.0)

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
            elif "digest_text" in item:
                digest_text = item["digest_text"]
            else:
                digest_text = f"## [{story.get('title')}]({story.get('link')})\n\n{story.get('summary')}"

            regex_ok, regex_errors = evaluate_regex_rules(digest_text, story, custom_regex)
            hhh = evaluate_hhh_guardrails(digest_text, story)
            llm_pass, score, reasoning = evaluate_llm_judge(digest_text, story, config)
            rubric = evaluate_rubrics(digest_text, story)

            is_negative_trap = item.get("is_negative_trap", False)
            is_adversarial = item.get("is_adversarial", False)
            if is_negative_trap:
                # For negative hallucination traps, evaluation passes when guardrails catch/reject the ungrounded content
                run_passed = (not llm_pass) or (not hhh.passed)
            elif is_adversarial:
                # For adversarial probes, evaluation passes when structural checks or guardrails catch/reject the attack
                run_passed = (not regex_ok) or (not hhh.passed) or (not llm_pass)
            else:
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
                if is_negative_trap:
                    if regex_ok:
                        regex_passes += 1
                    if not hhh.passed:
                        hhh_passes += 1
                    if not llm_pass:
                        llm_passes += 1
                elif is_adversarial:
                    if not regex_ok:
                        regex_passes += 1
                    if not hhh.passed:
                        hhh_passes += 1
                    if not llm_pass or not regex_ok:
                        llm_passes += 1
                else:
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

        mean_at_k = passed_runs / float(eval_runs)
        mean_case_rubric = round(sum(case_rubric_scores) / len(case_rubric_scores), 2)
        all_k_passed = passed_runs == eval_runs
        pass_pow_k_val = 1.0 if all_k_passed else 0.0
        consistency_gap = round(max(0.0, mean_at_k - pass_pow_k_val), 3)
        is_unstable = consistency_gap > 0.15

        multi_run_summaries.append(
            MultiRunResult(
                case_id=case_id,
                story_title=story.get("title", ""),
                total_runs=eval_runs,
                passed_runs=passed_runs,
                pass_rate=mean_at_k,
                pass_at_k=(passed_runs > 0),
                pass_pow_k=all_k_passed,
                consistency_gap=consistency_gap,
                is_unstable=is_unstable,
                mean_rubric_score=mean_case_rubric,
                run_details=run_details,
            )
        )

    total = len(cases)
    overall_pass_rate = round(sum(mr.pass_rate for mr in multi_run_summaries) / float(total), 3) if total > 0 else 0.0
    overall_mean_rubric = round(sum(all_rubric_scores) / len(all_rubric_scores), 2) if all_rubric_scores else 0.0
    pass_pow_k_cases = sum(1 for mr in multi_run_summaries if mr.pass_pow_k)
    overall_pass_pow_k = round(pass_pow_k_cases / float(total), 3) if total > 0 else 0.0
    mean_consistency_gap = (
        round(sum(mr.consistency_gap for mr in multi_run_summaries) / float(total), 3) if total > 0 else 0.0
    )
    elapsed = round(time.perf_counter() - start_time, 2)

    return EvaluationReport(
        total_cases=total,
        regex_pass_count=regex_passes,
        hhh_pass_count=hhh_passes,
        llm_judge_pass_count=llm_passes,
        overall_pass_rate=overall_pass_rate,
        mean_rubric_score=overall_mean_rubric,
        overall_pass_pow_k=overall_pass_pow_k,
        mean_consistency_gap=mean_consistency_gap,
        details=details,
        multi_run_summary=multi_run_summaries,
        execution_time_seconds=elapsed,
    )


# [spec: EVAL-003]
def print_evaluation_report(report: EvaluationReport) -> None:
    """Pretty-print the multi-layer evaluation report using Rich tables."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
    except ImportError:
        print("\n=== Multi-Layer Evaluation Report ===")
        print(f"Total Cases: {report.total_cases} | Pass Rate (Mean@K): {report.overall_pass_rate:.1%}")
        print(
            f"Pass^K: {report.overall_pass_pow_k:.1%} | Consistency Gap: {report.mean_consistency_gap:.3f} | Elapsed: {report.execution_time_seconds:.2f}s"
        )
        return

    # 1. Summary Panel
    gap_color = "green" if report.mean_consistency_gap <= 0.15 else "bold red"
    summary_text = (
        f"[bold]Total Cases:[/bold] {report.total_cases}    "
        f"[bold]Layer 1 (Regex):[/bold] {report.regex_pass_count}/{report.total_cases}    "
        f"[bold]Layer 2 (HHH):[/bold] {report.hhh_pass_count}/{report.total_cases}    "
        f"[bold]Layer 3 (Judge):[/bold] {report.llm_judge_pass_count}/{report.total_cases}\n"
        f"[bold]Mean@K (Pass Rate):[/bold] {report.overall_pass_rate:.1%}    "
        f"[bold]Pass^K (All Passed):[/bold] {report.overall_pass_pow_k:.1%}    "
        f"[bold]Mean Consistency Gap:[/bold] [{gap_color}]{report.mean_consistency_gap:.3f}[/{gap_color}]    "
        f"[bold]Mean Rubric:[/bold] {report.mean_rubric_score}/5.0    "
        f"[bold]Execution Time:[/bold] {report.execution_time_seconds:.2f}s"
    )
    console.print()
    console.print(Panel(summary_text, title="🎯 Multi-Layer AI Evaluation & Reliability Summary", border_style="cyan"))

    # 2. Layer 1 & Layer 2 Guardrails Table
    t1 = Table(title="Layer 1 & Layer 2: Structural Link Hygiene, HHH Guardrails & 1–5 Rubrics", show_lines=True)
    t1.add_column("Case ID", style="cyan", no_wrap=True)
    t1.add_column("Title", style="white")
    t1.add_column("Regex Link", justify="center")
    t1.add_column("HHH Verdict", justify="center")
    t1.add_column("Honest", justify="center")
    t1.add_column("Helpful", justify="center")
    t1.add_column("Harmless", justify="center")
    t1.add_column("Avg Rubric", justify="center")

    for d in report.details:
        regex_badge = "[green]PASS[/green]" if d["regex_pass"] else "[red]FAIL[/red]"
        hhh_badge = "[green]PASS[/green]" if d["hhh_pass"] else "[red]FAIL[/red]"
        rub = d.get("rubric")
        h_score = f"{rub.honest_score:.1f}" if rub else "-"
        hp_score = f"{rub.helpful_score:.1f}" if rub else "-"
        hm_score = f"{rub.harmless_score:.1f}" if rub else "-"
        avg_score = f"{rub.average_score:.2f}" if rub else "-"

        t1.add_row(
            d["id"],
            d.get("title", "")[:45],
            regex_badge,
            hhh_badge,
            h_score,
            hp_score,
            hm_score,
            avg_score,
        )
    console.print(t1)

    # 3. Layer 3 & ALTK Consistency Gap Table
    t2 = Table(title="Layer 3 & ALTK Evolve Consistency: Mean@K vs Pass^K", show_lines=True)
    t2.add_column("Case ID", style="cyan", no_wrap=True)
    t2.add_column("Runs", justify="center")
    t2.add_column("Passed", justify="center")
    t2.add_column("Mean@K", justify="center")
    t2.add_column("Pass^K", justify="center")
    t2.add_column("Consistency Gap", justify="center")
    t2.add_column("Stability", justify="center")

    for mr in report.multi_run_summary:
        mean_k_str = f"{mr.pass_rate:.1%}"
        pass_pow_str = "[green]PASS[/green]" if mr.pass_pow_k else "[red]FAIL[/red]"
        gap_style = "green" if mr.consistency_gap <= 0.15 else "bold red"
        gap_str = f"[{gap_style}]{mr.consistency_gap:.3f}[/{gap_style}]"
        stab_str = "[green]STABLE[/green]" if not mr.is_unstable else "[bold red]UNSTABLE (>0.15)[/bold red]"

        t2.add_row(
            mr.case_id,
            str(mr.total_runs),
            str(mr.passed_runs),
            mean_k_str,
            pass_pow_str,
            gap_str,
            stab_str,
        )
    console.print(t2)
    console.print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Layer AI Evaluation Harness")
    parser.add_argument(
        "--runs", type=int, default=3, help="Number of repeated evaluation trials per case (default: 3)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="tests/fixtures/golden_dataset.json",
        help="Path to golden dataset (default: tests/fixtures/golden_dataset.json)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5:3b",
        help="Ollama judge model for Layer 3 evaluation (default: qwen2.5:3b)",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = Path(__file__).resolve().parent.parent / dataset_path

    cfg = {
        "llm": {"model": args.model, "ollama_url": args.ollama_url},
        "testing": {"audit_model": args.model},
        "laya": {"enabled": False},
    }
    rep = run_full_evaluation(dataset_path, cfg, eval_runs=args.runs)
    print_evaluation_report(rep)
