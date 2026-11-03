# Golden Dataset & Multi-Layer Evaluation Harness Specifications (`evaluator.py`)

Formal EARS specifications for the 3-layer offline evaluation harness: structural regex/link checks, HHH (Helpful, Honest, Harmless) guardrails with 1–5 rubrics, and multi-run Consistency Gap (`Mean@K` vs `Pass^K`) benchmarking.

---

## EVAL-001: Structural Link Hygiene & Regex Verification (Layer 1)

When evaluating a generated digest summary against a ground-truth story, the system shall verify that the summary contains a properly formatted Markdown title link (`## [Title](URL)`), contains zero bare unbracketed HTTP/HTTPS URLs, and satisfies any case-specific `required_regex` patterns.

Acceptance Criteria:
- AC-EVAL-001.1: Summaries matching `## [Title](URL)` with no bare URLs return `(True, [])` from `evaluate_regex_rules`.
- AC-EVAL-001.2: Summaries missing the Markdown header link or containing bare URLs outside `](...)` return `False` with descriptive error messages.

---

## EVAL-002: HHH Guardrails & 1–5 Rubric Scoring Matrix (Layer 2)

When evaluating a generated digest summary on the Helpful, Honest, and Harmless (HHH) axes, the system shall check factual token overlap and unanchored fabrications (`Honest`), minimum word length and heading structure (`Helpful`), and absence of unsubstantiated hype terms (`Harmless`), computing both a boolean `HHHVerdict` and a 1.0–5.0 `RubricScore`.

Acceptance Criteria:
- AC-EVAL-002.1: Factually grounded summaries with valid structure and zero hype pass all three HHH guardrails (`passed=True`) and achieve an average rubric score $\ge 4.0$.
- AC-EVAL-002.2: Summaries containing fabricated numbers/entities or unsubstantiated hype terms (`"guaranteed agi"`, `"game-changer"`) fail `evaluate_hhh_guardrails` (`passed=False`) and receive penalized rubric scores.

---

## EVAL-003: Multi-Run Golden Dataset Evaluation & Consistency Gap (`Mean@K` vs `Pass^K`)

When running the full evaluation suite across the Golden Dataset over $K$ repeated trials (`run_full_evaluation`), the system shall evaluate positive, difficult, boundary, negative-trap, and adversarial test cases, computing `Mean@K` (`pass_rate`), `Pass^K` (`pass_pow_k`), and the ALTK Consistency Gap (`Mean@K - Pass^K`).

Acceptance Criteria:
- AC-EVAL-003.1: `run_full_evaluation` computes per-case `MultiRunResult` and aggregate `EvaluationReport` metrics (`overall_pass_rate`, `overall_pass_pow_k`, `mean_consistency_gap`, `mean_rubric_score`) across all golden dataset cases.
- AC-EVAL-003.2: Negative hallucination traps (`is_negative_trap`) and adversarial probes (`is_adversarial`) in the golden dataset are deterministically caught and rejected by at least one defense-in-depth layer, while difficult/boundary cases pass without false positives.
