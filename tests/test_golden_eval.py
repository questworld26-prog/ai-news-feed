"""
Pytest test suite for Golden Dataset evaluation harness.
Tests Layer 1 (Regex & Structure), Layer 2 (HHH Guardrails & 1-5 Rubric Matrix), and Layer 3 (LLM-as-a-Judge Pass Rate & Multi-Run).
"""

import json
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from model_eval.evaluator import (
    evaluate_hhh_guardrails,
    evaluate_regex_rules,
    evaluate_rubrics,
    print_evaluation_report,
    run_full_evaluation,
)
from validator import validate_story


@pytest.fixture
def sample_story():
    return {
        "title": "vLLM 0.7.0 Released with Chunked Prefill",
        "summary": "vLLM team announced version 0.7.0 featuring chunked prefill enabled by default, reducing TTFT by up to 3x on Llama 3 70B workloads.",
        "link": "https://github.com/vllm-project/vllm/releases/tag/v0.7.0",
        "source": "Hacker News (MLOps)",
    }


# [verifies: EVAL-001/AC-EVAL-001.1]
def test_evaluate_regex_rules_valid_format(sample_story):
    valid_digest = (
        "## [vLLM 0.7.0 Released with Chunked Prefill](https://github.com/vllm-project/vllm/releases/tag/v0.7.0)\n\n"
        "vLLM 0.7.0 introduces chunked prefill by default, improving TTFT performance by 3x on Llama 3 70B."
    )
    ok, errors = evaluate_regex_rules(valid_digest, sample_story)
    assert ok is True
    assert len(errors) == 0


# [verifies: EVAL-001/AC-EVAL-001.2]
def test_evaluate_regex_rules_catches_bare_url_and_bad_header(sample_story):
    bad_digest = (
        "### vLLM 0.7.0 Released with Chunked Prefill\n"
        "Check out https://github.com/vllm-project/vllm/releases/tag/v0.7.0 for more details."
    )
    ok, errors = evaluate_regex_rules(bad_digest, sample_story)
    assert ok is False
    assert any("Header does not match" in e for e in errors)
    assert any("Bare URL found" in e for e in errors)


# [verifies: EVAL-002/AC-EVAL-002.1]
def test_evaluate_hhh_guardrails_honest_pass(sample_story):
    valid_digest = (
        "## [vLLM 0.7.0 Released with Chunked Prefill](https://github.com/vllm-project/vllm/releases/tag/v0.7.0)\n\n"
        "vLLM 0.7.0 introduces chunked prefill by default, improving TTFT performance by 3x on Llama 3 70B."
    )
    verdict = evaluate_hhh_guardrails(valid_digest, sample_story)
    assert verdict.passed is True
    assert verdict.honest_pass is True
    assert verdict.helpful_pass is True
    assert verdict.harmless_pass is True


# [verifies: EVAL-002/AC-EVAL-002.2]
def test_evaluate_hhh_guardrails_catches_fabrication_and_hype(sample_story):
    hallucinated_digest = (
        "## [vLLM 0.7.0 Released with Chunked Prefill](https://github.com/vllm-project/vllm/releases/tag/v0.7.0)\n\n"
        "vLLM 0.7.0 achieves a guaranteed AGI benchmark score of 99.9% with 5000 GPU nodes."
    )
    verdict = evaluate_hhh_guardrails(hallucinated_digest, sample_story)
    assert verdict.passed is False
    assert verdict.honest_pass is False or verdict.harmless_pass is False


# [verifies: EVAL-002/AC-EVAL-002.1]
def test_evaluate_rubrics_1_to_5_scoring(sample_story):
    valid_digest = (
        "## [vLLM 0.7.0 Released with Chunked Prefill](https://github.com/vllm-project/vllm/releases/tag/v0.7.0)\n\n"
        "vLLM team announced version 0.7.0 featuring chunked prefill enabled by default, reducing TTFT by up to 3x on Llama 3 70B workloads."
    )
    rubric = evaluate_rubrics(valid_digest, sample_story)
    assert rubric.honest_score >= 4.0
    assert rubric.helpful_score == 5.0
    assert rubric.harmless_score == 5.0
    assert rubric.average_score >= 4.5


# [verifies: EVAL-003/AC-EVAL-003.1]
def test_run_full_evaluation_multi_run(monkeypatch):
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"

    # Mock requests to return LLM pass for test verification
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": json.dumps({"pass": True, "reasoning": "Factual and supported."})}

    import requests

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())

    dummy_config = {
        "llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"},
        "laya": {"enabled": False},
    }
    report = run_full_evaluation(fixtures_path, dummy_config, eval_runs=3)
    print_evaluation_report(report)

    assert report.total_cases == 30
    assert report.overall_pass_rate == 1.0
    assert report.mean_rubric_score >= 4.0
    assert len(report.multi_run_summary) == report.total_cases
    for mr in report.multi_run_summary:
        assert mr.total_runs == 3
        assert mr.passed_runs == 3
        assert mr.pass_rate == 1.0
        assert mr.pass_at_k is True
        assert mr.pass_pow_k is True
        assert mr.consistency_gap == 0.0
        assert mr.is_unstable is False

    assert report.overall_pass_pow_k == 1.0
    assert report.mean_consistency_gap == 0.0


# [verifies: EVAL-003/AC-EVAL-003.2]
def test_golden_dataset_negative_traps_are_rejected():
    """Verify that negative traps with fabricated numbers or entities are caught by guardrails."""
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"
    with open(fixtures_path, encoding="utf-8") as f:
        cases = json.load(f)

    traps = [c for c in cases if c.get("is_negative_trap")]
    assert len(traps) >= 8

    dummy_config = {"llm": {"model": "phi4-mini:3.8b"}, "laya": {"enabled": False}}

    for trap in traps:
        story = trap["story"]
        digest = trap["digest_text"]
        ok, errors = evaluate_regex_rules(digest, story)
        assert ok is True  # Header is well formatted

        # But factual guardrail / judge MUST reject it
        validation_res = validate_story(story, digest, dummy_config, run_llm_check=False)
        assert validation_res.passed is False
        assert len(validation_res.fabrication_warnings) > 0


# [verifies: EVAL-003/AC-EVAL-003.2]
def test_golden_dataset_adversarial_probes_are_flagged():
    """Verify that adversarial attacks, link hijacks, and XSS script tags are caught by structural or guardrail checks."""
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"
    with open(fixtures_path, encoding="utf-8") as f:
        cases = json.load(f)

    adversarial_cases = [c for c in cases if c.get("is_adversarial")]
    assert len(adversarial_cases) >= 5

    dummy_config = {"llm": {"model": "phi4-mini:3.8b"}, "laya": {"enabled": False}}

    for case in adversarial_cases:
        story = case["story"]
        digest = case.get("digest_text", f"## [{story['title']}]({story['link']})\n\n{story['summary']}")
        custom_regex = case.get("required_regex", [])
        regex_ok, regex_errors = evaluate_regex_rules(digest, story, custom_regex)
        hhh = evaluate_hhh_guardrails(digest, story)
        validation_res = validate_story(story, digest, dummy_config, run_llm_check=False)

        # Defense-in-depth: AT LEAST one defensive layer must flag/reject the adversarial probe
        adversarial_caught = (not regex_ok) or (not hhh.passed) or (not validation_res.passed)
        assert adversarial_caught is True, f"Adversarial probe {case['id']} escaped all security gates!"


# [verifies: EVAL-003/AC-EVAL-003.2]
def test_golden_dataset_difficult_and_boundary_cases_pass_factuality():
    """Verify that difficult technical cases and boundary cases pass formatting and guardrails without false positives."""
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"
    with open(fixtures_path, encoding="utf-8") as f:
        cases = json.load(f)

    complex_cases = [c for c in cases if c.get("type") in {"difficult", "boundary"}]
    assert len(complex_cases) >= 10

    dummy_config = {"llm": {"model": "phi4-mini:3.8b"}, "laya": {"enabled": False}}

    for case in complex_cases:
        story = case["story"]
        digest = f"## [{story['title']}]({story['link']})\n\n{story['summary']}"
        custom_regex = case.get("required_regex", [])

        regex_ok, regex_errors = evaluate_regex_rules(digest, story, custom_regex)
        assert regex_ok is True, f"Failed regex check for {case['id']}: {regex_errors}"

        hhh = evaluate_hhh_guardrails(digest, story)
        assert hhh.passed is True, f"Failed HHH guardrails for {case['id']}: {hhh}"

        validation_res = validate_story(story, digest, dummy_config, run_llm_check=False)
        assert validation_res.passed is True, f"False positive in {case['id']}: {validation_res.fabrication_warnings}"
