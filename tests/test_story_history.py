"""
Unit tests for StoryHistoryManager and sliding-window recurrence filtering.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from news_fetcher import build_candidate_pool
from story import Story
from story_history import (
    StoryHistoryManager,
    compute_story_hash,
    normalize_title,
    normalize_url,
)


def test_normalize_url():
    url1 = "https://www.example.com/ai/article/?utm_source=twitter&utm_medium=social#section-1"
    url2 = "https://example.com/ai/article?ref=hackernews"
    assert normalize_url(url1) == "https://example.com/ai/article"
    assert normalize_url(url2) == "https://example.com/ai/article"

    # Preserves non-tracking query parameters
    url3 = "https://example.com/search?q=machine+learning&utm_campaign=spring"
    assert "q=machine+learning" in normalize_url(url3)
    assert "utm_campaign" not in normalize_url(url3)


def test_normalize_title():
    t1 = "[Show HN] Fast-Inference: A new local LLM engine (v1.0)!"
    t2 = "Show HN: Fast-Inference: A new local LLM engine"
    norm1 = normalize_title(t1)
    norm2 = normalize_title(t2)
    assert "fast inference a new local llm engine" in norm1
    assert "fast inference a new local llm engine" in norm2


def test_compute_story_hash():
    h1 = compute_story_hash("https://example.com/article", "fast inference engine")
    h2 = compute_story_hash("https://example.com/article", "fast inference engine")
    h3 = compute_story_hash("https://example.com/other", "fast inference engine")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 24


def test_history_record_and_recurrence_detection(tmp_path: Path):
    db_file = tmp_path / "test_history.db"
    manager = StoryHistoryManager(db_file)

    past_date = datetime.now(UTC) - timedelta(days=2)
    story1 = Story(
        source="Hacker News",
        title="DeepSeek V3 Model Weights Released",
        link="https://github.com/deepseek-ai/DeepSeek-V3?utm_source=hn",
        summary="DeepSeek announces open release of model weights.",
        pub_dt=past_date,
    )
    story2 = Story(
        source="PyTorch Blog",
        title="PyTorch 2.5 Architecture Breakdown",
        link="https://pytorch.org/blog/pytorch-2-5/",
        summary="Technical deep dive into the new compiler features.",
        pub_dt=past_date,
    )

    manager.record_briefed_stories([story1, story2], theme_name="practitioner_radar", briefed_at=past_date)

    # 1. Exact URL match (even with different tracking params)
    cand_exact_url = Story(
        source="Twitter AI",
        title="DeepSeek V3 Weights are Live Now",
        link="https://github.com/deepseek-ai/DeepSeek-V3?ref=dailyai",
        summary="Check out the new release.",
    )
    is_rec, prev_date = manager.check_recurrence(cand_exact_url, lookback_days=7)
    assert is_rec is True
    assert prev_date == past_date.strftime("%Y-%m-%d")

    # 2. Fuzzy Title match
    cand_fuzzy_title = Story(
        source="ArXiv Blog",
        title="PyTorch 2.5 Architecture Breakdown: Deep Dive",
        link="https://different-domain.org/pytorch-25",
        summary="A review of PyTorch 2.5 compiler.",
    )
    is_rec2, prev_date2 = manager.check_recurrence(cand_fuzzy_title, lookback_days=7, title_threshold=0.75)
    assert is_rec2 is True
    assert prev_date2 == past_date.strftime("%Y-%m-%d")

    # 3. Completely fresh story
    fresh_story = Story(
        source="Google DeepMind",
        title="AlphaFold 3 Updates for Protein Complexes",
        link="https://deepmind.google/alphafold3",
        summary="New biomolecular structure modeling.",
    )
    is_rec3, prev_date3 = manager.check_recurrence(fresh_story, lookback_days=7)
    assert is_rec3 is False
    assert prev_date3 is None


def test_soft_score_decay_application(tmp_path: Path):
    db_file = tmp_path / "test_decay.db"
    manager = StoryHistoryManager(db_file)

    past_date = datetime.now(UTC) - timedelta(days=3)
    past_story = Story(
        source="Hacker News",
        title="vLLM 0.6 Performance Optimization",
        link="https://vllm.ai/blog/0-6",
        summary="Serving throughput boosted by 2x.",
        pub_dt=past_date,
    )
    manager.record_briefed_stories([past_story], theme_name="practitioner_radar", briefed_at=past_date)

    # Candidate list: 1 recurring, 1 fresh
    cand_recurring = Story(
        source="Hacker News",
        title="vLLM 0.6 Performance Optimization Discussion",
        link="https://vllm.ai/blog/0-6?ref=feed",
        summary="Follow up discussion on throughput.",
        score=0.80,
    )
    cand_fresh = Story(
        source="AWS Blog",
        title="Neuron Kernel Generation on Trainium2",
        link="https://aws.amazon.com/trainium2",
        summary="Accelerating training workloads.",
        score=0.60,
    )

    config = {
        "deduplication": {
            "enable_recurrence_filter": True,
            "lookback_days": 7,
            "decay_factor": 0.25,
            "title_similarity_threshold": 0.80,
        }
    }

    decayed = manager.apply_soft_decay([cand_recurring, cand_fresh], config=config)
    assert len(decayed) == 2

    # Recurring story gets decayed: 0.80 * 0.25 = 0.20
    assert cand_recurring.is_update is True
    assert cand_recurring.original_briefed_date == past_date.strftime("%Y-%m-%d")
    assert cand_recurring.score == 0.20
    assert cand_recurring.extra_metadata.get("recurrence_decayed") is True

    # Fresh story remains untouched
    assert cand_fresh.is_update is False
    assert cand_fresh.score == 0.60


def test_build_candidate_pool_integration_with_decay(tmp_path: Path):
    db_file = tmp_path / "candidate_pool_decay.db"
    manager = StoryHistoryManager(db_file)

    past_date = datetime.now(UTC) - timedelta(days=1)
    briefed_story = Story(
        source="Hacker News",
        title="Llama 3.3 70B Released",
        link="https://ai.meta.com/llama3-3",
        summary="Meta releases new 70B open weight model.",
    )
    manager.record_briefed_stories([briefed_story], theme_name="practitioner_radar", briefed_at=past_date)

    now = datetime.now(UTC)
    # Story 1: Recurring with high initial score
    s1 = Story(
        source="Hacker News",
        title="Llama 3.3 70B Released on Hugging Face",
        link="https://ai.meta.com/llama3-3",
        summary="Meta releases new 70B open weight model with full weights.",
        pub_dt=now,
        points=300,
    )
    # Story 2: Fresh story with moderate score
    s2 = Story(
        source="PyTorch Blog",
        title="TorchTitan Distributed Pretraining Guide",
        link="https://pytorch.org/titan",
        summary="End to end pretraining guide for large language models.",
        pub_dt=now,
        points=50,
    )

    config = {
        "deduplication": {
            "enable_recurrence_filter": True,
            "lookback_days": 7,
            "decay_factor": 0.20,
            "title_similarity_threshold": 0.80,
            "history_db_path": str(db_file),
        },
        "laya": {"enabled": False},
    }

    pool = build_candidate_pool([s1, s2], candidate_pool_size=5, config=config)

    # s1 score got decayed, so fresh story s2 should rank #1
    assert pool[0].title == "TorchTitan Distributed Pretraining Guide"
    assert pool[0].is_update is False

    # s1 is still in pool (if size permits), but flagged as update
    assert pool[1].title == "Llama 3.3 70B Released on Hugging Face"
    assert pool[1].is_update is True
    assert pool[1].original_briefed_date == past_date.strftime("%Y-%m-%d")


def test_clear_history(tmp_path: Path):
    db_file = tmp_path / "clear_history.db"
    manager = StoryHistoryManager(db_file)
    s = Story(source="A", title="Title", link="https://a.com", summary="Sum")
    manager.record_briefed_stories([s], theme_name="test")
    assert len(manager.get_recent_briefed_stories(lookback_days=7)) == 1

    manager.clear_history()
    assert len(manager.get_recent_briefed_stories(lookback_days=7)) == 0
