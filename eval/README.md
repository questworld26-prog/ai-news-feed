# Evaluation & Quality Benchmarking Suite (`eval/`) 📊

This directory houses the offline evaluation harness, multi-role model benchmarking suite, and real-time telemetry dashboard for the **AI News Voice Feed** pipeline.

It bridges development-time model selection with production runtime observability, ensuring every small model ($\le 4\text{B}$) deployed to local hardware meets strict criteria for factual precision, latency, and memory efficiency.

---

## 🏛️ Architectural Context: Offline Eval vs Local Production

As defined in **ADR-04 (Zero Paid API Invariant)**, the production pipeline runs **100% locally** with zero paid cloud API dependencies (`phi4-mini:3.8b`, `qwen2.5:3b`, `convaiinnovations/laya`, and `kokoro-mlx`).

However, developer evaluations and model selection benefit from objective, external reference grading:
- **Offline Dev Evals**: Use an external LLM-as-a-judge (`gemini-2.5-flash` via `google-genai`) to evaluate candidate local models against ground-truth golden sets. If no API key is provided, the harness automatically falls back to deterministic heuristic grading.
- **Production Execution**: Strictly isolated to local Ollama and MLX runtimes.

---

## 🧩 Components & File Structure

```text
eval/
├── eval_config.toml          # Benchmark configuration, thresholds, targets & judge settings
├── golden_dataset.json       # 30 curated multi-role benchmark cases with ground-truth annotations
├── model_comparator.py       # Multi-role LLM benchmark harness across all 4 pipeline roles
├── benchmark_cgap.py         # Empirical A/B benchmark harness for CGAP (ADR-14) monologue validation
├── quality.db                # SQLite database storing execution telemetrics & human review ratings
├── quality_dashboard.html    # Single-page interactive telemetrics & human evaluation UI
├── save_html.py              # Chart.js visualization generator for benchmark comparison reports
├── serve_dashboard.py        # Lightweight HTTP server & REST JSON API on localhost:8765
└── reports/                  # Generated markdown and HTML benchmark comparison artifacts
```

---

## 🔬 Multi-Role Model Comparator (`model_comparator.py`)

Small language models rarely excel across all tasks simultaneously. The model comparator tests candidate models independently across the four core pipeline roles:

| Role | Target Model | Key Metrics & Targets | Evaluation Method |
| :--- | :--- | :--- | :--- |
| **1. Summarization** | `qwen2.5:3b` | ROUGE-L ($\ge 0.45$), Keyword Overlap ($\ge 0.35$), Latency ($< 3.0$s) | Extractive quote accuracy, numeric fidelity, Gemini judge |
| **2. Curation** | `phi4-mini:3.8b` | Schema Compliance ($100\%$), Precision ($\ge 0.80$), Recall ($\ge 0.80$) | Pydantic JSON schema validation, CoT justification audit |
| **3. Scriptwriting** | `phi4-mini:3.8b` | Coverage ($\ge 75\%$), Zero Leakage (0 bare URLs/markdown), Length ($750 \pm 250$w) | Spoken cadence, grounding against validated summaries |
| **4. Adversarial Audit** | `qwen2.5:3b` | True Positive Rate ($\ge 80\%$), True Negative Rate ($\ge 80\%$) | Synthetic hallucination/poisoning detection safety net |

### CLI Usage

```bash
# Benchmark all candidate models across all four roles:
uv run python eval/model_comparator.py --task all

# Benchmark specific models for summarization only:
uv run python eval/model_comparator.py --task summarization --models qwen2.5:3b,phi4-mini:3.8b

# Target adversarial fact-checking audit capabilities:
uv run python eval/model_comparator.py --task audit --models qwen2.5:3b
```

Benchmark runs generate comprehensive markdown tables and standalone interactive HTML dashboards in `eval/reports/`.

---

## 🔬 Empirical CGAP A/B Benchmark (`benchmark_cgap.py`)

Measures the quantitative impact of **Capability-Grounded Agentic Planning ([ADR-14](../ADR.md))** on Level 3 spoken monologue generation. Compares unconstrained baseline prompts against predicate-compiled symbolic execution plans across identical golden multi-story test cases.

### Evaluated Metrics
- **Generation Latency (s)**: Total wall-clock time for script generation.
- **Monologue Word Density**: Boundedness and conciseness of the spoken text.
- **Theatrical Flattery Rate**: Frequency of forbidden conversational filler ("welcome back", "our journey", "intellectual voyage").
- **Grounded Entity & Metric Violations**: Count of unanchored company names, metrics, or hallucinated facts detected by deterministic pre-gates.
- **Plan Coverage & Sequence Order**: Verification of 100% story inclusion in strictly monotonic order.

### Benchmark Results (Apple Silicon M1, `phi4-mini:3.8b`)

| Metric | Baseline (Pre-CGAP) | Post-CGAP (ADR-14) | Empirical Delta |
| :--- | :---: | :---: | :--- |
| **Generation Latency** | **56.55s** | **31.08s** | ⚡ **45.0% faster execution** |
| **Spoken Word Count** | 539 words | 137 words | 🎯 **$3.9\times$ more concise** |
| **Theatrical Flattery Phrases** | **3.00** / run | **0.00** / run | 🚫 **100% elimination** |
| **Ungrounded Entity Violations** | **21 violations** | **0 violations** | 🛡️ **Zero hallucinated entities** |
| **Plan Story Coverage Rate** | 100.0% | 100.0% | Maintained full story coverage |
| **Sequence Monotonicity** | 100.0% | 100.0% | Strictly ordered step sequence |
| **Pre-Gate Validation Latency** | N/A ($> 15\text{s}$ neural) | **$< 2\text{ms}$** | 🚀 **Sub-millisecond verification** |

### CLI Usage

```bash
# Run 3 trials comparing Baseline vs CGAP on local phi4-mini:3.8b:
uv run python eval/benchmark_cgap.py --runs 3

# Test with a different local model:
uv run python eval/benchmark_cgap.py --model qwen2.5:3b --runs 2
```

---

## 📈 Quality & Telemetrics Dashboard (`serve_dashboard.py`)

A local web interface and REST API to monitor daily execution telemetry, inspect pipeline stage latencies, track fact-checking retry rates, and submit human-in-the-loop (HITL) quality reviews.

### Features
- **Telemetry Trends**: Visualizes stage latency breakdown (Ingestion, Theme Routing, Curation, Summarization, Monologue Scripting, TTS Synthesis).
- **Process Memory Profile**: Tracks Peak RSS and Stage Memory Delta ($\Delta$ MB) across Apple Silicon unified memory.
- **Fact-Checking Pass Rates**: Monitors first-pass validation rates vs retry loops.
- **Human-in-the-Loop Review**: Rate daily briefings on a 1–5 scale with feedback notes, saved directly into `eval/quality.db`.

### Launching the Dashboard

```bash
uv run python eval/serve_dashboard.py
```

Open your browser at: **`http://127.0.0.1:8765/`**

**Options**:
- `--port PORT`: Custom port (default: `8765`).
- `--host HOST`: Custom bind address (default: `127.0.0.1`).

*Note: On startup, `serve_dashboard.py` automatically initializes `quality.db` and backfills telemetry metrics from existing briefing digests in `output/`.*

---

## 🧪 Golden Benchmark Suite (`golden_dataset.json`)

The golden dataset consists of 30 curated test cases across themes, testing edge cases including:
1. **Numeric Precision**: Articles with complex statistics, percentages, and benchmark scores.
2. **Entity Grounding**: Disambiguating similarly named institutions, authors, and AI model variants.
3. **Poisoned / Hallucination Injections**: Synthetic falsehoods inserted into source texts to test whether the adversarial audit layer catches them.

### Running Golden Regression Tests

```bash
# Run fast-path unit verification against the golden set:
uv run pytest tests/test_golden_eval.py

# Print the full Multi-Layer Evaluation Report (Regex, HHH Rubrics, Pass^K Consistency Gaps):
uv run python src/evaluator.py
```

---

## ⚙️ Configuration (`eval_config.toml`)

Key parameters in `eval_config.toml`:
- `judge.model`: Cloud LLM-as-a-judge model (default: `"gemini-2.5-flash"`).
- `ollama.temperature`: Default temperature for benchmark generation (default: `0.1`).
- `ollama.stream`: Enables token streaming to capture **Time-to-First-Token (TTFT)** and generation tokens/sec.
- `evaluation.eval_runs`: Number of repeated evaluation trials per case (for calculating $\text{Pass@K}$ and ALTK consistency gaps).
- `evaluation.target_max_ram_gb`: Hard ceiling for candidate model memory usage (default: `5.0` GB for 8 GB M1 machines).

