# Release Notes

All notable changes to this project are documented in this file under [Semantic Versioning](https://semver.org/).
Major and minor releases require explicit human sign-off before version increments.

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
