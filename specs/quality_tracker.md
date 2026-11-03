# Quality Tracker & Telemetry Specifications (`TRACK`)

Formal specifications defining pipeline run persistence, per-story scoring, human review storage, and golden dataset promotion.

---

## TRACK-001: SQLite Run & Pipeline Metrics Persistence

When a pipeline execution completes, the system shall record run timing, TTFT, token throughput, failure rates, model metadata, and memory footprints in quality.db.

Acceptance Criteria:
- AC-TRACK-001.1: Persists execution run metadata into the briefing_runs SQLite table with exact timestamps and durations.
- AC-TRACK-001.2: Records per-story domain, summary status, retries, and entailment confidence in story_scores.

---

## TRACK-002: Human Review Submission & Aggregation

When a user submits quality feedback via the dashboard, the system shall record human rating (1-5), review comments, and timestamp in SQLite.

Acceptance Criteria:
- AC-TRACK-002.1: Updates the specified run in briefing_runs with human rating integer and feedback comment string.
- AC-TRACK-002.2: Computes aggregate human satisfaction metrics and average star ratings across reviewed runs.

---

## TRACK-003: Golden Dataset Feedback Promotion

Where a story receives negative human feedback, the system shall support promoting the story into the golden regression test dataset.

Acceptance Criteria:
- AC-TRACK-003.1: Appends the downvoted story and summary text into golden_dataset.json with failure metadata.
- AC-TRACK-003.2: Prevents duplicate promotions of the same story link into the golden dataset.

