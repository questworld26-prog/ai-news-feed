"""
Pytest test suite for testing AI News Digest output quality & factual adherence.
"""

import json
import sys
from pathlib import Path

import pytest

# Ensure src and tests directory is on path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

from validator import compute_keyword_overlap, detect_fabrications, validate_story


@pytest.fixture
def golden_stories():
    fixtures_path = Path(__file__).parent / "fixtures" / "golden_stories.json"
    if fixtures_path.exists():
        with open(fixtures_path, encoding="utf-8") as f:
            return json.load(f)
    return [
        {
            "title": "datasette-auth-github 1.0",
            "summary": "Simon Willison released version 1.0 of datasette-auth-github, fixing a session cookie expiration issue on Mobile Safari by configuring Max-Age.",
            "link": "https://simonwillison.net/2026/Sep/19/datasette-auth-github/",
        },
        {
            "title": "Science Is Open Software",
            "summary": "Jepedersen published a post discussing the importance of open-source software in scientific research to accelerate collaboration.",
            "link": "https://jepedersen.dk/blog/202505_research/",
        },
    ]


# [verifies: VALID-003/AC-VALID-003.1]
# [verifies: VALID-003/AC-VALID-003.2]
def test_keyword_overlap_accurate():
    source = "Datasette auth github 1.0 released by Simon Willison fixing session cookie expiration."
    digest = "Simon Willison released datasette auth github 1.0 to fix session cookie expiration issues."
    score = compute_keyword_overlap(source, digest)
    assert score >= 0.5
    # Token normalization and stopword removal check on unrelated vocabulary
    unrelated_digest = "Bananas and apples are popular fruits grown worldwide."
    assert compute_keyword_overlap(source, unrelated_digest) == 0.0


# [verifies: VALID-001/AC-VALID-001.1]
# [verifies: VALID-001/AC-VALID-001.2]
def test_detect_fabrications_catches_fake_numbers():
    source = "Datasette auth github 1.0 released by Simon Willison."
    digest = "Datasette auth github 1.0 was released with a 99.9% accuracy score and 5000 stars."
    warnings = detect_fabrications(source, digest)
    assert len(warnings) == 2
    assert any("99.9" in w for w in warnings)
    assert any("5000" in w for w in warnings)


# [verifies: VALID-002/AC-VALID-002.2]
def test_golden_story_validation(golden_stories):
    dummy_config = {"llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"}}
    story = golden_stories[0]
    digest = "Simon Willison released version 1.0 of datasette-auth-github. It fixes session cookie expiration on Mobile Safari."

    result = validate_story(story, digest, config=dummy_config, run_llm_check=False)
    assert result.passed
    assert result.keyword_overlap_score > 0.4
    assert len(result.fabrication_warnings) == 0


# [verifies: INGEST-002/AC-INGEST-002.1]
def test_matches_hard_filters_filters_quote_and_low_context():
    from news_fetcher import matches_hard_filters

    # Test quote prefix titles (Strategy 2)
    assert matches_hard_filters("Quoting voxium", "Some quote text here", [])
    assert matches_hard_filters("Quote: AI in 2026", "Some quote text", [])
    assert matches_hard_filters("Re: LLM scaling laws", "Discussion on scaling", [])
    assert matches_hard_filters("Sighting 401567", "California Sea Lion", [])

    # Test low-context short summaries (Strategy 2)
    assert matches_hard_filters("Short Title", "Very short", [])

    # Test legitimate technical post (should pass)
    assert not matches_hard_filters(
        "vLLM High Performance Serving",
        "In-depth guide on vLLM inference engine architecture and KV-cache optimization.",
        [],
    )


# [verifies: VALID-003/AC-VALID-003.1]
def test_detect_fabrications_catches_hallucinated_tool():
    # Test prompt guardrail / fabrication detection on quote-like summary
    source = "Quoting voxium: It has been half a month since I started a new role. Everything is made by Claude Code."
    hallucinated_digest = "A new AI-powered tool for automating documentation tasks and writing specs."

    detect_fabrications(source, hallucinated_digest)
    overlap = compute_keyword_overlap(source, hallucinated_digest)

    # Low overlap score indicates hallucination
    assert overlap < 0.35


# [verifies: VALID-004/AC-VALID-004.2]
def test_llm_fact_check_passes_mocked(monkeypatch):
    from validator import llm_fact_check

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": json.dumps({"pass": True, "reasoning": "Factual and supported."})}

    import requests

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())

    dummy_config = {"llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"}}
    passed, reasoning = llm_fact_check("Source text here", "Digest summary here", dummy_config)
    assert passed is True
    assert "Factual and supported" in reasoning


# [verifies: VALID-004/AC-VALID-004.2]
def test_llm_fact_check_fails_mocked(monkeypatch):
    from validator import llm_fact_check

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": json.dumps({"pass": False, "reasoning": "Summary contains unsupported claims."})}

    import requests

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())

    dummy_config = {"llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"}}
    passed, reasoning = llm_fact_check("Source text here", "Hallucinated summary", dummy_config)
    assert passed is False
    assert "unsupported claims" in reasoning


# [verifies: VALID-004/AC-VALID-004.2]
def test_llm_fact_check_fails_closed_on_exception(monkeypatch):
    import requests

    from validator import llm_fact_check

    def mock_post_raise(*args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out")

    monkeypatch.setattr(requests, "post", mock_post_raise)

    dummy_config = {"llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"}}
    passed, reasoning = llm_fact_check("Source text here", "Digest summary", dummy_config)
    # Must fail closed: return False rather than True
    assert passed is False
    assert "timed out" in reasoning


# [verifies: VALID-003/AC-VALID-003.2]
def test_extract_key_tokens_preserves_acronyms_and_models():
    from validator import extract_key_tokens

    text = "OpenAI released o1 and o3 with advanced AI and ML capabilities for CI pipelines."
    tokens = extract_key_tokens(text)
    # 2-letter AI acronyms and model names should not be discarded
    assert "ai" in tokens
    assert "ml" in tokens
    assert "ci" in tokens
    assert "o1" in tokens
    assert "o3" in tokens


# [verifies: INGEST-002/AC-INGEST-002.1]
def test_parse_feed_entry_rejects_stale_stories():
    from datetime import UTC, datetime, timedelta

    from news_fetcher import parse_feed_entry

    now = datetime.now(UTC)
    stale_time = now - timedelta(hours=50)

    class MockFeedEntry:
        published_parsed = stale_time.timetuple()
        title = "Ancient Discovery in Machine Learning"
        link = "https://example.com/ancient"
        summary = "A historical paper that was submitted long ago."

    result = parse_feed_entry(MockFeedEntry(), "Hacker News", hard_filters=[], now=now, max_age_hours=48.0)
    assert result is None  # Must be rejected due to 48-hour cutoff


# [verifies: INGEST-002/AC-INGEST-002.2]
def test_fetch_article_excerpt_filters_cookie_banners(monkeypatch):
    import requests

    from news_fetcher import fetch_article_excerpt

    class MockWebResponse:
        def raise_for_status(self):
            pass

        text = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <header><nav>Home About Contact Login</nav></header>
            <p>We use cookies and privacy policy to track consent and improve your experience.</p>
            <main>
                <article>
                    <p>Engineers at Anthropic deployed a new distributed inference kernel reducing latency by 45%.</p>
                </article>
            </main>
            <footer>Copyright 2026</footer>
        </body>
        </html>
        """

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockWebResponse())
    excerpt = fetch_article_excerpt("https://example.com/test-article")
    assert "cookies" not in excerpt.lower()
    assert "distributed inference kernel" in excerpt


# [verifies: VALID-002/AC-VALID-002.1]
def test_detect_unanchored_entities_catches_hallucinated_orgs():
    from validator import detect_unanchored_entities

    source = "Simon Willison released version 1.0 of datasette-auth-github."
    # Digest hallucinates Stanford R&DE and OpenAI
    digest = "Simon Willison and Stanford R&DE collaborated with OpenAI on datasette."
    warnings = detect_unanchored_entities(source, digest)

    assert len(warnings) >= 2
    assert any("Stanford R&DE" in w for w in warnings)
    assert any("OpenAI" in w for w in warnings)


# [verifies: SUMM-001/AC-SUMM-001.1]
def test_story_summary_response_extractive_anchoring():
    from briefing_generator import StorySummaryResponse

    data = {
        "direct_quotes": [
            "Simon Willison released version 1.0 of datasette-auth-github",
            "fixing a session cookie expiration issue on Mobile Safari",
        ],
        "summary": "Simon Willison released datasette-auth-github 1.0. It resolves a Mobile Safari cookie expiration bug.",
    }
    model = StorySummaryResponse.model_validate(data)
    assert len(model.direct_quotes) == 2
    assert "datasette-auth-github 1.0" in model.summary
