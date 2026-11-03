# Release Notes

All notable changes to this project are documented in this file under [Semantic Versioning](https://semver.org/).
Major and minor releases require explicit human sign-off before version increments.

## [2.3.0] - 2026-11-03

### Added
- **Capability-Grounded Agentic Planning (CGAP) for Level 3 Monologues (ADR-14)**:
  - Implemented the CGAP framework (`src/cgap_planner.py`) inspired by Shrestha et al., 2026 (Washington University in St. Louis, [arXiv:2610.41040](https://arxiv.org/abs/2610.41040)).
  - Compiles verified Level 2 stories into atomic ground capability predicates (`StoryFactPredicate`), extracting authorized metrics, entities, and extractive quotes.
  - Generates symbolic step-by-step execution plans (`build_cgap_script_plan`) passed directly to `phi4-mini:3.8b` to eliminate narrative wandering and dropped stories.
- **Deterministic CGAP Grounding Pre-Gate (`verify_cgap_grounding`)**:
  - Validates complete plan story coverage and monotonic chronological sequence in $< 2\text{ms}$ on CPU.
  - Enforces strict entity and metric grounding against the predicate domain, flagging unanchored numbers or outside hallucinations before expensive neural audits or TTS synthesis.
- **Empirical A/B Benchmark Harness (`eval/benchmark_cgap.py`)**:
  - Repeatable empirical benchmark comparing Baseline (unconstrained) vs CGAP-grounded monologue generation on local hardware.
  - Demonstrates a **45% reduction in generation latency** (56.55s down to 31.08s), **100% elimination of conversational throat-clearing** (3.00 down to 0.00), and **zero ungrounded entity hallucinations**.
- **Evaluation Subsystem Documentation (`eval/README.md`)**:
  - Full architectural documentation of the offline evaluation suite, model comparator, golden benchmark datasets, and interactive telemetrics dashboard server.
- **Unit Test Suite Expansion**:
  - Added 8 dedicated unit tests in `tests/test_cgap_planner.py` covering predicate compilation, plan formatting, sequence verification, and failure feedback hint formatting (bringing the test suite to 81 unit tests passing in $< 1\text{s}$).

---

## [2.2.0] - 2026-11-03

### Added
- **Weekend Ingestion Resilience & Configurable Staleness Window (ADR-13)**: Extended default RSS staleness cutoff to 96 hours (`feeds.max_age_hours`), eliminating the Monday corporate blog starvation issue where Friday posts (~65–75h old) were dropped. Preserves 7-day SQLite deduplication and soft score decay (`ADR-12`) to prevent duplicate coverage.
- **Multi-Tier Orchestrator Ingestion Fallback**: Added Tier 1 in-theme staleness backoff (relaxing to 168h / 7 days if 96h yields zero candidates) and Tier 2 automatic alternative theme fallback before pipeline termination.
- **Aggregator Hardening & Feed Endpoints**: Added configurable HTTP request timeouts (25s) and 3 retries with exponential backoff on HTTP 500/502/504 errors and read timeouts (specifically stabilizing `hnrss.org`). Fixed ArXiv RSS endpoint to active URL (`https://rss.arxiv.org/rss/cs.AI`), replaced dead community feeds with active feeds (`Latent Space AI`, Hacker News Anthropic & Claude query).
- **Multi-Voice Showcase & Kokoro TTS Headroom**: Generated 11 curated local voice samples under `output/voice_samples/` demonstrating the breadth of Kokoro's 54 built-in voices. Added candidate pool evaluation capping in `build_candidate_pool` to avoid unnecessary CPU neural inferences on large RSS feeds.

### Fixed & Hardened
- **Monologue Flattery & Throat-Clearing Removal**: Redesigned spoken monologue prompt to strictly prohibit conversational filler, grandiose adjectives, theatrical preambles ("our journey through the realms", "let's embark on this mission"), and dramatic conclusions ("in conclusion, today's thematic journey", "intellectual voyage").
- **Deterministic Script Sanitizer Gate**: Added regex filters in `clean_script_for_audio()` that scrub boilerplate flattery intros and outro summaries while guaranteeing a crisp opening and concise sign-off ("That is your briefing for today.").
- **Unit Test Coverage**: Added dedicated unit tests in `tests/test_news_fetcher.py` and `tests/test_notifier.py` verifying staleness boundaries, retry backoff, candidate capping, and theatrical flattery stripping.

---

## [2.1.0] - 2026-11-02

### Added
- **Public GitHub Security & Privacy Hardening**: Created `.env.example` template for Telegram and evaluation keys; sanitized all local absolute paths and personal hostnames across LaunchAgent and eval configs.
- **LAYA CPU Memory Headroom Management**: Added `unload_laya_engine()` to reclaim System 1 PyTorch CPU memory (~400–800 MB) alongside Ollama VRAM before starting Metal TTS synthesis.
- **Audio Script Deterministic Pre-Gate**: Integrated deterministic fabrication and number checks into `validate_and_correct_audio_script()` prior to LLM audits.
- **Test Suite Auto-Isolation Fixture**: Added `tests/conftest.py` with an autouse fixture ensuring `ModelProviderFactory` singleton state is pristine across test runs.

### Fixed & Hardened
- **HITL Golden Benchmark Promotion**: Added missing `summary_text` column persistence to SQLite `story_scores` and verified promoted golden dataset entries contain full summary text.
- **Token Redaction in Notifier Logs**: Redacted `TELEGRAM_BOT_TOKEN` in exception logs to prevent credential leakage in automated logs.
- **Scraper Bounds & SSRF Protection**: Enforced strict `http://` / `https://` protocol schemes and capped HTTP response payload decoding at 512 KB in `fetch_article_excerpt()`.
- **Dashboard Static Route Lockdown**: Restricted static file serving in `eval/serve_dashboard.py` to `quality_dashboard.html` and `/reports/`, preventing raw database or configuration downloads over HTTP.
- **Documentation Parity**: Updated `README.md` and `docs/RELIABLE_NEWS_PIPELINE.md` with relative links, refreshed CLI options (`--theme`, `--clear-history`), and synced architecture diagrams.
- **Dead Entrypoint Cleanup**: Removed unused root `main.py` stub in favor of direct execution via `src/generate_news_digest.py`.

---

## [2.0.1] - 2026-10-15

### Fixed & Hardened
- **Tier 1 Test Isolation & Speed**: Decoupled unit tests from live PyTorch weights via deterministic mock fixtures, accelerating test suite execution from 14.5s to 0.5s.
- **Heavy Test Tagging**: Added `@pytest.mark.heavy` and default `-m 'not heavy'` filter to isolate live neural model loads.
- **ADR-02 Safety Invariants Test Suite**: Created `tests/test_briefing_generator.py` testing retry loops, correction hint injection, fail-closed fallback, and Level 3 monologue verification.
- **ALTK Consistency Analysis**: Implemented Pass^K and Consistency Gap metrics in `evaluator.py` to detect prompt instability.
- **30-Item Golden Benchmark**: Expanded test fixture (`tests/fixtures/golden_dataset.json`) across canonical cases, negative hallucination traps, boundary cases, and adversarial probes.
- **HITL Continuous Promotion**: Added `/api/runs/<run_id>/stories/<story_idx>/promote` endpoint and helper to promote human-downvoted failures into golden dataset regression benchmarks.

---

## [2.0.0] - 2026-10-15

### Added
- **LAYA System 1 Decision Engine**: Pre-ranking curation, semantic fact-check pre-gating, hype/PR pre-filtering, and dynamic theme routing.
- **Cross-Day Recurrence Suppression (ADR-12)**: Sliding-window SQLite story history filter with soft score decay to prevent repeating stories over 7 days.
- **Context Hardening & Concurrency (ADR-11)**: Ingestion gate filtering low-context links, parallel synthesis concurrency of 2, and spoken monologue sanitization.
- **Quality Tracker & Telemetrics Web Dashboard**: SQLite-backed quality tracker, real-time memory and stage metrics, and interactive browser dashboard (`eval/serve_dashboard.py`).
- **Small-Model Factual Hardening (ADR-07 & ADR-08)**: Structured Pydantic data contracts (`Story`, `BriefingOutput`), extractive anchoring, and schema-constrained CoT decoding.
- **Always-on Anti-Hallucination Loop (ADR-06)**: Inline per-story validation with retry-with-feedback correction hints and audio script validation.
- **Multi-Layer Evaluation Harness (ADR-03)**: Regex structural verification, HHH guardrails (1–5 rubric scoring), and multi-run Pass@K metrics over golden benchmarks.

---

## [1.2.0] - 2026-09-20

### Changed
- Modularized monolithic `pipeline.py` into single-responsibility modules: `news_fetcher.py`, `briefing_generator.py`, and `notifier.py`.
- Renamed main entry point to `src/generate_news_digest.py`.

---

## [1.1.0] - 2026-09-19

### Added
- Two-stage story selection combining recency/popularity scoring with LLM candidate curation.
- Candidate pool buffer (`candidate_pool_size = 15`) with fallback to score-based selection.
- URL sanitization in audio scripts to strip bracketed domain paths.

---

## [1.0.0] - 2026-09-19

### Added
- Initial release of automated local daily AI news voice briefing pipeline.
- Curated RSS feed aggregation with theme-driven story filtering.
- Local audio synthesis via `kokoro-mlx` and automated Telegram briefing dispatch.
