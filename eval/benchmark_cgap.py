"""
Empirical Benchmark: Baseline vs CGAP Monologue Generation.
Measures the quantitative impact of Capability-Grounded Agentic Planning (ADR-14)
across Story Coverage, Sequence Order, Metric Grounding, Flattery, and Latency.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any

# Ensure src is in python path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from briefing_generator import clean_script_for_audio  # noqa: E402
from cgap_planner import build_cgap_script_plan, compile_story_predicates, verify_cgap_grounding  # noqa: E402
from model_provider import ModelProviderFactory  # noqa: E402
from story import Story  # noqa: E402

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("cgap_benchmark")


def run_benchmark(model: str = "phi4-mini:3.8b", runs: int = 2) -> dict[str, Any]:
    # Load test case from golden dataset
    dataset_path = REPO_ROOT / "eval" / "golden_dataset.json"
    with open(dataset_path) as f:
        dataset = json.load(f)

    script_case = next(c for c in dataset if c.get("id") == "script_radar_monologue_01")
    input_stories = [
        Story(
            source="Tech Wire",
            title=s["title"],
            link="https://example.com",
            summary=s["summary"],
            validated_summary=s["summary"],
        )
        for s in script_case["input_stories"]
    ]
    theme_name = script_case["theme_dict"]["name"]
    theme_tone = script_case["theme_dict"]["tone"]
    word_target = 450  # Compact target for fast benchmark runs

    predicates = compile_story_predicates(input_stories)
    cgap_plan = build_cgap_script_plan(predicates, theme_name)

    # 1. Baseline Prompt (Pre-CGAP: unstructured narrative without symbolic plan)
    stories_raw_block = "\n".join([f"{idx}. {s.title}: {s.summary}" for idx, s in enumerate(input_stories, 1)])
    baseline_prompt = (
        f"You are a professional tech podcast host briefing an engineering peer. "
        f"Today's thematic lens is: '{theme_name}'. Editorial tone: {theme_tone}.\n\n"
        f"Here are the stories to cover:\n{stories_raw_block}\n\n"
        f"Task:\n"
        f"Write a complete, natural spoken podcast monologue script of approximately {word_target} words covering these stories.\n"
        f"Rules: Open smoothly, transition naturally between stories, and conclude with a professional wrap-up.\n"
        f"Output ONLY the spoken script text."
    )

    # 2. Treatment Prompt (CGAP: explicit symbolic plan and allowed facts per step)
    cgap_prompt = (
        f"You are a concise, sharp technical news presenter briefing a software engineer or CTO. "
        f"Today's thematic lens is: '{theme_name}'. Editorial tone: {theme_tone}.\n\n"
        f"{cgap_plan}\n\n"
        f"Task:\n"
        f"Write a spoken briefing monologue script of approximately {word_target} words following the exact CGAP Execution Steps above.\n\n"
        f"STRICT EDITORIAL RULES:\n"
        f"- ZERO FLATTERY & ZERO PREAMBLE: Direct opening with theme and first story.\n"
        f"- SEQUENCE ADHERENCE: Cover every story in exact numerical order (Story #1 to #{len(input_stories)}).\n"
        f"- STRICT GROUNDING: Confine claims and metrics exclusively to Allowed Facts.\n"
        f"- CLEAN CONCLUSION: End cleanly with 'That is your briefing for today.'\n"
        f"Output ONLY the spoken script text."
    )

    config = {"llm": {"model": model, "ollama_url": "http://localhost:11434"}}
    provider = ModelProviderFactory.get_provider(config)

    print("\n==========================================================================")
    print(f"🚀 RUNNING EMPIRICAL CGAP BENCHMARK ({model}) — {runs} RUNS PER CONDITION")
    print("==========================================================================")

    results: dict[str, list[dict[str, Any]]] = {"baseline": [], "cgap": []}

    conditions = [
        ("Baseline (Pre-CGAP)", baseline_prompt, "baseline"),
        ("Treatment (CGAP Grounded)", cgap_prompt, "cgap"),
    ]

    for label, prompt, key in conditions:
        print(f"\nEvaluating: {label}...")
        for r in range(1, runs + 1):
            t0 = time.perf_counter()
            try:
                raw_script = provider.generate(
                    prompt=prompt,
                    model=model,
                    temperature=0.7,
                    num_ctx=4096,
                    timeout=120,
                )
                duration = time.perf_counter() - t0
                clean_script = clean_script_for_audio(raw_script)

                # Evaluate with CGAP deterministic gate
                cgap_eval = verify_cgap_grounding(clean_script, predicates, config)

                # Theatrical flattery check on raw script
                flattery_matches = len(
                    re.findall(
                        r"(?i)\b(welcome back|intellectual voyage|journey through|embark on|in conclusion|thank you for joining|until next time)\b",
                        raw_script,
                    )
                )

                # Metric hallucination check
                all_permitted_metrics = set()
                for p in predicates:
                    all_permitted_metrics.update(p.metrics)
                    all_permitted_metrics.update(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", p.summary))
                script_metrics = set(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", clean_script))
                fabricated_numbers = [
                    n
                    for n in script_metrics
                    if n not in {"1", "2", "3", "4", "5", str(len(input_stories))} and n not in all_permitted_metrics
                ]

                run_data = {
                    "run": r,
                    "duration_s": round(duration, 2),
                    "word_count": len(clean_script.split()),
                    "coverage_pct": round(len(cgap_eval.covered_story_ids) / len(input_stories) * 100, 1),
                    "is_ordered": cgap_eval.is_ordered,
                    "flattery_count": flattery_matches,
                    "fabricated_metrics_count": len(fabricated_numbers),
                    "passed_cgap_gate": cgap_eval.passed,
                }
                results[key].append(run_data)
                print(
                    f"  Run {r}: {duration:.1f}s | Words: {run_data['word_count']} | Coverage: {run_data['coverage_pct']}% | Ordered: {run_data['is_ordered']} | Flattery: {run_data['flattery_count']} | Gate: {'PASS' if cgap_eval.passed else 'FAIL'}"
                )
                if not cgap_eval.passed:
                    print(f"    └─ Violations: {cgap_eval.violations}")
                print(f'    └─ Script Preview: "{clean_script[:180]}..."')
            except Exception as e:
                print(f"  Run {r} FAILED: {e}")

    return results


def print_comparison_table(results: dict[str, list[dict[str, Any]]]) -> None:
    def avg(lst, key):
        return sum(x[key] for x in lst) / len(lst) if lst else 0

    def pct_true(lst, key):
        return (sum(1 for x in lst if x[key]) / len(lst) * 100) if lst else 0

    base = results["baseline"]
    cgap = results["cgap"]

    print("\n" + "=" * 82)
    print(f"{'EMPIRICAL COMPARISON: BASELINE vs CGAP-GROUNDED MONOLOGUE':^82}")
    print("=" * 82)
    print(f"{'Metric':<34} | {'Baseline (Pre-CGAP)':<20} | {'Post-CGAP (ADR-14)':<20}")
    print("-" * 82)
    print(
        f"{'Story Coverage Rate (%)':<34} | {avg(base, 'coverage_pct'):>18.1f}% | {avg(cgap, 'coverage_pct'):>18.1f}%"
    )
    print(
        f"{'Narrative Sequence Adherence (%)':<34} | {pct_true(base, 'is_ordered'):>18.1f}% | {pct_true(cgap, 'is_ordered'):>18.1f}%"
    )
    print(
        f"{'Theatrical Flattery Phrases (avg)':<34} | {avg(base, 'flattery_count'):>19.2f} | {avg(cgap, 'flattery_count'):>19.2f}"
    )
    print(
        f"{'Fabricated Metrics Detected (avg)':<34} | {avg(base, 'fabricated_metrics_count'):>19.2f} | {avg(cgap, 'fabricated_metrics_count'):>19.2f}"
    )
    print(
        f"{'Deterministic Gate Pass Rate (%)':<34} | {pct_true(base, 'passed_cgap_gate'):>18.1f}% | {pct_true(cgap, 'passed_cgap_gate'):>18.1f}%"
    )
    print(f"{'Generation Latency (avg s)':<34} | {avg(base, 'duration_s'):>18.2f}s | {avg(cgap, 'duration_s'):>18.2f}s")
    print("=" * 82 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Empirical benchmark for CGAP impact")
    parser.add_argument("--runs", type=int, default=2, help="Number of benchmark trials per condition")
    parser.add_argument("--model", type=str, default="phi4-mini:3.8b", help="Ollama model to benchmark")
    args = parser.parse_args()

    results = run_benchmark(model=args.model, runs=args.runs)
    print_comparison_table(results)
