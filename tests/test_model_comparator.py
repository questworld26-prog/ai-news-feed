"""
Unit tests for the Multi-Role Model Comparator and Benchmark Harness.
Verifies role evaluation, scoring metrics, and interactive HTML report generation.
"""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from model_eval.model_comparator import (
    build_argument_parser,
    compute_keyword_overlap,
    compute_length_metrics,
    compute_rouge_l,
    detect_hallucinations,
    evaluate_audit_case,
    generate_summary_ollama,
    print_comparison_table,
)
from model_eval.save_html import save_html_dashboard


# [verifies: COMPARE-001/AC-COMPARE-001.1]
def test_cli_argument_parser_options() -> None:
    """Verify CLI parser supports all designated tasks and model list parsing."""
    parser = build_argument_parser()

    # Valid task choices
    for task in ["all", "summarization", "curation", "script", "audit"]:
        args = parser.parse_args(["--task", task, "--models", "llama3.2:3b,phi4-mini:3.8b"])
        assert args.task == task
        assert args.models == "llama3.2:3b,phi4-mini:3.8b"

    # Default values
    default_args = parser.parse_args([])
    assert default_args.task == "all"
    assert default_args.models is None


# [verifies: COMPARE-001/AC-COMPARE-001.2]
def test_generate_summary_ollama_metrics() -> None:
    """Verify generate_summary_ollama measures latency, TTFT, and tokens/sec throughput."""
    mock_response = MagicMock()
    # Simulate streaming Ollama chunks
    lines = [
        b'{"response": "Here is ", "done": false}',
        b'{"response": "a fast briefing.", "done": true, "prompt_eval_count": 12, "eval_count": 5, "eval_duration": 100000000}',
    ]
    mock_response.iter_lines.return_value = lines

    with patch("requests.post", return_value=mock_response):
        summary, latency, ttft, tps, prompt_tokens, eval_tokens = generate_summary_ollama(
            source_text="Test source article text.",
            model="phi4-mini:3.8b",
            prompt_template="{source_text}",
            ollama_url="http://localhost:11434",
            temperature=0.1,
            num_ctx=2048,
            timeout=30,
            stream=True,
        )

        assert summary == "Here is a fast briefing."
        assert latency >= 0.0
        assert ttft >= 0.0
        assert tps == 50.0  # 5 tokens in 0.1s = 50.0 tps
        assert prompt_tokens == 12
        assert eval_tokens == 5


# [verifies: COMPARE-002/AC-COMPARE-002.1]
def test_compute_rouge_l_and_keyword_overlap() -> None:
    """Verify ROUGE-L and keyword overlap metric computations."""
    source_text = "Anthropic released Claude Sonnet featuring state of the art coding benchmarks."
    exact_summary = "Claude Sonnet featuring state of the art coding benchmarks."
    unrelated_summary = "Bananas and apples are popular fruits grown worldwide."

    # ROUGE-L checks
    rouge_high = compute_rouge_l(source_text, exact_summary)
    rouge_low = compute_rouge_l(source_text, unrelated_summary)
    assert rouge_high > 0.8
    assert rouge_low == 0.0

    # Keyword overlap checks
    expected_facts = ["Claude Sonnet", "coding benchmarks", "Anthropic"]
    overlap_high = compute_keyword_overlap(source_text, exact_summary, expected_facts)
    # 2 out of 3 facts ("Claude Sonnet", "coding benchmarks") match
    assert overlap_high == 0.6667

    overlap_zero = compute_keyword_overlap(source_text, unrelated_summary, expected_facts)
    assert overlap_zero == 0.0

    # Length and hallucination checks
    metrics = compute_length_metrics(exact_summary)
    assert metrics["word_count"] == 9
    assert metrics["sentence_count"] == 1

    hallucinations = detect_hallucinations(source_text, "Claude scored 99.9% on tests.")
    assert "99.9" in hallucinations or "99.9%" in hallucinations


# [verifies: COMPARE-002/AC-COMPARE-002.2]
def test_evaluate_audit_case_clean_and_poisoned() -> None:
    """Verify adversarial audit evaluates True Positive and True Negative rates."""
    clean_case = {
        "id": "audit_clean_1",
        "source_text": "Meta released Llama 3 8B model with improved tokenizer.",
        "digest_summary": "Meta introduced the Llama 3 8B model with better tokenization.",
        "is_poisoned": False,
        "expected_verdict": True,
        "injected_hallucinations": [],
    }

    poisoned_case = {
        "id": "audit_poisoned_1",
        "source_text": "Meta released Llama 3 8B model with improved tokenizer.",
        "digest_summary": "Meta released Llama 3 with 500B parameters and acquired Google.",
        "is_poisoned": True,
        "expected_verdict": False,
        "injected_hallucinations": ["acquired Google"],
    }

    dummy_config = {"ollama": {"url": "http://localhost:11434"}}

    with patch(
        "model_eval.model_comparator.get_system_and_ollama_memory_gb",
        return_value={"ollama_process_rss_gb": 1.2, "system_used_ram_gb": 4.5},
    ):
        # Mock Clean summary passing verification (True Negative)
        with patch("model_eval.model_comparator.llm_fact_check", return_value=(True, "Factual summary")):
            res_clean = evaluate_audit_case(clean_case, "phi4-mini:3.8b", dummy_config)
            assert res_clean["is_poisoned"] is False
            assert res_clean["actual_verdict"] is True
            assert res_clean["accurate_verdict"] is True
            assert res_clean["passed"] is True

        # Mock Poisoned summary failing verification (True Positive detection of poison)
        with patch(
            "model_eval.model_comparator.llm_fact_check", return_value=(False, "Fabrication detected: acquired Google")
        ):
            res_poisoned = evaluate_audit_case(poisoned_case, "phi4-mini:3.8b", dummy_config)
            assert res_poisoned["is_poisoned"] is True
            assert res_poisoned["actual_verdict"] is False
            assert res_poisoned["accurate_verdict"] is True
            assert res_poisoned["passed"] is True


# [verifies: COMPARE-003/AC-COMPARE-003.1]
def test_save_html_dashboard_generation(tmp_path: Path) -> None:
    """Verify generation of interactive dark-theme HTML report with Chart.js."""
    all_results = [
        {
            "model": "phi4-mini:3.8b",
            "aggregate": {
                "total_cases": 2,
                "avg_latency": 1.25,
                "avg_ttft": 0.45,
                "avg_throughput_tps": 42.1,
                "overall_score": 8.5,
            },
            "summarization": {"avg_rouge_l": 0.65, "avg_keyword_overlap": 0.8},
            "curation": {"avg_precision": 1.0, "avg_recall": 0.8},
            "script": {"avg_coverage": 1.0, "cleanliness_rate": 1.0},
            "audit": {"audit_accuracy": 1.0, "tpr": 1.0, "tnr": 1.0},
        }
    ]
    config = {
        "output": {"report_dir": "reports"},
        "evaluation": {"eval_runs": 1},
        "judge": {"model": "gemini-2.5-flash"},
    }

    report_path = save_html_dashboard(all_results, config, project_root=tmp_path)
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert 'class="dark"' in content
    assert "chart.js" in content.lower()
    assert "phi4-mini:3.8b" in content


# [verifies: COMPARE-003/AC-COMPARE-003.2]
def test_print_comparison_table() -> None:
    """Verify print_comparison_table formats and renders results table via Rich."""
    all_results = [
        {
            "model": "phi4-mini:3.8b",
            "aggregate": {
                "total_cases": 2,
                "avg_latency": 1.25,
                "avg_ttft": 0.45,
                "avg_throughput_tps": 42.1,
                "overall_score": 8.5,
            },
            "summarization": {"avg_rouge_l": 0.65, "avg_keyword_overlap": 0.8, "heuristic_pass_rate": 1.0},
            "curation": {"avg_precision": 1.0, "avg_recall": 0.8},
            "script": {"avg_coverage": 1.0, "cleanliness_rate": 1.0},
            "audit": {"audit_accuracy": 1.0, "tpr": 1.0, "tnr": 1.0},
        }
    ]
    test_console = Console(file=io.StringIO(), force_terminal=False)
    with patch("model_eval.model_comparator.console", test_console):
        print_comparison_table(all_results)
        output = test_console.file.getvalue()
        assert "Multi-Role Model Evaluation" in output
        assert "phi4-mini:3.8b" in output
