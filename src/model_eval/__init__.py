"""
Model Evaluation and Benchmarking Package.
Provides multi-role model evaluation, multi-layer golden test evaluation,
lexical and heuristic metrics, and Chart.js HTML reporting.
"""

from __future__ import annotations

from model_eval.evaluator import (
    HHHVerdict,
    RubricScore,
    evaluate_hhh_guardrails,
    evaluate_regex_rules,
    evaluate_rubrics,
    run_full_evaluation,
)
from model_eval.judges import (
    build_gemini_client,
    llm_judge_score,
    llm_judge_script_score,
)
from model_eval.metrics import (
    compute_keyword_overlap,
    compute_length_metrics,
    compute_rouge_l,
    detect_hallucinations,
)
from model_eval.model_comparator import (
    build_argument_parser,
    evaluate_audit_case,
    evaluate_curation_case,
    evaluate_model,
    evaluate_script_case,
    evaluate_summarization_case,
    generate_summary_ollama,
    print_comparison_table,
    save_markdown_report,
)
from model_eval.save_html import save_html_dashboard

__all__ = [
    "HHHVerdict",
    "RubricScore",
    "build_argument_parser",
    "build_gemini_client",
    "compute_keyword_overlap",
    "compute_length_metrics",
    "compute_rouge_l",
    "detect_hallucinations",
    "evaluate_audit_case",
    "evaluate_curation_case",
    "evaluate_hhh_guardrails",
    "evaluate_model",
    "evaluate_regex_rules",
    "evaluate_rubrics",
    "evaluate_script_case",
    "evaluate_summarization_case",
    "generate_summary_ollama",
    "llm_judge_score",
    "llm_judge_script_score",
    "print_comparison_table",
    "run_full_evaluation",
    "save_html_dashboard",
    "save_markdown_report",
]
