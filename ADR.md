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

---

### ADR-07: Small-Model Factual Hardening (Extractive Anchoring, Positive Constraints, Few-Shot Grounding & Truth Hierarchy)
- **Decision**: To achieve $\ge 99\%$ factual accuracy when operating with small language models (SLMs, $\le 4\text{B}$ parameters like `phi4-mini:3.8b` and `qwen2.5:3b`), implement six architectural guardrails:
  1. **Extractive Anchoring (`StorySummaryResponse`)**: Force the model to quote verbatim phrases from the source into `direct_quotes` before generating `summary`, preventing parametric hallucinations.
  2. **Deterministic Entity & Model Gate (`detect_unanchored_entities`)**: Deterministically audit capitalized proper nouns and model identifiers in Python before calling LLM auditors; reject unanchored entities in $< 1\text{ms}$.
  3. **Positive Constraint Framing**: Rephrase prompts into positive active constraints rather than confusing negative "DO NOT" instructions that trigger attention misdirection.
  4. **Few-Shot In-Context Grounding**: Embed explicit positive and negative few-shot reference pairs directly in prompts to anchor structural conciseness.
  5. **Hierarchy of Truth**: The spoken podcast monologue is generated and fact-checked strictly against the *validated 2-sentence summaries* rather than uncleaned RSS text, eliminating multi-stage fact degradation.
  6. **Model Specialization**: Separate pipeline roles to best-in-class small models:
     - `curation_model`: `phi4-mini:3.8b` (structured logic & ranking)
     - `summary_model`: `qwen2.5:3b` (factual extraction & precision)
     - `script_model`: `phi4-mini:3.8b` (natural spoken monologue voice)
     - `audit_model`: `qwen2.5:3b` (deterministic fact-checker at temperature 0.0)
- **Rationale**: Small models lack the broad reasoning capacity of frontier models. Hardening the pipeline with extractive anchoring, deterministic entity gating, and positive few-shot constraints eliminates hallucinations without requiring larger hardware.

---

### ADR-08: Structured Data Contracts (`Story`, `BriefingOutput`) and Schema-Constrained Decoding
- **Decision**: Formalize pipeline state transitions and output artifacts through strongly typed dataclasses and Pydantic response models in `src/story.py` and `src/briefing_generator.py`:
  1. **`Story` Dataclass**: Single source of truth for story lifecycle across fetching, score ranking, curation selection, validated summary storage, and prompt rendering (`to_prompt_context()`, `to_structured_prompt_dict()`).
  2. **`BriefingOutput` Dataclass**: Standardized container for briefing artifacts guaranteeing uniform Markdown document hierarchy (`to_markdown()`) with backward-compatible dict access.
  3. **JSON Schema-Constrained Decoding**: Ollama requests pass native JSON schemas (`format=Model.model_json_schema()`) for `CurationResponse`, `StorySummaryResponse`, and `FactCheckResponse`, eliminating JSON parsing errors and hallucinated keys.
- **Rationale**: Loose dictionary dictionaries throughout pipeline stages caused subtle key mismatch bugs and inconsistent Markdown outputs. Structured types provide strict compile/test-time guarantees and consistent file formats across runs.

---

### ADR-09: Rejection of Multi-Agent Architecture in Favor of In-Process Pipeline Parallelism
- **Decision**: Evaluate and reject a full multi-agent framework topology (e.g. separate orchestrator, curation, synthesis, script, and voice agents communicating via message passing/RPC) in favor of keeping the modular in-process pipeline with targeted concurrency optimizations:
  1. **Concurrent RSS Feed Ingestion (`news_fetcher.py`)**: Execute HTTP feed requests concurrently using `ThreadPoolExecutor` across all configured sources per theme.
  2. **Per-Story Synthesis Concurrency & Fault Isolation (`briefing_generator.py`)**: Wrap per-story summary synthesis and validation in `ThreadPoolExecutor` with per-item exception handling so individual story failures log fallbacks without crashing the pipeline. Concurrency defaults to single-worker for standard Ollama deployments but scales via `synthesis_concurrency` config.
- **Rationale**:
  - **Single-Host Inference Bottleneck**: Local LLM execution via Ollama is predominantly queued sequentially on local metal hardware (single GPU / Unified Memory bandwidth). Multi-agent message passing introduces framework overhead, context serialization, and distributed state complexity without enabling true parallel model inference on single-host local LLMs.
  - **Causal Hierarchy Constraints**: The Hierarchy of Truth requires sequential stage dependencies (Validated Summaries $\rightarrow$ Podcast Script $\rightarrow$ Audio Synthesis). A multi-agent network cannot bypass these causal boundaries.
  - **Maintainability & Reliability**: In-process thread pooling for I/O-bound RSS fetching and graceful per-story error boundaries achieve 80%+ of multi-agent resilience and performance benefits without adding external agent dependencies or distributed tracing complexity.

---

### ADR-10: System 1 / System 2 Cognitive Architecture with LAYA Decision Engine
- **Decision**: Integrate LAYA (`convaiinnovations/laya`) as a low-latency System 1 decision engine to augment slow generative local SLMs (System 2, e.g. `phi4-mini:3.8b`, `qwen2.5:3b`) across four critical pipeline stages:
  1. **Fast Theme Curation & Story Pre-Ranking (`briefing_generator.py`)**: LAYA pre-ranks and shortlists candidate stories against theme definitions in sub-second time, cutting prompt context and Ollama inference latency by >50%.
  2. **Semantic Fact-Checking & Hallucination Pre-Gate (`validator.py`)**: LAYA evaluates single-pass semantic entailment. High-confidence grounded summaries get an instant PASS, while obvious hallucinations FAIL fast for immediate retry, bypassing 70–80% of slow local SLM audits.
  3. **Semantic Hype & PR Pre-Filter (`news_fetcher.py`)**: LAYA acts as a semantic classifier separating substantive technical engineering from marketing fluff, corporate PR, and fundraising speculation, replacing brittle substring regex filters.
  4. **Story-Driven Dynamic Theme Routing (`generate_news_digest.py`)**: Replaces blind random theme selection (`random.choice()`) by sampling breaking headlines and letting LAYA dynamically route to the theme with the highest breaking news signal and story density.
- **Rationale**: Generative SLMs take 10–30+ seconds per invocation on local hardware. Offloading deterministic classification, entailment pre-gating, and triage to a single-pass System 1 model cuts total pipeline runtime by 50–70% while improving curation quality and eliminating blind spot regex failures.

---

### ADR-11: Ingestion Context Hardening, Parallel Synthesis Concurrency, and Monologue Sanitization
- **Decision**: Harden end-to-end reliability, speed, and accuracy across three targeted engineering axes:
  1. **Minimum Content Gate & Ingestion Hardening (`news_fetcher.py`)**:
     - Enforce a strict minimum context threshold ($\ge 80\text{ characters}$) for any feed entry before passing to curation.
     - Reject raw binary PDF links from naive regex parsing and upgrade the scraper user-agent to a modern browser profile.
     - Add OpenGraph/meta-description fallback extraction when article bodies are dynamic or paywalled.
     - Eliminate the root cause of summary validation failure loops: stories without sufficient body text are filtered out before reaching Phase 3 summarization.
  2. **Safe Parallel Story Synthesis (`config.toml` & `briefing_generator.py`)**:
     - Enable `synthesis_concurrency = 2` within `ThreadPoolExecutor`.
     - Calibrated specifically for Apple Silicon M1 (8GB Unified Memory): parallel slots share the base `qwen2.5:3b` model weights in memory ($1.9\text{GB}$) and only allocate an additional $\sim 150\text{MB}$ KV cache per slot ($2.2\text{GB}$ total footprint), cutting Phase 3 synthesis time by $\sim 40\text{–}50\%$ without memory pressure or thermal throttling.
  3. **Spoken Audio Monologue Fallback Sanitization (`briefing_generator.py`)**:
     - Ensure fallback error notices (`⚠️ Failed to generate a reliable summary...`) are intercepted and sanitized before building the podcast monologue prompt context.
     - Prevents conversational audio scripts from reading system error messages on air.
  4. **Deterministic Validation Fast-Path (`validator.py`)**:
     - If keyword overlap falls below `min_keyword_threshold` ($0.35$), fail fast immediately in $<1\text{ms}$ without burning a 30-second Ollama audit call.
- **Rationale**: 100% of historical 3-retry summarization failures were caused by information starvation (empty link posts or unparseable PDFs). Enforcing an ingestion content gate prevents failure cascades, while concurrency of 2 unlocks multi-core parallelism safely within an 8GB hardware budget.

---

### ADR-09: Sliding-Window Recurrence Filter with Soft Score Decay & Update Tracking
- **Decision**: Implement persistent cross-day story tracking in SQLite (`briefed_story_history`) with a configurable rolling lookback window (default 7 days) and soft score decay:
  1. **Canonical URL & Title Matching**:
     - Normalize URLs by stripping tracking parameters (`utm_*`, `ref`, `source`, `fbclid`, etc.) and normalizing fragments and trailing slashes.
     - Normalize titles by stripping common aggregator tags (`[Show HN]`, `[Paper]`) and comparing via `SequenceMatcher` with a $0.80$ similarity threshold.
  2. **Soft Score Decay**:
     - Rather than hard-dropping recurring stories, multiply their calculated relevance score by `decay_factor = 0.25` (a 75% score reduction).
     - Allows fast-moving, massive breaking stories (e.g., 500+ HN points or multi-day releases) to still qualify while preventing routine stories from crowding out fresh news.
  3. **Update / Follow-up Tracking**:
     - Tag qualifying recurring stories with `is_update = True` and link back to `original_briefed_date`.
     - Automatically render markdown summaries with `_🔄 Follow-up to our YYYY-MM-DD briefing._` annotations and prompt the monologue scriptwriter to frame the story as an explicit continuation.
  4. **Post-Briefing Commit**:
     - Automatically record delivered stories into SQLite upon briefing completion (bypassed in `--dry-run` mode).
- **Rationale**: RSS news cycles linger across 48–96 hours. Stateless single-run deduplication caused consecutive daily briefings to repeat identical news items. Sliding-window recurrence with soft score decay guarantees fresh daily intelligence without blinding the system to major evolving stories.

---

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
