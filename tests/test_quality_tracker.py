"""
Unit tests for Quality Tracker module and SQLite metrics logging.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import pytest

from quality_dashboard import (
    QualityTracker,
    extract_domain,
    get_current_git_commit,
    parse_summary_markdown,
)


@pytest.fixture
def temp_tracker(tmp_path):
    db_file = tmp_path / "test_quality.db"
    return QualityTracker(db_file)


def test_extract_domain():
    assert extract_domain("https://www.cnbc.com/2026/09/30/ftc-ai-probe.html") == "cnbc.com"
    assert extract_domain("https://aws.amazon.com/blogs/ml/test") == "aws.amazon.com"
    assert extract_domain("not-a-url") == "unknown"


def test_get_current_git_commit():
    commit = get_current_git_commit()
    assert isinstance(commit, str)
    assert len(commit) >= 4


# [verifies: TRACK-001/AC-TRACK-001.1]
# [verifies: TRACK-001/AC-TRACK-001.2]
def test_log_run_and_get_detail(temp_tracker):
    stories = [
        {
            "title": "Story 1",
            "link": "https://simonwillison.net/2026/1",
            "summary": "This is a good technical summary.",
            "extra_metadata": {"retry_count": 1, "summary_status": "success", "keyword_overlap": 0.65},
        },
        {
            "title": "Story 2",
            "link": "https://example.com/2",
            "summary": "⚠️ Failed to generate a reliable summary. Read the original article.",
            "extra_metadata": {"retry_count": 3, "summary_status": "failed", "keyword_overlap": 0.0},
        },
    ]

    models = {
        "curation": "phi4-mini:3.8b",
        "summary": "qwen2.5:3b",
        "script": "phi4-mini:3.8b",
        "audit": "qwen2.5:3b",
        "theme_router": "convaiinnovations/laya",
        "tts_voice": "bm_george",
    }

    run_id = temp_tracker.log_run(
        run_id="run_20261002_test",
        run_date="2026-10-02",
        git_commit="fc16b29",
        models_used=models,
        theme="practitioner_radar",
        strategy="auto",
        total_duration_s=120.5,
        phase3_duration_s=85.2,
        phase3_mem_delta_mb=-10.5,
        phase3_mem_rss_mb=250.0,
        stories=stories,
        audio_script="Welcome back to our daily briefing. Today we explore tech...",
        audio_script_target=750,
        factcheck_passed=True,
        factcheck_retries=1,
    )

    assert run_id == "run_20261002_test"

    # Verify run detail
    detail = temp_tracker.get_run_detail(run_id)
    assert isinstance(detail, dict)
    assert detail["run_id"] == "run_20261002_test"
    assert detail["git_commit"] == "fc16b29"
    assert detail["total_duration_s"] == 120.5
    assert detail["stories_total"] == 2
    assert detail["stories_failed"] == 1
    assert detail["story_failure_rate"] == 0.5
    assert detail["total_retries"] == 4  # 1 + 3
    assert detail["models_used"]["curation"] == "phi4-mini:3.8b"

    # Verify per-story breakdown
    story_scores = detail["stories"]
    assert len(story_scores) == 2
    assert story_scores[0]["story_domain"] == "simonwillison.net"
    assert story_scores[0]["summary_status"] == "success"
    assert story_scores[1]["summary_status"] == "failed"


# [verifies: TRACK-002/AC-TRACK-002.1]
# [verifies: TRACK-002/AC-TRACK-002.2]
def test_human_review_update(temp_tracker):
    stories = [{"title": "Test Story", "link": "https://test.com", "summary": "Valid summary", "extra_metadata": {}}]
    run_id = temp_tracker.log_run(
        run_id="run_review_test",
        run_date="2026-10-02",
        git_commit="test_sha",
        models_used={},
        theme="builders_digest",
        strategy="random",
        total_duration_s=60.0,
        phase3_duration_s=30.0,
        phase3_mem_delta_mb=0.0,
        phase3_mem_rss_mb=100.0,
        stories=stories,
        audio_script="Test script monologue",
    )

    # Initial state: unreviewed
    detail = temp_tracker.get_run_detail(run_id)
    assert detail["human_rating"] is None

    # Submit review
    updated = temp_tracker.update_review(run_id, rating=5, comment="Spot-on summary, loved the tone!")
    assert updated is True

    detail_after = temp_tracker.get_run_detail(run_id)
    assert detail_after["human_rating"] == 5
    assert detail_after["human_comment"] == "Spot-on summary, loved the tone!"
    assert len(detail_after["reviewed_at"]) >= 19

    # Verify summary aggregate
    summary = temp_tracker.get_summary()
    assert summary["total_runs"] == 1
    assert summary["avg_human_rating"] == 5.0


def test_parse_summary_markdown():
    sample_md = """🧭 **Practitioner's Radar**
_What you need to know to stay credible in AI and prototype smarter_

## [First Test Story](https://github.com/test1)
The team released version 2.0 with improved performance and stability across distributed nodes.

## [Second Test Story](https://example.com/test2)
⚠️ Failed to generate a reliable summary. Read the original article.

## Spoken Audio Script

Welcome back. Today we look through our practitioner lens at distributed nodes and performance.
"""
    stories, script = parse_summary_markdown(sample_md)
    assert len(stories) == 2
    assert stories[0]["title"] == "First Test Story"
    assert stories[0]["extra_metadata"]["summary_status"] == "success"
    assert stories[1]["title"] == "Second Test Story"
    assert stories[1]["extra_metadata"]["summary_status"] == "failed"
    assert "Welcome back" in script


# [verifies: TRACK-003/AC-TRACK-003.1]
# [verifies: TRACK-003/AC-TRACK-003.2]
def test_promote_story_to_golden(temp_tracker, tmp_path):
    """Tier 4 HITL Promotion: Verify promoting a flagged story into a golden benchmark file."""
    import json

    stories = [
        {
            "title": "Poisoned Benchmark Claim",
            "link": "https://example.com/poisoned",
            "summary": "⚠️ Failed to generate a reliable summary. Read the original article.",
            "extra_metadata": {"summary_status": "failed", "retry_count": 3},
        }
    ]
    run_id = temp_tracker.log_run(
        run_id="run_promote_test",
        run_date="2026-10-15",
        git_commit="git123",
        models_used={},
        theme="practitioner_radar",
        strategy="auto",
        total_duration_s=40.0,
        phase3_duration_s=20.0,
        phase3_mem_delta_mb=0.0,
        phase3_mem_rss_mb=50.0,
        stories=stories,
        audio_script="Short script",
    )

    golden_file = tmp_path / "test_golden.json"
    golden_file.write_text("[]", encoding="utf-8")

    result = temp_tracker.promote_story_to_golden(
        run_id=run_id,
        story_idx=0,
        correction="Invented 100x speedup claim",
        notes="Reviewer flagged hallucinated numbers",
        golden_path=golden_file,
    )

    assert result["status"] == "ok"
    assert result["case_id"] == f"hitl_{run_id}_0"
    assert result["total_cases"] == 1

    with open(golden_file, encoding="utf-8") as f:
        promoted = json.load(f)

    assert len(promoted) == 1
    case = promoted[0]
    assert case["id"] == f"hitl_{run_id}_0"
    assert case["is_poisoned"] is True
    assert case["digest_summary"] == stories[0]["summary"]
    assert case["injected_hallucinations"] == ["Invented 100x speedup claim"]
    assert case["promoted_by"] == "human_reviewer"

    # Re-promote same case to verify deduplication
    result_repromoted = temp_tracker.promote_story_to_golden(
        run_id=run_id,
        story_idx=0,
        correction="Updated correction",
        notes="Updated notes",
        golden_path=golden_file,
    )
    assert result_repromoted["status"] == "ok"
    assert result_repromoted["total_cases"] == 1  # Deduplicated: updated in-place
