"""
Pytest test suite for testing AI News Digest output quality & factual adherence.
"""

import json
from pathlib import Path
import pytest
import sys

# Ensure src and tests directory is on path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

from validator import compute_keyword_overlap, detect_fabrications, validate_story


@pytest.fixture
def golden_stories():
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_stories.json"
    if fixtures_path.exists():
        with open(fixtures_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {
            "title": "datasette-auth-github 1.0",
            "summary": "Simon Willison released version 1.0 of datasette-auth-github, fixing a session cookie expiration issue on Mobile Safari by configuring Max-Age.",
            "link": "https://simonwillison.net/2026/Sep/19/datasette-auth-github/"
        },
        {
            "title": "Science Is Open Software",
            "summary": "Jepedersen published a post discussing the importance of open-source software in scientific research to accelerate collaboration.",
            "link": "https://jepedersen.dk/blog/202505_research/"
        }
    ]


def test_keyword_overlap_accurate():
    source = "Datasette auth github 1.0 released by Simon Willison fixing session cookie expiration."
    digest = "Simon Willison released datasette auth github 1.0 to fix session cookie expiration issues."
    score = compute_keyword_overlap(source, digest)
    assert score >= 0.5


def test_detect_fabrications_catches_fake_numbers():
    source = "Datasette auth github 1.0 released by Simon Willison."
    digest = "Datasette auth github 1.0 was released with a 99.9% accuracy score and 5000 stars."
    warnings = detect_fabrications(source, digest)
    assert len(warnings) >= 1
    assert any("99.9%" in w or "5000" in w for w in warnings)


def test_golden_story_validation(golden_stories):
    dummy_config = {"llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"}}
    story = golden_stories[0]
    digest = "Simon Willison released version 1.0 of datasette-auth-github. It fixes session cookie expiration on Mobile Safari."
    
    result = validate_story(story, digest, config=dummy_config, run_llm_check=False)
    assert result.passed
    assert result.keyword_overlap_score > 0.4
    assert len(result.fabrication_warnings) == 0
