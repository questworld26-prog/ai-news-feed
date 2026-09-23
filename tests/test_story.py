"""
Unit tests for Story dataclass.
"""

from datetime import UTC, datetime
import pytest

from story import Story


def test_story_init_defaults():
    s = Story(
        source="Test Source",
        title="Test Story Title",
        link="https://example.com/story",
        summary="A test summary of the story.",
    )
    assert s.source == "Test Source"
    assert s.title == "Test Story Title"
    assert s.link == "https://example.com/story"
    assert s.summary == "A test summary of the story."
    assert s.points == 0
    assert s.score == 0.0
    assert s.pub_dt is None
    assert s.validated_summary is None


def test_story_to_dict_and_from_dict():
    now = datetime.now(UTC)
    s1 = Story(
        source="Hacker News",
        title="vLLM serving 2.0",
        link="https://example.com/vllm",
        summary="In-depth breakdown of high-throughput LLM serving.",
        pub_dt=now,
        points=150,
        score=0.85,
        validated_summary="High-throughput LLM serving released.",
        extra_metadata={"category": "AI"},
    )
    d = s1.to_dict()
    assert d["source"] == "Hacker News"
    assert d["title"] == "vLLM serving 2.0"
    assert d["points"] == 150
    assert d["score"] == 0.85

    s2 = Story.from_dict(d)
    assert s2.source == s1.source
    assert s2.title == s1.title
    assert s2.link == s1.link
    assert s2.summary == s1.summary
    assert s2.pub_dt == s1.pub_dt
    assert s2.points == s1.points
    assert s2.score == s1.score
    assert s2.validated_summary == s1.validated_summary
    assert s2.extra_metadata == s1.extra_metadata


def test_story_to_prompt_context():
    s = Story(
        source="GitHub Trending",
        title="Awesome AI Library",
        link="https://github.com/example/awesome-ai",
        summary="Curated list of AI frameworks and tools.",
        points=42,
    )
    prompt_str = s.to_prompt_context(idx=1, max_summary_chars=100)
    assert "1. [GitHub Trending] Awesome AI Library" in prompt_str
    assert "Link: https://github.com/example/awesome-ai" in prompt_str
    assert "Points: 42" in prompt_str
    assert "Summary: Curated list of AI frameworks and tools." in prompt_str


def test_story_to_structured_prompt_dict():
    s = Story(
        source="TechCrunch",
        title="New Model Released",
        link="https://techcrunch.com/model",
        summary="Open weights model launched today.",
        points=10,
    )
    struct_dict = s.to_structured_prompt_dict()
    assert struct_dict == {
        "source": "TechCrunch",
        "title": "New Model Released",
        "link": "https://techcrunch.com/model",
        "summary": "Open weights model launched today.",
        "points": 10,
    }
