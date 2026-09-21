"""
Pytest test suite for Golden Dataset evaluation harness.
Tests Layer 1 (Regex & Structure), Layer 2 (HHH Guardrails), and Layer 3 (LLM-as-a-Judge Pass Rate).
"""

import json
from pathlib import Path
import pytest
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from evaluator import (
    evaluate_hhh_guardrails,
    evaluate_regex_rules,
    run_full_evaluation,
)


@pytest.fixture
def sample_story():
    return {
        "title": "vLLM 0.7.0 Released with Chunked Prefill",
        "summary": "vLLM team announced version 0.7.0 featuring chunked prefill enabled by default, reducing TTFT by up to 3x on Llama 3 70B workloads.",
        "link": "https://github.com/vllm-project/vllm/releases/tag/v0.7.0",
        "source": "Hacker News (MLOps)",
    }


def test_evaluate_regex_rules_valid_format(sample_story):
    valid_digest = (
        "## [vLLM 0.7.0 Released with Chunked Prefill](https://github.com/vllm-project/vllm/releases/tag/v0.7.0)\n\n"
        "vLLM 0.7.0 introduces chunked prefill by default, improving TTFT performance by 3x on Llama 3 70B."
    )
    ok, errors = evaluate_regex_rules(valid_digest, sample_story)
    assert ok is True
    assert len(errors) == 0


def test_evaluate_regex_rules_catches_bare_url_and_bad_header(sample_story):
    bad_digest = (
        "### vLLM 0.7.0 Released with Chunked Prefill\n"
        "Check out https://github.com/vllm-project/vllm/releases/tag/v0.7.0 for more details."
    )
    ok, errors = evaluate_regex_rules(bad_digest, sample_story)
    assert ok is False
    assert any("Header does not match" in e for e in errors)
    assert any("Bare URL found" in e for e in errors)


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


def test_evaluate_hhh_guardrails_catches_fabrication_and_hype(sample_story):
    hallucinated_digest = (
        "## [vLLM 0.7.0 Released with Chunked Prefill](https://github.com/vllm-project/vllm/releases/tag/v0.7.0)\n\n"
        "vLLM 0.7.0 achieves a guaranteed AGI benchmark score of 99.9% with 5000 GPU nodes."
    )
    verdict = evaluate_hhh_guardrails(hallucinated_digest, sample_story)
    assert verdict.passed is False
    assert verdict.honest_pass is False or verdict.harmless_pass is False


def test_run_full_evaluation_on_golden_dataset(monkeypatch):
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"

    # Mock requests to return LLM pass for test verification
    class MockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"response": json.dumps({"pass": True, "reasoning": "Factual and supported."})}

    import requests
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())

    dummy_config = {"llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"}}
    report = run_full_evaluation(fixtures_path, dummy_config)

    assert report.total_cases >= 4
    assert report.regex_pass_count == report.total_cases
    assert report.hhh_pass_count == report.total_cases
    assert report.llm_judge_pass_count == report.total_cases
    assert report.overall_pass_rate == 1.0
