# Architectural Decision Record (ADR) — AI News Voice Feed

**Date**: 2026-09-22  
**Status**: Accepted  
**Context**: Building a production-grade, privacy-first, automated daily AI news voice briefing pipeline with enterprise quality controls.

---

## 1. Context & Problem Statement

Engineering teams and tech executives require daily briefings on AI developments. However, standard AI news feeds suffer from three major operational issues:
1. **Hype and noise**: Unfiltered RSS feeds contain funding announcements, speculative claims, and quote posts.
2. **LLM Hallucinations**: Standard LLM text summaries risk introducing fabricated figures, tool names, or dates not present in source articles.
3. **Lack of Voice Quality & High Costs**: Cloud-based TTS APIs (e.g. ElevenLabs, OpenAI Audio) incur recurring API costs and data privacy concerns.

**Goal**: Build a 100% local, automated pipeline that aggregates RSS feeds, curates stories based on daily technical themes, generates voice briefings using local LLMs and local TTS, and enforces strict factual guardrails via a multi-layer evaluation harness.

---

## 2. Decision Log & Architectural Choices

### ADR-01: Modular Single-Responsibility Pipeline Architecture
- **Decision**: Modularize into four distinct components:
  - `news_fetcher.py`: RSS aggregation, cleaning, scoring, and fuzzy title deduplication.
  - `briefing_generator.py`: Story curation, markdown digest generation, monologue script generation, and script sanitization.
  - `notifier.py`: Local TTS audio synthesis (`kokoro-mlx`) and Telegram dispatch.
  - `validator.py` & `evaluator.py`: Factual validation, HHH guardrails, and evaluation harness.
- **Rationale**: Isolates domain logic, enabling independent testing and swapping of models or notification channels without touching core pipeline logic.

---

### ADR-02: Three-Stage LLM Pipeline with Immediate Per-Item Factual Validation
- **Decision**: Implement a 3-stage LLM execution flow:
  1. **Stage 1 (Curation)**: Ollama (`phi4-mini:3.8b`) filters candidate stories against theme criteria.
  2. **Stage 2 (Validated Summary & Audio Script Generation)**:
     - **Story Summaries**: Summaries are generated per-story and immediately validated inline against source text before moving to the next item.
     - **Audio Script**: Podcast monologue script (~750 words) is generated and validated against source stories before synthesis.
  3. **Stage 3 (Validation & Correction Loop)**: Always-on anti-hallucination retry loop operating immediately after generation for both story summaries and audio scripts. Failed items are regenerated with fact-checker reasoning injected as correction feedback or fall back gracefully — never silently included.
- **Rationale**: Validating immediately per-item eliminates bulk-digest parsing fragile boundaries, speeds up early failure detection, and extends factual guardrails to spoken audio scripts as well as text digests.

---

### ADR-03: Multi-Layer Evaluation Harness (Regex, HHH Guardrails, LLM-as-a-Judge)
- **Decision**: Build a 3-layer evaluation harness (`src/evaluator.py`) operating over a benchmark **Golden Dataset** (`tests/fixtures/golden_dataset.json`):
  - **Layer 1 (Regex & Structure)**: Enforces markdown link syntax `## [Title](URL)` and detects bare URL leaks.
  - **Layer 2 (HHH Guardrails & 1–5 Rubrics)**: Audits outputs on a 1.0–5.0 scale across **Honest** (factual fidelity), **Helpful** (technical depth), and **Harmless** (objective engineering tone).
  - **Layer 3 (LLM-as-a-Judge & Multi-Run Metrics)**: Runs multi-trial evaluations (`eval_runs=N`) measuring **Pass Rate %** ($\frac{\text{Passed Runs}}{\text{Total Runs}}$) and **Pass@K** metrics.
- **Rationale**: Single-point LLM checks are non-deterministic. Combining deterministic Regex, rule-based HHH guardrails, and multi-run LLM-as-a-Judge provides reproducible, enterprise-grade QA.

---

### ADR-04: Local-First Privacy & Zero Paid API Footprint
- **Decision**: Use local inference via Ollama (`phi4-mini:3.8b` and `qwen2.5:3b`) and local Apple Silicon Metal TTS (`kokoro-mlx`).
- **Rationale**: Ensures zero subscription costs, complete data privacy, offline resilience, and ultra-fast local synthesis.

---

### ADR-05: Strategy 2 Hard Filters & Deduplication
- **Decision**: Filter out quote posts (`Quoting...`, `Re:...`), low-context short entries, and funding/hype keywords (`series A`, `funding round`, `AGI by`). Apply `difflib.SequenceMatcher` to prevent duplicate story coverage across feeds.
- **Rationale**: Guarantees the daily briefing remains strictly technical, high-signal, and hype-free.

---

### ADR-06: Inline Per-Item Summary & Audio Script Fact-Check Loop
- **Decision**: Integrate anti-hallucination validation directly into the generation flow within `briefing_generator.py`:
  1. **Immediate Per-Story Summary Validation (`generate_story_summary_validated`)**:
     - Generates each 2-sentence story summary and validates it immediately against the story's source text using `validate_story()`.
     - **Attempts 2–3**: If validation fails, injects the fact-checker's exact error reasoning into the prompt as a `correction_hint`, strictly instructing the LLM to strip external domain knowledge, ungrounded numbers, or markdown links.
     - **Fallback**: If all 3 attempts fail, replaces the summary with `STORY_FALLBACK_SUMMARY` while retaining the story title and link.
  2. **Audio Script Validation (`validate_and_correct_audio_script`)**:
     - Audits the full spoken monologue script against all source stories using `llm_fact_check()`.
     - Performs up to 3 retry attempts with correction feedback if ungrounded claims or hallucinations are detected in spoken script text.
  3. **Fact-Checker Precision Tuning (`validator.py`)**:
     - Explicitly permits high-level concept paraphrasing while strictly flagging ungrounded numbers, fabricated claims, or markdown link leaks.
- **Key Design Principle**: Inline validation catches hallucinations at the exact point of individual text item creation rather than during post-assembly parsing, ensuring both the text digest and audio podcast monologue meet strict factual standards.
- **Module Boundary**: `generate_story_summary_validated()` and `validate_and_correct_audio_script()` live in `briefing_generator.py` alongside LLM generation logic; `validator.py` remains stateless and decoupled.
- **Rationale**: Running post-hoc regex-splitting over assembled bulk digests was fragile and left spoken audio scripts unvalidated. Inline per-item validation guarantees end-to-end factual accuracy across both text and voice channels.

## 3. Testing & QA Strategy Summary

| Level | Component | Focus | Implementation |
|---|---|---|---|
| **Unit** | Regex & Sanitizer | Structural formatting & link hygiene | `test_notifier.py`, `test_golden_eval.py` |
| **Guardrails** | HHH Audit Engine | Honest, Helpful, Harmless verification | `test_evaluate_hhh_guardrails()` |
| **Integration** | LLM-as-a-Judge | Factual adherence against source text | `test_llm_fact_check_passes_mocked()` |
| **Benchmark** | Golden Dataset | Multi-run Pass Rate % & Pass@K | `test_run_full_evaluation_multi_run()` |
| **End-to-End** | Dry-Run Pipeline | Pipeline orchestration & validation | `generate_news_digest.py --dry-run` |

---

## 4. Consequences & Trade-offs

### Positive Consequences
- **Zero Operating Cost**: Fully local LLM + TTS inference.
- **Zero Hallucination Leakage**: Stage 3 validation with active retry-with-feedback correction prevents hallucinated summaries from reaching end users.
- **Graceful Degradation**: Stories that cannot be reliably summarised still reach readers via their original source link with a clear fallback notice.
- **High Technical Quality**: Hard filters eliminate funding hype and low-value social media quote posts.

### Recognized Trade-offs
- **Hardware Requirement**: Local inference requires Apple Silicon (M-series) or local GPU with $\ge 8\text{GB}$ VRAM/unified memory.
- **Multi-Run Latency**: Running $N=3$ or $N=5$ evaluation runs during full benchmark suites increases evaluation time, mitigated by mock fixtures during CI.
- **Retry Latency**: Each failed story can trigger up to 2 additional LLM generation + validation cycles. For a 5-story briefing with all stories failing all 3 attempts, worst-case overhead is $5 \times 2 = 10$ extra LLM calls. In practice, most stories pass on attempt 1 or 2.
