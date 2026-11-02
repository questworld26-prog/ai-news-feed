# AI News Daily Voice Briefing Pipeline 🎙️

An automated, 100% local daily AI news briefing pipeline. Uses a **System 1 (LAYA) / System 2 (Ollama)** cognitive architecture for dynamic theme routing, semantic pre-ranking, and multi-layer anti-hallucination verification, synthesizes natural podcast audio locally (`kokoro-mlx` on Apple Silicon Metal), and dispatches formatted summaries and voice briefings directly to Telegram.

---

## 💡 Why Did I Build This?

Beyond building a bespoke, privacy-first news curator, my primary goal was to master the practical engineering challenges of local agentic AI pipelines on consumer hardware.

Key lessons learned:

1. **Immediate Per-Item Validation**: Never wait for a post-hoc batch check. Catch hallucinations early using deterministic fast-fail gates (regex for entities and numbers), strict **Pydantic** schemas, and inline correction-hint retry loops.
2. **The Nuances of Small Language Models ($\le 4\text{B}$)**: Small models struggle with complex negative constraints ("do not include..."). Shorter prompts with positive constraints, few-shot grounding, and extractive quote anchoring yield far higher factual accuracy.
3. **System 1 / System 2 Cognitive Architecture**: Using a fast, lightweight model (LAYA) for sub-second story pre-ranking, hype filtering, and semantic entailment pre-gating cut expensive Ollama generation passes and total runtime by over 50%.
4. **Multi-Layer Evaluation Harness**: Moving beyond "vibe checks" by implementing an enterprise-grade evaluation pipeline: structural regex verification, 1–5 HHH (Helpful, Honest, Harmless) rubrics, ALTK consistency-gap metrics ($\text{Pass}^K$ vs $\text{Mean@K}$), and regression testing against a curated 30-item golden benchmark dataset.
5. **Local Voice Synthesis**: Generating high-fidelity podcast monologues locally using `kokoro-mlx` on Apple Silicon Metal, along with spoken monologue sanitization (stripping markdown syntax and bare URLs before synthesis).
6. **Automated Telegram Delivery**: Packaging the pipeline end-to-end to dispatch daily markdown briefings and audio notes directly via the Telegram Bot API.

---

## 💻 Command Line Usage & Options

### CLI Usage

```text
usage: uv run python src/generate_news_digest.py [-h] [--config CONFIG] [--dry-run] [--skip-tts]
                                                 [--all-themes] [--theme THEME] [--force] [--clear-history]

AI News Daily Voice Briefing Pipeline

options:
  -h, --help        show this help message and exit
  --config CONFIG   Path to configuration TOML file (default: config.toml)
  --dry-run         Fetch and generate script only; skip TTS synthesis and Telegram dispatch
  --skip-tts        Skip audio synthesis and dispatch only the markdown text digest to Telegram
  --all-themes      Generate full digest for all 4 themes in dry-run mode (saved to output/YYYY-MM-DD_all_themes.md)
  --theme THEME     Specify theme key, 'auto' (LAYA story-driven dynamic routing), or 'random' (default: auto)
  --force           Force execution even on weekends
  --clear-history   Clear the briefed story history database and exit
```

### Testing & Quality Verification

Run the fast-path test suite (68 tests in $< 1\text{s}$ with decoupled mock providers):
```bash
uv run pytest
```

Print the detailed Multi-Layer Evaluation & Reliability Report (Structural Regex, HHH Guardrails, 1–5 Rubrics, and ALTK Consistency Gap tables):
```bash
uv run python src/evaluator.py
# Or view with pytest stdout capture disabled:
uv run pytest -s tests/test_golden_eval.py
```

Run heavy, live neural model integration tests (loads live LAYA / Ollama models into memory):
```bash
uv run pytest -m heavy
```

Compare candidate Ollama models across all 4 pipeline roles (Summarization, Curation, Scriptwriting, Adversarial Audit):
```bash
uv run python eval/model_comparator.py --task all
```

### 📊 Telemetrics & Quality Web Dashboard

Launch the interactive telemetrics webpage server to monitor pipeline execution telemetry, memory footprints, fact-checking pass rates, and submit human quality reviews:

```bash
uv run python eval/serve_dashboard.py
```

Once launched, open your browser at:  
👉 **`http://127.0.0.1:8765/`**

**Options**:
* `--port PORT`: Specify custom port (default: `8765`)
* `--host HOST`: Specify host IP address (default: `127.0.0.1`)

*Note: The server automatically initializes `eval/quality.db` and backfills telemetry metrics from existing briefing files in `output/` if starting fresh.*

---

## 🏛️ System Architecture

The pipeline is built as a modular, local-first, factual-guaranteed system designed to execute with zero paid cloud API dependencies on local hardware (Apple Silicon / Metal), augmented with a **System 1 (LAYA) / System 2 (Ollama)** cognitive architecture.

> 📖 **Full Engineering Guide**: See [docs/RELIABLE_NEWS_PIPELINE.md](docs/RELIABLE_NEWS_PIPELINE.md) for a comprehensive breakdown of each pipeline stage and reliability guarantee.  
> 🗺️ **Interactive Pipeline Diagram**: Open [docs/pipeline_workflow.html](docs/pipeline_workflow.html) in your browser for the full interactive architecture diagram with stage focus views and theme switching.  
> 🧪 **Interactive Testing Diagram**: Open [docs/testing_strategy.html](docs/testing_strategy.html) for the 4-tier testing and evaluation visual architecture.

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion, Routing & Pre-Filtering"]
        A["Curated RSS Feeds (HN, Blogs, arXiv)"] --> B["news_fetcher.py + laya_decision.py"]
        B -->|"LAYA Dynamic Theme Routing<br/>7-Day Recurrence Soft Decay<br/>LAYA Hype Filter + 48h Cutoff"| C["Candidate Pool (15 Stories)"]
    end

    subgraph Curation["2. Two-Stage Theme Curation"]
        C --> D["laya_decision.py (System 1 Pre-Rank)"]
        D -->|"Top 7 Shortlist (<500ms)"| D2["briefing_generator.py (llm_curate_stories)"]
        D2 -->|"Ollama (phi4-mini:3.8b)<br/>CoT Justifications + Pydantic Schema"| E["Selected Stories (Top 5)"]
    end

    subgraph Synthesis["3. Factual Synthesis & Validation Loop"]
        E --> F["Per-Story Summary Generation"]
        F -->|"Ollama (qwen2.5:3b)<br/>Extractive Anchoring (direct_quotes)"| G["Candidate Summary"]
        G --> H{"Deterministic Entity & Metric Pre-Gate<br/>(validator.py)"}
        H -->|"Unanchored Entity/Number"| I["Retry Prompt + Error Feedback<br/>(Max 3 Attempts)"]
        I --> F
        H -->|"Passes Regex Gate"| J{"LAYA Entailment Pre-Gate +<br/>SLM Fact-Check (qwen2.5:3b @ T=0.0)"}
        J -->|"Fails Fact-Check"| I
        J -->|"Passes Fact-Check"| K["Validated Story Summaries"]
        K --> L["Podcast Monologue Generation<br/>(phi4-mini:3.8b)"]
        L --> M{"Hierarchy of Truth Fact-Check<br/>(Audited against Validated Summaries)"}
        M -->|"Passes"| N["BriefingOutput (Standard Markdown + Audio Script)"]
    end

    subgraph Output["4. Local Voice & Distribution"]
        N --> O["notifier.py (VRAM Offload + kokoro-mlx TTS)"]
        O --> P["Local Apple Silicon Audio Synthesis (.wav)"]
        N --> Q["Local Markdown Storage (output/YYYY-MM-DD.md)"]
        P --> R["Telegram Bot API Dispatch (Markdown + Voice WAV)"]
        Q --> R
    end
```

### Core Architectural Pillars

1. **Hierarchy of Truth & Extractive Anchoring**:
   - Small Language Models ($\le 4\text{B}$) are forced to extract verbatim quotes (`direct_quotes: list[str]`) into a strict Pydantic schema before generating summaries.
   - The spoken podcast monologue is generated and fact-checked strictly against the *already-validated summaries* rather than noisy, uncurated raw RSS feeds.
2. **Deterministic Fast-Fail Pre-Gates**:
   - `validator.py` applies deterministic regex matching for unanchored proper nouns, company names, model names (`detect_unanchored_entities`), and numerical fabrications (`detect_fabrications`) in $< 1\text{ms}$ before executing neural checks.
3. **System 1 / System 2 Specialization & Zero-Cost Privacy**:
   - **System 1 Triage & Entailment**: `convaiinnovations/laya` (sub-second theme routing, hype filtering, candidate pre-ranking, and semantic entailment pre-gating).
   - **Curation & Monologue Scripting**: `phi4-mini:3.8b` (structured logic, ranking, and conversational flow).
   - **Extractive Summarization & Fact Auditing**: `qwen2.5:3b` (adversarial precision and factual verification).
   - **TTS Voice Synthesis**: `kokoro-mlx` running on Apple Silicon Metal acceleration after automatic LLM/LAYA memory offloading.
4. **Structured Typed Outputs**:
   - Strongly-typed Pydantic schemas (`CurationResponse`, `StorySummaryResponse`, `FactCheckResponse`) enforce structured JSON schemas via Ollama's native schema format, eliminating JSON syntax errors.
   - `BriefingOutput` enforces strict, standardized Markdown document structures across all output digests.

---

## ⚡ Key Features

- **100% Local & Private Execution**: Runs entirely on Apple Silicon (8 GB M1 budget) with zero recurring paid API subscriptions.
- **Dynamic Story-Driven Theme Routing**: Uses LAYA System 1 to sample breaking headlines across feeds and route daily briefings to the theme with the strongest signal (with recent-theme cooldown rotation):
  - 🧭 **Practitioner's Radar**: Production deployment patterns, MLOps, inference optimization, and engineering architecture.
  - 🏛️ **Executive Lens**: Strategic moves, industry risks, enterprise shifts, safety, and regulation.
  - 🔨 **Builder's Digest**: Concrete tools, open-source libraries, local AI, and developer tooling.
  - 🔭 **Innovation Scout**: Cross-disciplinary AI breakthroughs in science, biology, robotics, and creative domains.
- **Cross-Day Recurrence Suppression & Source Diversity**:
  - Persistent 7-day SQLite sliding-window filter (`story_history.py`) applies a 75% soft score decay to previously briefed stories and tags major evolving stories with `_🔄 Follow-up_` annotations.
  - Enforces a cap of 2 stories per single RSS source per briefing and applies fuzzy title deduplication (`difflib.SequenceMatcher`).
- **Multi-Layer Evaluation & HHH Guardrails**:
  - **Layer 1 (Regex & Structure)**: Enforces heading link syntax `## [Title](URL)` and detects bare URL leaks.
  - **Layer 2 (HHH Guardrails & 1–5 Rubrics)**: Audits outputs on a 1.0–5.0 scale for **Honest** (zero hallucinated figures), **Helpful** (technical depth), and **Harmless** (objective, hype-free tone).
  - **Layer 3 (LLM-as-a-Judge & Consistency Metrics)**: Runs multi-trial evaluations (`eval_runs=N`) over a 30-item golden benchmark, calculating **Mean@K**, **$\text{Pass@K}$**, **$\text{Pass}^K$**, and **ALTK Consistency Gap**.
- **Local TTS & Telegram Dispatch**: Synthesizes natural 24 kHz spoken audio using `kokoro-mlx` and delivers formatted summaries and WAV audio files via Telegram Bot API (handling 45 MB file splitting automatically).

---

## 📂 Project Structure

```text
AI_news_voice_feed/
├── config.toml                   # Central configuration (themes, RSS sources, LAYA, voice, LLM)
├── pyproject.toml                # Project metadata, dependencies & pytest/ruff config
├── ADR.md                        # Architectural Decision Records (ADR-01 through ADR-12)
├── RELEASE.md                    # Semantic Versioning release changelog
├── AGENTS.md                     # Workspace engineering standards & hardware invariants
├── .env.example                  # Environment template for Telegram & offline eval credentials
├── docs/                         # Architecture guides & interactive HTML workflow diagrams
│   ├── RELIABLE_NEWS_PIPELINE.md # Deep-dive stage-by-stage engineering guide
│   ├── pipeline_workflow.html    # Interactive System 1 / System 2 pipeline visualizer
│   └── testing_strategy.html     # Interactive 4-tier testing & evaluation visualizer
├── eval/                         # Quality tracker DB, model comparator & web dashboard
│   ├── eval_config.toml          # Model comparator benchmark configuration
│   ├── golden_dataset.json       # Multi-role benchmark dataset for model comparison
│   ├── model_comparator.py       # Multi-role LLM benchmark harness
│   ├── quality_dashboard.html    # Interactive telemetrics web interface
│   ├── save_html.py              # Chart.js HTML report generator
│   └── serve_dashboard.py        # Web server & REST API for telemetrics dashboard
├── launchd/
│   └── com.aibriefing.daily.plist # macOS LaunchAgent daily schedule configuration
├── src/
│   ├── generate_news_digest.py   # Main CLI entrypoint & phase orchestrator
│   ├── news_fetcher.py           # Concurrent RSS aggregation, scraping, scoring & filtering
│   ├── laya_decision.py          # LAYA System 1 router, pre-ranker, hype filter & entailment gate
│   ├── briefing_generator.py     # LLM story curation, markdown digest & monologue generator
│   ├── model_provider.py         # Centralized LLM provider factory & VRAM manager
│   ├── story.py                  # Structured Story and BriefingOutput data contracts
│   ├── story_history.py          # Persistent sliding-window recurrence & decay manager
│   ├── validator.py              # Anti-hallucination validation & deterministic entity/number gates
│   ├── evaluator.py              # 3-layer evaluation harness (Regex, HHH, Pass^K / Consistency Gap)
│   ├── quality_tracker.py        # SQLite telemetry, quality scoring & HITL benchmark promotion
│   ├── telemetry.py              # Stage latency & RSS memory profiler
│   └── notifier.py               # Local TTS synthesis (kokoro-mlx) & Telegram dispatch
└── tests/                        # 68 fast-path unit tests + 30-case golden benchmark suite
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
- **uv**: Python package and environment manager. Install dependencies:
  ```bash
  uv sync
  ```
- **Ollama**: Running locally with your configured small language models:
  ```bash
  ollama pull phi4-mini:3.8b
  ollama pull qwen2.5:3b
  ```

### 2. Configure Environment Secrets
Copy `.env.example` to `.env` and fill in your Telegram credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
TELEGRAM_CHAT_ID="your_telegram_chat_id_here"
```

### 3. Configuration (`config.toml`)
Customize themes, RSS feed URLs, specialized model tags, and schedule settings in [config.toml](config.toml):
- `schedule.weekdays_only`: Restricts automatic runs to Monday–Friday (default: `true`).
- `feeds.max_stories`: Number of top stories selected per briefing (default: `5`).
- `feeds.candidate_pool_size`: Size of candidate pool collected before curation (default: `15`).
- `llm.curation_model`: Model for theme-based story selection and CoT justification (default: `"phi4-mini:3.8b"`).
- `llm.summary_model`: Model for extractive anchoring and factual distillation (default: `"qwen2.5:3b"`).
- `llm.script_model`: Model for spoken conversational podcast monologue generation (default: `"phi4-mini:3.8b"`).
- `testing.audit_model`: Adversarial model for anti-hallucination fact checking (default: `"qwen2.5:3b"`).

---

## ⏰ Scheduled Automation (`launchd`)

To run the briefing automatically every day on macOS:

1. Update `/Users/YOUR_USERNAME` and the repository path in `launchd/com.aibriefing.daily.plist` to match your local machine.
2. Copy the plist to LaunchAgents:
   ```bash
   cp launchd/com.aibriefing.daily.plist ~/Library/LaunchAgents/
   ```
3. Load and register the service:
   ```bash
   launchctl load -w ~/Library/LaunchAgents/com.aibriefing.daily.plist
   ```
4. Test trigger immediately:
   ```bash
   launchctl start com.aibriefing.daily
   ```
