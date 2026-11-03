# Model Comparator & Multi-Role Benchmark Specifications (`COMPARE`)

Formal specifications defining multi-role SLM evaluation, role-specific metrics, and Chart.js HTML reporting.

---

## COMPARE-001: Multi-Role Benchmark Execution

When invoked, the system shall evaluate candidate Ollama models across the four specialized pipeline roles: Summarization, Curation, Scriptwriting, and Adversarial Audit.

Acceptance Criteria:
- AC-COMPARE-001.1: Supports CLI filtering by task (all, summarization, curation, script, audit) and models.
- AC-COMPARE-001.2: Measures time-to-first-token, tokens-per-second throughput, and total execution latency per candidate model.

---

## COMPARE-002: Multi-Dimensional Evaluation Scoring

The system shall compute automated quantitative and qualitative metrics per role including ROUGE-L, fact overlap, Pydantic schema validation, and TPR/TNR.

Acceptance Criteria:
- AC-COMPARE-002.1: Computes summarization ROUGE-L scores and direct quote factual overlap.
- AC-COMPARE-002.2: Computes adversarial audit True Positive Rate on injected poisoned facts versus True Negative Rate on clean summaries.

---

## COMPARE-003: Interactive HTML Report Generation

The system shall compile benchmark results into an interactive HTML report with Chart.js visualizations and render terminal summary tables.

Acceptance Criteria:
- AC-COMPARE-003.1: Emits an interactive dark-theme HTML report with Chart.js bar and line charts via save_html.py.
- AC-COMPARE-003.2: Renders comparative model ranking tables and throughput summaries in the terminal via rich.
