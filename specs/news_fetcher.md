# RSS Ingestion & Candidate Pool Specifications (`news_fetcher.py`)

Formal EARS specifications for resilient RSS feed fetching, HTML cleaning, staleness filtering, candidate scoring, and source pool health diagnostics.

---

## INGEST-001: Resilient RSS Fetching & Transient Gateway Backoff

When fetching entries from a configured RSS source URL, the system shall sanitize malformed XML entities and retry transient HTTP 5xx (`500`, `502`, `503`, `504`) or network timeout errors up to `max_retries` attempts with linear backoff (`attempt * 2.0` seconds).

Acceptance Criteria:
- AC-INGEST-001.1: Unescaped ampersands in raw RSS XML bytes are converted to `&amp;` before `feedparser` parsing while preserving valid XML entities.
- AC-INGEST-001.2: Transient HTTP 502/504 or connection timeout errors trigger automatic retries with backoff and recover cleanly when the upstream feed responds with HTTP 200.

---

## INGEST-002: Staleness Cutoff, Hard Filtering & Live Excerpt Enrichment

When parsing an individual RSS feed entry, the system shall enforce the configured `max_age_hours` staleness window (default `96.0` hours to accommodate Friday-to-Monday weekend gaps), reject noise matching `hard_filters` or low-context rules (`< 80` characters), and enrich short snippets via live HTML/OpenGraph extraction while stripping cookie consent banners.

Acceptance Criteria:
- AC-INGEST-002.1: Stories within `max_age_hours` (e.g., 72h weekend posts under a 96h window) are accepted, whereas stories older than `max_age_hours` or failing hard/context filters are rejected (`None`).
- AC-INGEST-002.2: Live article excerpt extraction strips `<script>`, `<style>`, `<nav>`, and cookie/privacy consent paragraphs while preserving substantive `<article>`/`<main>`/`<p>` or OpenGraph description text.

---

## INGEST-003: Candidate Pool Scoring, Fuzzy Deduplication & Per-Source Caps

When building the candidate story pool for curation, the system shall score stories by recency and Hacker News popularity, apply soft recurrence decay and optional LAYA hype filtering, deduplicate fuzzy title matches, and enforce `max_per_source` and `candidate_pool_size` bounds.

Acceptance Criteria:
- AC-INGEST-003.1: `build_candidate_pool` caps total returned stories at `candidate_pool_size`, enforces `max_per_source` during the primary pass, and eliminates fuzzy duplicate titles (`SequenceMatcher` ratio $\ge 0.65$).
- AC-INGEST-003.2: Stratified breaking headline sampling (`sample_breaking_headlines`) and theme fetching (`fetch_stories_for_theme`) return deduplicated `Story` objects sorted by relevance score.

---

## INGEST-004: Concurrent Multi-Theme RSS Source Health Audit (`--check-sources`)

Where the `--check-sources` CLI diagnostic is invoked, the system shall concurrently probe all configured RSS feed URLs across every editorial theme and return a structured health report with HTTP status codes, recent story counts within `max_age_hours`, and latencies.

Acceptance Criteria:
- AC-INGEST-004.1: `check_all_sources_health` returns exact `total_sources`, `healthy_sources`, and `failed_sources` counts along with per-theme source diagnostic records.
- AC-INGEST-004.2: Sources returning HTTP 4xx/5xx or connection errors are marked `"status": "FAILED"` with `"stories_count": 0` without crashing the overall health audit.
