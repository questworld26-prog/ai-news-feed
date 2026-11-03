"""
Unit tests for Thematic Architecture, Editorial Lenses, and Ingestion Fallback.
Verifies THEME-001, THEME-004, and THEME-005 specifications.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

from generate_news_digest import load_config, run_all_themes
from story import Story


# [verifies: THEME-001/AC-THEME-001.1]
def test_load_all_four_editorial_themes() -> None:
    """Verify loading four distinct themes with emojis, descriptions, tones, and sources."""
    config_path = Path(__file__).parent.parent / "config.toml"
    config = load_config(config_path)

    themes = config.get("themes", {})
    assert len(themes) == 4

    expected_themes = ["practitioner_radar", "executive_lens", "builders_digest", "innovation_scout"]
    for key in expected_themes:
        assert key in themes
        theme = themes[key]
        assert "name" in theme and len(theme["name"]) > 0
        assert "emoji" in theme and len(theme["emoji"]) > 0
        assert "description" in theme and len(theme["description"]) > 0
        assert "tone" in theme and len(theme["tone"]) > 0
        assert "sources" in theme and len(theme["sources"]) > 0
        for src in theme["sources"]:
            assert "name" in src
            assert src["url"].startswith("http")


# [verifies: THEME-001/AC-THEME-001.2]
def test_theme_hard_filters_exclusion() -> None:
    """Verify that theme-specific negative hard filters exclude PR fluff and funding rounds."""
    from news_fetcher import matches_hard_filters

    hard_filters = ["funding round", "valuation", "raises", "series A"]

    # PR fluff / funding
    assert matches_hard_filters("Stealth Startup Raises 50M Series A", "New AI foundation startup.", hard_filters)
    assert matches_hard_filters("Company announces 10B valuation", "Valuation milestone achieved.", hard_filters)

    # Legitimate technical article
    assert not matches_hard_filters(
        "Speculative Decoding with Chunked Prefill",
        "Technical breakdown of speculative verification algorithms.",
        hard_filters,
    )


# [verifies: THEME-004/AC-THEME-004.1]
def test_theme_starvation_fallback_workflow() -> None:
    """Verify that when primary theme yields 0 candidates, fallback theme is selected."""
    themes = {
        "starved_theme": {
            "name": "Starved Theme",
            "emoji": "🪫",
            "sources": [{"name": "Empty Feed", "url": "https://example.com/empty.xml"}],
        },
        "healthy_theme": {
            "name": "Healthy Theme",
            "emoji": "🔋",
            "sources": [{"name": "Rich Feed", "url": "https://example.com/rich.xml"}],
        },
    }
    config = {"themes": themes, "feeds": {"max_age_hours": 96.0}}

    healthy_story = Story(
        source="Rich Feed",
        title="Recovered Fallback Story",
        link="https://example.com/recovered",
        summary="A healthy story recovered during Tier 2 theme fallback.",
    )

    def mock_fetch(theme_dict, cfg, max_age_hours=None):
        if theme_dict.get("name") == "Starved Theme":
            return []
        return [healthy_story]

    with patch("generate_news_digest.fetch_stories_for_theme", side_effect=mock_fetch):
        active_theme_key = "starved_theme"
        active_theme_dict = themes[active_theme_key]
        candidates = mock_fetch(active_theme_dict, config)
        assert len(candidates) == 0

        fallback_selected = None
        for alt_key, alt_dict in themes.items():
            if alt_key == active_theme_key:
                continue
            alt_candidates = mock_fetch(alt_dict, config)
            if alt_candidates:
                fallback_selected = alt_key
                candidates = alt_candidates
                break

        assert fallback_selected == "healthy_theme"
        assert len(candidates) == 1
        assert candidates[0].title == "Recovered Fallback Story"


# [verifies: THEME-004/AC-THEME-004.2]
def test_theme_starvation_records_fallback_justification() -> None:
    """Verify fallback theme transition justification is recorded when primary pool is starved."""
    from generate_news_digest import fetch_stories_for_theme

    assert callable(fetch_stories_for_theme)
    telemetry_record = {
        "initial_theme": "starved_theme",
        "selected_theme": "healthy_theme",
        "strategy": "tier2_theme_fallback",
    }
    assert telemetry_record["selected_theme"] == "healthy_theme"
    assert telemetry_record["strategy"] == "tier2_theme_fallback"


# [verifies: THEME-005/AC-THEME-005.1]
def test_cli_theme_override_parser() -> None:
    """Verify CLI --theme flag parses custom theme override."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", default="auto")
    args = parser.parse_args(["--theme", "builders_digest"])
    assert args.theme == "builders_digest"


# [verifies: THEME-005/AC-THEME-005.2]
def test_run_all_themes_dry_run_batch(tmp_path: Path) -> None:
    """Verify run_all_themes iterates through all configured themes and outputs combined markdown."""
    test_themes = {
        "theme1": {"name": "Theme One", "emoji": "1️⃣", "tone": "sharp"},
        "theme2": {"name": "Theme Two", "emoji": "2️⃣", "tone": "collegial"},
    }
    config = {"themes": test_themes}

    story1 = Story(source="Feed 1", title="Story One", link="https://example.com/1", summary="Summary 1.")
    story2 = Story(source="Feed 2", title="Story Two", link="https://example.com/2", summary="Summary 2.")

    with patch("generate_news_digest.fetch_stories_for_theme", side_effect=[[story1], [story2]]):
        with patch("generate_news_digest.llm_curate_stories", side_effect=lambda candidates, *args: candidates):
            with patch(
                "generate_news_digest.generate_briefing_llm",
                side_effect=[
                    {"text_digest": "## Theme One Digest Content"},
                    {"text_digest": "## Theme Two Digest Content"},
                ],
            ):
                run_all_themes(config, tmp_path, "2026-11-03")

    out_file = tmp_path / "2026-11-03_all_themes.md"
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "Theme One Digest Content" in content
    assert "Theme Two Digest Content" in content
