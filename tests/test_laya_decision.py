"""
Unit tests for LAYA System 1 Decision Engine (Options 1, 2, 4, 5).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from laya_decision import LayaDecisionEngine, get_laya_engine
from story import Story


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
    engine = LayaDecisionEngine()
    dummy_config = {"laya": {"enabled": False}}

    assert not LayaDecisionEngine.is_enabled(dummy_config)
