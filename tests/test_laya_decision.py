"""
Unit tests for LAYA System 1 Decision Engine (Options 1, 2, 4, 5).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from laya_decision import LayaDecisionEngine, get_laya_engine
from story import Story


class MockLayaAgent:
    """Mock LAYA agent providing deterministic System 1 responses for fast-path unit tests."""

    def system_one(self, state: dict, questions: dict) -> dict:
        answers = {}
        if "quality_category" in questions or "content_type" in questions:
            text = f"{state.get('title', '')} {state.get('headline', '')} {state.get('summary', '')}".lower()
            key = "quality_category" if "quality_category" in questions else "content_type"
            if any(k in text for k in ["raises 50m", "stealth ai startup", "proprietary ai vision", "fundraising"]):
                answers[key] = {"choice": "hype", "answer_confidence": 0.95}
            else:
                answers[key] = {"choice": "technical", "answer_confidence": 0.92}

        if "is_grounded" in questions:
            gen = state.get("generated_summary", "").lower()
            if any(k in gen for k in ["100 billion", "quantum computing", "openai partnered with microsoft"]):
                answers["is_grounded"] = {"choice": "hallucinated", "answer_confidence": 0.95}
            else:
                answers["is_grounded"] = {"choice": "grounded", "answer_confidence": 0.94}

        if "theme_fit" in questions:
            headline = state.get("headline", "").lower()
            if "rag" in headline or "fastapi" in headline:
                answers["theme_fit"] = {"choice": "theme_aligned", "answer_confidence": 0.92}
            else:
                answers["theme_fit"] = {"choice": "off_topic", "answer_confidence": 0.88}

        if "theme_match" in questions:
            headline = state.get("headline", "").lower()
            if "vllm" in headline or "triton" in headline:
                answers["theme_match"] = {
                    "choice": "practitioner_radar",
                    "probabilities": {"practitioner_radar": 0.85, "builders_digest": 0.15},
                }
            elif "microservice" in headline:
                answers["theme_match"] = {
                    "choice": "practitioner_radar",
                    "probabilities": {"practitioner_radar": 0.55, "builders_digest": 0.45},
                }
            else:
                answers["theme_match"] = {
                    "choice": "practitioner_radar",
                    "probabilities": {"practitioner_radar": 0.5, "builders_digest": 0.5},
                }
        return {"answers": answers}


@pytest.fixture(autouse=True)
def mock_laya_agent_autouse(monkeypatch, request):
    """Automatically mock LAYA inference for fast-path Tier 1 unit tests."""
    if request.node.get_closest_marker("heavy"):
        return
    mock_agent = MockLayaAgent()
    monkeypatch.setattr(LayaDecisionEngine, "load_agent", lambda self: mock_agent)


# [verifies: THEME-001/AC-THEME-001.2]
def test_laya_filter_hype_technical_vs_fluff():
    """Option 4: Test that LAYA differentiates technical substance from marketing hype."""
    engine = get_laya_engine()

    # Substantive technical story
    is_hype, conf, reason = engine.filter_hype(
        title="vLLM v0.6.0 Released with Speculative Decoding and Chunked Prefill",
        summary="Detailed benchmarks showing 3x throughput improvements on multi-GPU server deployments.",
    )
    assert not is_hype
    assert "technical" in reason.lower()

    # Marketing hype / fundraising
    is_hype_fluff, conf_fluff, reason_fluff = engine.filter_hype(
        title="Excited to announce our new stealth AI startup raises 50M seed valuation from angels",
        summary="Transforming the synergy of future paradigms with revolutionary proprietary AI vision.",
    )
    assert is_hype_fluff
    assert "hype" in reason_fluff.lower()


def test_laya_fact_check_pregate():
    """Option 2: Test that LAYA passes grounded summaries and rejects hallucinations."""
    engine = get_laya_engine()

    source = "Simon Willison released version 1.0 of datasette-auth-github to fix session cookie expiration on Safari."
    grounded_summary = "Simon Willison released datasette-auth-github 1.0, fixing Safari cookie expiration issues."
    hallucinated_summary = "OpenAI partnered with Microsoft to invest 100 billion dollars in quantum computing."

    # Grounded summary should pass or have high grounded confidence
    passed, conf, reason = engine.fact_check_pregate(source, grounded_summary)
    assert passed is True
    assert "grounded" in reason.lower()

    # Hallucinated summary should fail or have high hallucination confidence
    failed, fail_conf, fail_reason = engine.fact_check_pregate(source, hallucinated_summary)
    assert failed is False
    assert "hallucination" in fail_reason.lower()


def test_laya_rank_candidates_for_theme():
    """Option 1: Test that LAYA pre-ranks candidates according to theme relevance."""
    engine = get_laya_engine()

    theme_dict = {
        "name": "Builder's Digest",
        "description": "Concrete techniques, tools, and libraries you can actually use in a weekend project",
        "tone": "hands-on, energetic, and practical developer workflows",
    }

    candidates = [
        Story(
            title="Building local RAG agents with LangChain and Ollama in Python",
            link="https://example.com/rag",
            summary="Step by step hands-on tutorial with code for setting up local embeddings and vector stores.",
            source="Test Feed",
        ),
        Story(
            title="Federal Trade Commission opens broad antitrust probe into big tech cloud agreements",
            link="https://example.com/ftc",
            summary="Government regulators issue civil subpoenas examining strategic corporate agreements.",
            source="Test Feed",
        ),
        Story(
            title="FastAPI v0.115 introduces native Pydantic v2 streaming responses",
            link="https://example.com/fastapi",
            summary="Python developer tooling release for async high-performance APIs.",
            source="Test Feed",
        ),
    ]

    shortlist = engine.rank_candidates_for_theme(candidates, theme_dict, top_k=2)
    assert len(shortlist) == 2
    # The developer tutorial or library should be ranked above federal antitrust probe for Builder's Digest
    titles = [s.title for s in shortlist]
    assert "Building local RAG agents with LangChain and Ollama in Python" in titles


# [verifies: THEME-002/AC-THEME-002.1]
# [verifies: THEME-002/AC-THEME-002.2]
def test_laya_route_theme_from_stories():
    """Option 5: Test that LAYA dynamically routes breaking news to the appropriate theme."""
    engine = get_laya_engine()

    themes = {
        "practitioner_radar": {
            "name": "Practitioner's Radar",
            "description": "Production deployment patterns, MLOps, inference optimization, and engineering architecture",
            "tone": "collegial, sharp, focused on production systems",
        },
        "builders_digest": {
            "name": "Builder's Digest",
            "description": "Concrete techniques, tools, developer libraries, and weekend hacking",
            "tone": "hands-on, practical developer workflows",
        },
    }

    stories = [
        Story(
            title="vLLM Inference Engine: Architecture and Kubernetes Production Serving",
            link="https://example.com/vllm",
            summary="Scaling LLM inference with chunked prefill, paged attention, and continuous batching in production.",
            source="Test Feed",
        ),
        Story(
            title="Triton Server TensorRT-LLM Deployment Best Practices",
            link="https://example.com/triton",
            summary="MLOps pipeline for serving deep learning models at scale.",
            source="Test Feed",
        ),
    ]

    selected_theme, distribution = engine.route_theme_from_stories(stories, themes)
    assert selected_theme == "practitioner_radar"
    assert distribution["practitioner_radar"] > distribution["builders_digest"]


def test_laya_disabled_fallback():
    """Test that when LAYA is disabled in config, fallback behaviors operate safely."""
    LayaDecisionEngine()
    dummy_config = {"laya": {"enabled": False}}

    assert not LayaDecisionEngine.is_enabled(dummy_config)


# [verifies: THEME-003/AC-THEME-003.1]
def test_get_recent_briefed_themes(tmp_path: Path):
    """Test extraction of recent briefed themes from SQLite database."""
    import sqlite3

    from laya_decision import get_recent_briefed_themes

    db_path = tmp_path / "test_runs.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT,
                theme TEXT
            );
            """
        )
        conn.execute("INSERT INTO runs (run_date, theme) VALUES ('2026-10-01', 'practitioner_radar');")
        conn.execute("INSERT INTO runs (run_date, theme) VALUES ('2026-10-02', 'builders_digest');")
        conn.execute("INSERT INTO runs (run_date, theme) VALUES ('2026-10-03', 'practitioner_radar');")
        conn.commit()

    recent = get_recent_briefed_themes(db_path, limit=2)
    assert recent == ["practitioner_radar", "builders_digest"]


# [verifies: THEME-003/AC-THEME-003.2]
def test_laya_route_theme_cooldown_penalty(tmp_path: Path):
    """Test that recent theme cooldown penalty reduces score of recently briefed themes."""
    import sqlite3

    db_path = tmp_path / "test_cooldown.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("CREATE TABLE runs (id INTEGER PRIMARY KEY AUTOINCREMENT, theme TEXT);")
        # practitioner_radar won most recently
        conn.execute("INSERT INTO runs (theme) VALUES ('practitioner_radar');")
        conn.commit()

    engine = get_laya_engine()
    themes = {
        "practitioner_radar": {
            "name": "Practitioner's Radar",
            "description": "Production systems and MLOps",
            "tone": "collegial, sharp",
        },
        "builders_digest": {
            "name": "Builder's Digest",
            "description": "Developer tooling and weekend hacking",
            "tone": "practical, hands-on",
        },
    }

    # Ambiguous story that could match either theme
    story = Story(
        title="Building LLM Microservices with Docker and Python",
        link="https://example.com/microservice",
        summary="A practical guide to containerizing LLM APIs for development and deployment.",
        source="Test Feed",
    )

    # 1. With cooldown enabled
    config_with_cooldown = {
        "laya": {
            "enabled": True,
            "enable_theme_cooldown": True,
            "theme_cooldown_recent_1": 0.50,
        },
        "deduplication": {"history_db_path": str(db_path)},
    }
    _, dist_cooldown = engine.route_theme_from_stories([story], themes, config=config_with_cooldown)

    # 2. With cooldown disabled
    config_no_cooldown = {
        "laya": {
            "enabled": True,
            "enable_theme_cooldown": False,
        },
        "deduplication": {"history_db_path": str(db_path)},
    }
    _, dist_no_cooldown = engine.route_theme_from_stories([story], themes, config=config_no_cooldown)

    # The penalized theme's share should be lower when cooldown is active
    assert dist_cooldown["practitioner_radar"] < dist_no_cooldown["practitioner_radar"]


@pytest.mark.heavy
def test_laya_live_model_inference():
    """Heavy Tier 3 integration test: loads real weights when explicitly requested via `pytest -m heavy`."""
    engine = LayaDecisionEngine()
    agent = engine.load_agent()
    if agent is None:
        pytest.skip("LAYA library or checkpoint not locally available.")
    is_hype, conf, reason = engine.filter_hype(
        title="vLLM v0.6.0 Released with Speculative Decoding and Chunked Prefill",
        summary="Detailed benchmarks showing 3x throughput improvements on multi-GPU server deployments.",
    )
    assert not is_hype
    assert "technical" in reason.lower()
