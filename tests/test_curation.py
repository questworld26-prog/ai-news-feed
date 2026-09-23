"""
Unit tests for LLM Curation schema validation, CoT reasoning, and defensive post-processing.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from briefing_generator import CurationResponse, llm_curate_stories
from story import Story


@pytest.fixture
def mock_candidates() -> list[Story]:
    return [
        Story(source="Source A", title="Story 1 Title", link="http://a.com", summary="Summary 1", score=0.9),
        Story(source="Source B", title="Story 2 Title", link="http://b.com", summary="Summary 2", score=0.8),
        Story(source="Source C", title="Story 3 Title", link="http://c.com", summary="Summary 3", score=0.7),
        Story(source="Source D", title="Story 4 Title", link="http://d.com", summary="Summary 4", score=0.6),
        Story(source="Source E", title="Story 5 Title", link="http://e.com", summary="Summary 5", score=0.5),
        Story(source="Source F", title="Story 6 Title", link="http://f.com", summary="Summary 6", score=0.4),
    ]


def test_curation_response_schema_validation():
    data = {
        "evaluation_criteria": "Focus on system efficiency and AI performance optimizations.",
        "justifications": [
            {"index": 1, "reasoning": "High relevance to system serving."},
            {"index": 3, "reasoning": "Substantial benchmark dataset."},
        ],
        "selected": [1, 3],
    }
    model = CurationResponse.model_validate(data)
    assert model.evaluation_criteria.startswith("Focus on")
    assert len(model.justifications) == 2
    assert model.selected == [1, 3]


def test_llm_curate_stories_success_path(mock_candidates, monkeypatch):
    dummy_theme = {"name": "Test Theme", "description": "Test Desc", "tone": "Technical"}
    dummy_config = {
        "llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"},
        "feeds": {"max_stories": 3},
    }

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "response": '{"evaluation_criteria": "Strict technical relevance", "justifications": [{"index": 2, "reasoning": "Strong system architectural focus."}, {"index": 4, "reasoning": "Great open source benchmark."}], "selected": [2, 4, 1]}'
            }

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)

    curated = llm_curate_stories(mock_candidates, dummy_theme, dummy_config)
    assert len(curated) == 3
    assert curated[0].title == "Story 2 Title"
    assert curated[1].title == "Story 4 Title"
    assert curated[2].title == "Story 1 Title"


def test_llm_curate_stories_defensive_padding_and_dedup(mock_candidates, monkeypatch):
    dummy_theme = {"name": "Test Theme", "description": "Test Desc", "tone": "Technical"}
    dummy_config = {
        "llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"},
        "feeds": {"max_stories": 3},
    }

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            # Model returns duplicate index 2 and out-of-bounds index 99, needing score padding
            return {
                "response": '{"evaluation_criteria": "Engineering depth", "justifications": [{"index": 2, "reasoning": "Good paper."}], "selected": [2, 2, 99]}'
            }

    monkeypatch.setattr("requests.post", lambda *args, **kwargs: MockResponse())

    curated = llm_curate_stories(mock_candidates, dummy_theme, dummy_config)
    assert len(curated) == 3
    # Index 2 ("Story 2 Title") is selected first, then padded with highest scored remaining (Story 1 [0.9], Story 3 [0.7])
    assert curated[0].title == "Story 2 Title"
    assert curated[1].title == "Story 1 Title"
    assert curated[2].title == "Story 3 Title"
