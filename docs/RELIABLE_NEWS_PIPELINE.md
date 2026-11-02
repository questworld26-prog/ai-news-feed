# Reliable AI News Briefing Pipeline: Architecture & End-to-End Workflow

An in-depth technical explanation of how the automated daily AI news briefing pipeline ingests, curates, synthesizes, verifies, and delivers zero-hallucination briefings using a **System 1 (LAYA) / System 2 (Ollama SLMs)** cognitive architecture.

---

## 🗺️ Interactive Workflow Diagram

> **Interactive Visualization Available**: Open [docs/pipeline_workflow.html](pipeline_workflow.html) in your browser for the full interactive diagram with theme switching, relationship tracing, and stage focus views.

```
+----------------------------------------------------------------------------------------------------+
|                                    END-TO-END PIPELINE TOPOLOGY                                    |
|                                                                                                    |
|  [Curated RSS Feeds]                                                                               |
|          | (pull XML/Atom)                                                                         |
|  [News Fetcher] ----------> [LAYA Theme Router] (System 1: Signal Tally & Hype Drop)               |
|                                    | (active theme)                                                |
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
|                             [Podcast Script]        [Safe Fallback] (Warning badge + link)         |
|                             (phi4-mini Host)                                                       |
|                                    | (monologue check)                                             |
|                             [Script Auditor] (Hierarchy of Truth: Audited against Validated Story)  |
|                                    | (verified voice)                                              |
|                             [Telegram Bot API] (kokoro-mlx WAV + Formatted Digest)                 |
+----------------------------------------------------------------------------------------------------+
```

---

## 🧠 Cognitive Architecture: System 1 vs. System 2 Division of Labor

The pipeline models human cognitive processing by decoupling fast, intuitive filtering from slow, deliberate reasoning:

| Cognitive Role | Component | Hardware / Runtime | Latency | Primary Responsibilities |
|---|---|---|---|---|
| **System 1 (Intuitive Triage)** | **LAYA** (`convaiinnovations/laya`) | Local CPU (PyTorch) | **< 500ms** | Semantic hype and promotional PR filtering, story-driven dynamic theme routing, candidate pre-ranking, and semantic entailment pre-gating. |
| **System 2 (Deliberate Reasoning)** | **Ollama SLMs** (`phi4-mini:3.8b`, `qwen2.5:3b`) | Apple Silicon Metal GPU | **10–30s** | Chain-of-Thought curation justifications, extractive synthesis, adversarial fact-checking audits, and narrative spoken monologue generation. |
| **Deterministic Pre-Gates** | **Regex & Heuristics** (`validator.py`, `news_fetcher.py`) | Python standard library | **< 1ms** | Numerical verification, unanchored proper-noun extraction, URL leak detection, and fuzzy title deduplication. |

---

## 🔄 End-to-End Stages: "Who Does What"

### Stage 1: Ingestion & Live Enrichment
* **Actor**: [`src/news_fetcher.py`](../src/news_fetcher.py)
* **What Happens**:
  1. Concurrently queries curated RSS feeds (Hacker News AI, PyTorch Blog, Hugging Face, arXiv, Google DeepMind, etc.) using `ThreadPoolExecutor`.
  2. Strips raw HTML and metadata lines (`clean_html_text`).
  3. Applies fuzzy title deduplication via `difflib.SequenceMatcher` to prevent multiple feeds from reporting the identical story.
  4. If an RSS entry has a minimal snippet (<50 characters), triggers an eager HTTP scrape (`fetch_article_excerpt`) to pull clean text paragraphs directly from the article container, ensuring downstream models have sufficient context.

---

### Stage 2: System 1 Semantic Gating & Dynamic Theme Routing
* **Actors**: [`src/laya_decision.py`](../src/laya_decision.py) & [`src/generate_news_digest.py`](../src/generate_news_digest.py)
* **What Happens**:
  1. **Semantic Hype & PR Filter (Option 4)**: Incoming feed entries pass through LAYA's binary quality classifier. Stories classified as corporate marketing fluff, vague buzzwords, or fundraising rounds with $\ge 60\%$ confidence are rejected before expensive downstream processing.
  2. **Story-Driven Dynamic Theme Routing (Option 5)**: When executed in automatic mode, the orchestrator samples breaking headlines across feeds. LAYA evaluates the articles against the 4 configured themes (*Practitioner's Radar*, *Executive Lens*, *Builder's Digest*, *Innovation Scout*) and dynamically selects the theme with the highest story density for today's briefing.

---

### Stage 3: Theme-Based Curation & Pre-Ranking
* **Actors**: [`src/laya_decision.py`](../src/laya_decision.py) & [`src/briefing_generator.py`](../src/briefing_generator.py)
* **What Happens**:
  1. **LAYA Pre-Ranking (Option 1)**: From the 15 candidate stories, LAYA scores each headline and snippet against the active theme's description and tone, pruning the pool down to the top 7 highest-alignment stories in sub-second time.
  2. **SLM CoT Curation**: Ollama (`phi4-mini:3.8b`) receives the compact 7-story shortlist and executes structured Chain-of-Thought curation constrained by the `CurationResponse` Pydantic schema:
     - Formulates explicit evaluation criteria for the theme.
     - Produces technical justifications explaining why each specific story was chosen.
     - Selects the final top 5 stories in priority order.

---

### Stage 4: Factual Synthesis via Extractive Anchoring
* **Actor**: [`src/briefing_generator.py`](../src/briefing_generator.py) (`generate_story_summary`)
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
  5. **Fail-Closed Fallback**:
     - If a story fails validation across all 3 attempts, the pipeline does **not** publish unverified text. It safely falls back to:
       ```markdown
       ⚠️ Failed to generate a reliable summary. Read the original article.
       ```

---

### Stage 6: Podcast Scripting & Hierarchy of Truth Audio Audit
* **Actors**: [`src/briefing_generator.py`](../src/briefing_generator.py) & [`src/notifier.py`](../src/notifier.py)
* **What Happens**:
  1. **Monologue Generation**: The spoken podcast monologue (`phi4-mini:3.8b`) is generated using *only the already-validated story summaries* as ground truth context, completely isolating the scriptwriter from unvetted raw RSS feeds.
  2. **Audio Script Fact-Check Audit**: The candidate monologue is passed to `validate_and_correct_audio_script()`:
     - Audits the audio monologue against the validated summaries. The script is strictly forbidden from introducing outside entities, facts, figures, or URLs not present in the summaries.
     - If the script fails fact-checking, specific feedback reasoning is injected into the prompt and regenerated (up to 3 attempts).
     - If 3 attempts fail, it safely falls back to a deterministic story-by-story script.
  3. **Script Sanitization**: `clean_script_for_audio()` strips raw URLs, brackets, and markdown symbols to guarantee smooth acoustic flow.
  4. **Local TTS Voice Synthesis**: `kokoro-mlx` synthesizes natural 24kHz audio (`bm_george` voice) on Apple Silicon Metal acceleration with automatic text chunking (150 words/chunk).
  5. **Distribution**: Dispatches formatted Markdown summaries and audio WAV files directly to Telegram channels via Telegram Bot API (with automatic 45MB file splitting).

---

## 🛡️ Summary of Reliability Guarantees

| Failure Mode | Prevention Mechanism | Enforcing Component | Stage |
|---|---|---|---|
| **Marketing hype / funding noise** | Semantic zero-shot classification ($P(\text{hype}) \ge 0.60$) | LAYA System 1 | Stage 2 |
| **Weak daily theme alignment** | Dynamic breaking news momentum scoring across themes | LAYA System 1 | Stage 2 |
| **Irrelevant / tangential stories** | Semantic pre-ranking combining theme fit (70%) + recency (30%) | LAYA System 1 | Stage 3 |
| **Subtle hallucinated facts / figures** | Schema-enforced extractive quotes (`direct_quotes`) | `qwen2.5:3b` Pydantic Schema | Stage 4 |
| **Fabricated numbers & statistics** | Exact set intersection check (`detect_fabrications`) | `validator.py` (Regex) | Stage 5 |
| **Invented companies or model names** | Capitalized entity extraction (`detect_unanchored_entities`) | `validator.py` (Regex) | Stage 5 |
| **Semantic drift / contradictory claims** | Dual-tier verification: LAYA entailment + SLM audit @ temp 0.0 | LAYA + `qwen2.5:3b` | Stage 5 |
| **Hallucination persistence** | Feedback injection prompt (`CORRECTION REQUIRED`) with 3x retry | `briefing_generator.py` | Stage 5 |
| **Unverified text reaching users** | Fail-closed fallback badge with original verified article URL | `BriefingOutput` | Stage 5 |
| **Spoken script reciting hallucinated data** | Hierarchy of Truth: Monologue written strictly from validated summaries | `phi4-mini:3.8b` + Audit | Stage 6 |
| **Awkward audio pronunciation / URL leaks** | Pre-TTS script sanitization stripping links, brackets, and paths | `clean_script_for_audio` | Stage 6 |
