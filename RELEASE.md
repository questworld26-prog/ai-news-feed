# Release Notes

All notable changes to this project are documented in this file under [Semantic Versioning](https://semver.org/).
Major and minor releases require explicit human sign-off before version increments.

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
