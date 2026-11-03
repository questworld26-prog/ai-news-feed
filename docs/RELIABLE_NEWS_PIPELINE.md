# Reliable AI News Briefing Pipeline: Architecture & End-to-End Workflow

An in-depth technical explanation of how the automated daily AI news briefing pipeline ingests, curates, synthesizes, verifies, and delivers zero-hallucination briefings using a **System 1 (LAYA) / System 2 (Ollama SLMs) & CGAP (Capability-Grounded Agentic Planning)** cognitive architecture.

---

## 🗺️ Interactive Workflow Diagram

> **Interactive Visualization Available**: Open [docs/pipeline_workflow.html](pipeline_workflow.html) in your browser for the full interactive diagram with theme switching, relationship tracing, and stage focus views.

```
+----------------------------------------------------------------------------------------------------+
|                                    END-TO-END PIPELINE TOPOLOGY                                    |
|                                                                                                    |
|  [Curated RSS Feeds] (96h Ingestion Window + 168h Staleness Backoff)                               |
|          | (pull XML/Atom with exponential network backoff)                                        |
|  [News Fetcher] ----------> [LAYA Theme Router] (System 1: Signal Tally & Hype Drop)               |
|  (ADR-12 SQLite 7d dedupe)         | (active theme + Tier 2 fallback)                              |
|                             [LAYA Pre-Ranker] (System 1: Semantic Top-7 Shortlist in <500ms)       |
|                                    | (top 7 candidates)                                            |
|                             [SLM Story Curator] (System 2: phi4-mini CoT Selection of Top 5)        |
|                                    | (curated top 5)                                               |
|                             [Extractive Writer] (System 2: qwen2.5 Verbatim Quotes + 2 Sentences)  |
|                                    | (candidate summary)                                           |
|                             [LAYA & Regex Gate] (Deterministic Entity Match + Semantic Pre-Gate)   |
|                                    | (pre-gate pass)                                               |
|                             [SLM Fact Auditor] (System 2: qwen2.5 Adversarial Audit @ temp 0.0)    |
|                                    |-----------------------+                                       |
|                               (audit pass)             (fail 3x)                                   |
|                                    v                       v                                       |
|                             [CGAP Planner]          [Safe Fallback] (Warning badge + link in MD;   |
|                             (Dual-Grounding)        excluded from audio to prevent deadlock)       |
|                                    | (symbolic plan & prompt)                                      |
|                             [CGAP & Truth Gate] (<2ms CPU Predicate Pre-Gate + Hierarchy of Truth)  |
|                                    | (verified voice script)                                       |
|                             [Telegram Bot API] (kokoro-mlx 24kHz WAV + Formatted Digest)           |
+----------------------------------------------------------------------------------------------------+
```

---

## 🧠 Cognitive Architecture: System 1, System 2 & Symbolic CGAP Planning

The pipeline models human cognitive processing and capability-grounded planning by decoupling fast intuitive filtering, deliberate reasoning, and deterministic symbolic guarantees:

| Cognitive Role | Component | Hardware / Runtime | Latency | Primary Responsibilities |
|---|---|---|---|---|
| **System 1 (Intuitive Triage)** | **LAYA** (`convaiinnovations/laya`) | Local CPU (PyTorch) | **< 500ms** | Semantic hype and promotional PR filtering, story-driven dynamic theme routing, candidate pre-ranking, and semantic entailment pre-gating. |
| **System 2 (Deliberate Reasoning)** | **Ollama SLMs** (`phi4-mini:3.8b`, `qwen2.5:3b`) | Apple Silicon Metal GPU | **10–30s** | Chain-of-Thought curation justifications, extractive synthesis, adversarial fact-checking audits, and narrative spoken monologue generation. |
| **Deterministic Pre-Gates** | **Regex & Heuristics** (`validator.py`, `news_fetcher.py`) | Python standard library | **< 1ms** | Numerical verification, unanchored proper-noun extraction, URL leak detection, and fuzzy title deduplication. |
| **Capability-Grounded Planning** | **CGAP Engine** (`cgap_planner.py`) | Python standard library | **< 2ms** | Atomic predicate compilation, symbolic execution plans, Dual-Grounding prompt synthesis, and deterministic coverage/sequence/grounding pre-gates. |

---

## 🔄 End-to-End Stages: "Who Does What"

### Stage 1: Ingestion, Resiliency & Live Enrichment
* **Actors**: [`src/news_fetcher.py`](../src/news_fetcher.py) & [`src/story_history.py`](../src/story_history.py)
* **What Happens**:
  1. Concurrently queries curated RSS feeds (Hacker News AI, PyTorch Blog, Hugging Face, arXiv, Google DeepMind, etc.) using `ThreadPoolExecutor`.
  2. **Ingestion Window Resiliency (ADR-13)**:
     - Enforces a 96-hour (4-day) freshness window by default (`feeds.max_age_hours = 96.0`), bridging weekend publishing gaps without losing Friday stories.
     - **Staleness Backoff (Tier 1)**: If strict 96h yields zero candidate articles for the target theme, automatically re-queries with a relaxed 168h (7-day) window.
     - **Network Backoff**: Applies exponential backoff (`attempt * 1.5s`, up to 3 retries) for HTTP 500/502/503/504 errors and read timeouts on external aggregators.
  3. **Sliding-Window Recurrence Tracking (ADR-12)**:
     - Cross-references incoming stories against a 7-day rolling SQLite history (`story_history.db`).
     - Suppresses already-briefed URLs and soft-penalizes re-reported headlines to maintain novelty.
  4. **Title Deduplication & Live Article Scraping**:
     - Strips HTML markup (`clean_html_text`) and flags duplicates via `difflib.SequenceMatcher`.
     - If an RSS entry has a minimal snippet (<50 characters), triggers an eager HTTP scrape (`fetch_article_excerpt`) to pull clean text paragraphs directly from the article container, ensuring downstream models have sufficient context.

---

### Stage 2: System 1 Semantic Gating & Dynamic Theme Routing
* **Actors**: [`src/laya_decision.py`](../src/laya_decision.py) & [`src/generate_news_digest.py`](../src/generate_news_digest.py)
* **What Happens**:
  1. **Semantic Hype & PR Filter (Option 4)**: Incoming feed entries pass through LAYA's binary quality classifier. Stories classified as corporate marketing fluff, vague buzzwords, or fundraising rounds with $\ge 60\%$ confidence are rejected before expensive downstream processing.
  2. **Story-Driven Dynamic Theme Routing (Option 5)**: When executed in automatic mode, the orchestrator samples breaking headlines across feeds. LAYA evaluates the articles against configured themes (*Practitioner's Radar*, *Executive Lens*, *Builder's Digest*, *Innovation Scout*) and dynamically selects the theme with highest story density.
  3. **Multi-Tier Theme Fallback (ADR-13 Tier 2)**: If the top-scoring theme has fewer than the required candidate pool (5 stories) even after 168h staleness backoff, the orchestrator automatically falls back to the next highest-scoring theme that meets the quota, preventing empty runs.

---

### Stage 3: Theme-Based Curation & Pre-Ranking
* **Actors**: [`src/laya_decision.py`](../src/laya_decision.py) & [`src/briefing_generator.py`](../src/briefing_generator.py)
* **What Happens**:
  1. **LAYA Pre-Ranking (Option 1)**: From candidate stories, LAYA scores each headline and snippet against the active theme's description and tone, pruning the pool down to the top 7 highest-alignment stories in sub-second time.
  2. **SLM CoT Curation**: Ollama (`phi4-mini:3.8b`) receives the compact 7-story shortlist and executes structured Chain-of-Thought curation constrained by the `CurationResponse` Pydantic schema:
     - Formulates explicit evaluation criteria for the theme.
     - Produces technical justifications explaining why each specific story was chosen.
     - Selects the final top 5 stories in priority order.

---

### Stage 4: Factual Synthesis via Extractive Anchoring
* **Actor**: [`src/briefing_generator.py`](../src/briefing_generator.py) (`generate_story_summary_validated`)
* **What Happens**:
  1. Each of the 5 stories is synthesized individually using `qwen2.5:3b`.
  2. **Extractive Anchoring**: The model is forced by Pydantic schema (`StorySummaryResponse`) to extract 2 to 3 verbatim sentences directly from the source text into `direct_quotes: list[str]` **before** writing the summary.
  3. The summary must consist of exactly 2 concise sentences synthesizing *only* the facts contained in the extracted quotes.
  4. Positive framing constraints strictly restrict vocabulary to entities, benchmarks, and metrics explicitly present in the source article.

---

### Stage 5: Dual-Tier Verification & Anti-Hallucination Gate
* **Actors**: [`src/validator.py`](../src/validator.py) & [`src/laya_decision.py`](../src/laya_decision.py)
* **What Happens**:
  1. **Deterministic Regex Gates (< 1ms)**:
     - `detect_fabrications`: Extracts all numbers, floats, and percentages in the summary and verifies their existence in the source text.
     - `detect_unanchored_entities`: Flags capitalized proper nouns, company names, or model identifiers appearing in the summary that are missing from the source.
     - `compute_keyword_overlap`: Ensures summary keyword token overlap exceeds the configured threshold ($\ge 0.35$).
     - *If any deterministic check fails, the summary fails immediately without calling any SLM.*
  2. **LAYA Semantic Pre-Gate (Option 2)**:
     - Evaluates semantic entailment between source and summary.
     - **Grounded ($\ge 78\%$ confidence)**: **Fast PASS** (bypasses slow local SLM fact-checker).
     - **Hallucinated ($\ge 85\%$ confidence)**: **Fast FAIL** (triggers immediate retry without waiting for SLM).
     - **Ambiguous ($< 78\%$ grounded / $< 85\%$ hallucinated)**: Escalates to the System 2 fact auditor.
  3. **System 2 Adversarial Fact-Checking**:
     - `qwen2.5:3b` at temperature 0.0 audits the claim against the source text with strict CoT verification.
  4. **The 3-Attempt Feedback & Retry Loop**:
     - If validation fails, the exact failure reason (e.g. `Unanchored entity 'Safari' not found in source`) is injected into the regeneration prompt as a `CORRECTION REQUIRED` feedback hint.
  5. **Fail-Closed Fallback & Graceful Degradation (ADR-15)**:
     - If a story fails validation across all 3 attempts, the pipeline does **not** publish unverified text. It safely falls back in Markdown:
       ```markdown
       ⚠️ Failed to generate a reliable summary. Read the original article.
       ```
     - **Audio Story Exclusion**: Failed stories are excluded from `verified_audio_stories` for spoken audio generation. This prevents planner deadlock where the audio presenter is forced to speak about a story it has no verified facts for.

---

### Stage 6: CGAP Monologue Planning, Dual-Grounding & Audio Delivery
* **Actors**: [`src/cgap_planner.py`](../src/cgap_planner.py), [`src/briefing_generator.py`](../src/briefing_generator.py), [`src/notifier.py`](../src/notifier.py)
* **What Happens**:
  1. **Capability-Grounded Agentic Planning (CGAP - ADR-14)**:
     - **Predicate Compilation**: Deterministically compiles validated stories into atomic ground predicates: `StoryFactPredicate(story_id, title, source, summary, direct_quotes, key_entities, metrics)`.
     - **Dual-Grounding Architecture (ADR-15)**: Solves the "Parrot vs. Hallucinator" dilemma:
       - **Core Takeaway Anchor (Level 2)**: The verified, factual claim acts as an immutable factual anchor that the script cannot contradict or wander away from.
       - **Article Context Canvas (Level 1)**: A clean excerpt of the original article body (up to 300 characters, cleanly truncated on sentence boundaries via `extract_clean_sentence_excerpt`) provides engineering mechanisms, problem context, and technical vocabulary for natural conversational flow.
       - Allowed metrics and key entities are combined from both Level 1 and Level 2 into the predicate catalog.
     - **Symbolic Execution Plan**: Compiles an explicit symbolic sequence plan: `Step 0: Intro -> Step 1: CoverStory(1) -> ... -> Step N: SignOff`.
  2. **Plan-Guided Monologue Generation**:
     - `phi4-mini:3.8b` receives the symbolic plan, allowed predicate catalog, and Dual-Grounding prompt to generate a cohesive, engaging podcast monologue.
  3. **Deterministic CGAP Grounding Pre-Gate (<2ms on CPU)**:
     - Verifies 100% story coverage (no omitted stories).
     - Verifies strictly monotonic sequential execution order.
     - Verifies that every number, percentage, and proper noun matches the allowed predicate catalog.
     - Intercepts structural or grounding faults deterministically before invoking neural checkers or TTS.
  4. **Hierarchy of Truth Audio Audit**:
     - `validate_and_correct_audio_script()` verifies the monologue strictly against the validated ground truth.
     - If fact-checking fails, feedback is injected with up to 3 regeneration attempts.
     - **Emergency Fallback Protection**: If regeneration fails, safe fallback generates a deterministic story-by-story script protected by `extract_clean_sentence_excerpt` so it never reads raw truncated sentences or error notices over audio.
  5. **Script Sanitization**: `clean_script_for_audio()` strips raw URLs, markdown, brackets, and code paths for smooth acoustic delivery.
  6. **Local TTS Voice Synthesis**: `kokoro-mlx` synthesizes natural 24kHz audio (`bm_george` voice) on Apple Silicon Metal acceleration with automatic text chunking (150 words/chunk).
  7. **Distribution**: Dispatches formatted Markdown summaries and audio WAV files directly to Telegram channels via Telegram Bot API (with automatic 45MB file splitting).

---

## 🛡️ Summary of Reliability Guarantees

| Failure Mode | Prevention Mechanism | Enforcing Component | Stage |
|---|---|---|---|
| **Weekend publishing lull / starvation** | 96h default ingestion window + 168h staleness backoff | `news_fetcher.py` (ADR-13) | Stage 1 |
| **External aggregator timeouts (5xx)** | Exponential backoff (`attempt * 1.5s`) up to 3 retries | `news_fetcher.py` (ADR-13) | Stage 1 |
| **Duplicate / recurrent stories** | 7-day sliding SQLite history filter + soft score decay | `story_history.py` (ADR-12) | Stage 1 |
| **Marketing hype / funding noise** | Semantic zero-shot classification ($P(\text{hype}) \ge 0.60$) | LAYA System 1 | Stage 2 |
| **Empty daily theme run** | Multi-tier theme fallback to next highest story density | `generate_news_digest.py` (ADR-13) | Stage 2 |
| **Irrelevant / tangential stories** | Semantic pre-ranking combining theme fit (70%) + recency (30%) | LAYA System 1 | Stage 3 |
| **Subtle hallucinated facts / figures** | Schema-enforced extractive quotes (`direct_quotes`) | `qwen2.5:3b` Pydantic Schema | Stage 4 |
| **Fabricated numbers & statistics** | Exact set intersection check (`detect_fabrications`) | `validator.py` (Regex) | Stage 5 |
| **Invented companies or model names** | Capitalized entity extraction (`detect_unanchored_entities`) | `validator.py` (Regex) | Stage 5 |
| **Semantic drift / contradictory claims** | Dual-tier verification: LAYA entailment + SLM audit @ temp 0.0 | LAYA + `qwen2.5:3b` | Stage 5 |
| **Hallucination persistence** | Feedback injection prompt (`CORRECTION REQUIRED`) with 3x retry | `briefing_generator.py` | Stage 5 |
| **Unverified text reaching readers** | Fail-closed fallback badge with original verified article URL | `BriefingOutput` (Markdown) | Stage 5 |
| **Deadlock on failed story in audio** | Graceful degradation: unverified stories excluded from spoken audio | `briefing_generator.py` (ADR-15) | Stage 5 / 6 |
| **Story omission / sequence shuffling** | Capability-Grounded Agentic Planning (CGAP) symbolic plan | `cgap_planner.py` (ADR-14) | Stage 6 |
| **Robotic summary reading in audio** | Dual-Grounding: Core Takeaway Anchor + Article Context Canvas | `cgap_planner.py` (ADR-15) | Stage 6 |
| **Audio script entity / metric injection** | Deterministic CGAP Pre-Gate (<2ms on CPU) | `cgap_planner.py` (ADR-14) | Stage 6 |
| **Mid-sentence audio cutoffs** | Sentence-boundary truncation (`extract_clean_sentence_excerpt`) | `briefing_generator.py` (ADR-15) | Stage 6 |
| **Awkward audio pronunciation / URL leaks** | Pre-TTS script sanitization stripping links, brackets, and paths | `clean_script_for_audio` | Stage 6 |

---

## 🧪 4-Tier Testing & Verification Strategy

The repository enforces a 4-tier testing hierarchy guaranteeing that fast unit tests run in sub-second time while neural reliability is rigorously verified:

```
[ Tier 1: Fast CI (<1s) ]      -->  [ Tier 2: Golden Benchmarks ]  -->  [ Tier 3: ALTK Heavy Eval ]  -->  [ Tier 4: HITL Telemetry ]
84 unit tests in <0.5s              30 seeded scenarios & traps         K=3 Pass^K vs Mean@K (Gap <=0.15) SQLite telemetry & review
Mocked weights + <2ms CGAP          Fail-closed verification            Live LAYA + Ollama models         Downvotes -> regressions
```

* **Tier 1 (Fast CI Gate)**: 84 unit tests executing in **< 0.5s** using mocked model providers and deterministic standard library operations. Includes unit tests for fuzzy deduplication, regex validation, CGAP predicate generation, plan verification, and sentence truncation.
* **Tier 2 (Golden Benchmark & Guardrails)**: 30-item curated golden benchmark dataset (`eval/golden_dataset.json`) evaluating honest, helpful, harmless (HHH) guardrails, numerical precision, and fail-closed fallback behavior.
* **Tier 3 (Heavy Reliability & ALTK Consistency)**: ALTK Evolve-inspired consistency testing running $K=3$ trials per item to track Pass$^K$ vs. Mean@K and ensure non-deterministic drift gap $\le 0.15$ across live neural models (`pytest -m heavy`).
* **Tier 4 (Production Observability & HITL Flywheel)**: Production briefings log execution telemetry, token counts, time-to-first-token (TTFT), and entailment confidence to `quality.db`. Human reviews from the local HITL dashboard (`serve_dashboard.py`) promote downvoted stories directly into golden regression tests.
