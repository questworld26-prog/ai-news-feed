"""
Unit tests for News Fetcher module: staleness cutoffs, retries, and ingestion resilience.
"""

from datetime import UTC, datetime, timedelta

from news_fetcher import fetch_entries_from_source, parse_feed_entry


class MockFeedEntry:
    def __init__(self, title: str, link: str, summary: str, pub_dt: datetime):
        self.published_parsed = pub_dt.timetuple()
        self.title = title
        self.link = link
        self.summary = summary


def test_parse_feed_entry_accepts_weekend_posts_at_96h():
    """Verify that Friday posts (~72 hours old) are accepted under the 96-hour window."""
    now = datetime.now(UTC)
    friday_post_dt = now - timedelta(hours=72)
    entry = MockFeedEntry(
        title="OpenAI Releases New Research Paper",
        link="https://openai.com/news/paper",
        summary="Detailed technical exploration of reinforcement learning fine-tuning and inference optimizations.",
        pub_dt=friday_post_dt,
    )

    result = parse_feed_entry(entry, "OpenAI News", hard_filters=[], now=now, max_age_hours=96.0)
    assert result is not None
    assert result.title == "OpenAI Releases New Research Paper"
    assert result.source == "OpenAI News"


def test_parse_feed_entry_rejects_stories_beyond_max_age():
    """Verify that stories older than max_age_hours are cleanly discarded."""
    now = datetime.now(UTC)
    ancient_dt = now - timedelta(hours=100)
    entry = MockFeedEntry(
        title="Outdated Architecture Update",
        link="https://openai.com/news/old",
        summary="An older blog post from last week describing preliminary exploration results.",
        pub_dt=ancient_dt,
    )

    result = parse_feed_entry(entry, "OpenAI News", hard_filters=[], now=now, max_age_hours=96.0)
    assert result is None


def test_fetch_entries_from_source_retries_transient_502(monkeypatch):
    """Verify that transient 502/504 errors trigger retries with backoff and succeed when recovered."""
    call_count = 0

    class MockResponse:
        def __init__(self, status_code: int, content: bytes):
            self.status_code = status_code
            self.content = content

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

    def mock_requests_get(url, headers, timeout):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MockResponse(502, b"Bad Gateway")
        valid_rss = (
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<rss version="2.0">\n'
            b"<channel>\n"
            b"  <title>Mock Feed</title>\n"
            b"  <item>\n"
            b"    <title>Resilient RSS Story</title>\n"
            b"    <link>https://example.com/story</link>\n"
            b"    <description>This resilient story tests retry and recovery logic for transient RSS server failures with sufficient character context.</description>\n"
            b"  </item>\n"
            b"</channel>\n"
            b"</rss>"
        )
        return MockResponse(200, valid_rss)

    monkeypatch.setattr("requests.get", mock_requests_get)
    monkeypatch.setattr("time.sleep", lambda s: None)  # speed up test

    src = {"name": "Test Source", "url": "https://example.com/feed.xml"}
    config = {"feeds": {"request_timeout": 10, "max_retries": 3, "max_age_hours": 96.0}}
    now = datetime.now(UTC)

    entries = fetch_entries_from_source(src, hard_filters=[], now=now, config=config)
    assert call_count == 2
    assert len(entries) == 1
    assert entries[0].title == "Resilient RSS Story"


def test_build_candidate_pool_caps_evaluation():
    """Verify build_candidate_pool enforces candidate_pool_size and per-source caps."""
    from news_fetcher import build_candidate_pool
    from story import Story

    titles = [
        "Quantum Computing Breakthrough in Superconductors",
        "Diffusion Kernel Optimization for Edge Devices",
        "Agentic Tool Calling Framework Released by Anthropic",
        "Vector Indexing Benchmarks Across Scale Architectures",
        "Speculative Decoding Accelerates Inference by 2x",
        "Distributed Checkpointing for Large Scale Training",
        "Sparse Attention Mechanisms in Production Systems",
    ]

    mock_entries = [
        Story(
            source=f"Source {i % 3}",
            title=title,
            link=f"https://example.com/story-{i}",
            summary="A comprehensive technical breakdown of autonomous agent reasoning and performance.",
            score=float(i + 1),
        )
        for i, title in enumerate(titles)
    ]

    pool = build_candidate_pool(
        mock_entries,
        candidate_pool_size=5,
        max_per_source=2,
        config={"laya": {"enabled": False}, "deduplication": {"enable_recurrence_filter": False}},
    )
    assert len(pool) == 5
    # Enforces per-source cap of 2: maximum 2 from any single source
    counts = {}
    for item in pool:
        counts[item.source] = counts.get(item.source, 0) + 1
    assert all(c <= 2 for c in counts.values())


def test_check_all_sources_health(monkeypatch):
    """Verify check_all_sources_health diagnostics across configured themes."""
    from news_fetcher import check_all_sources_health

    class MockResp:
        def __init__(self, status_code: int, content: bytes):
            self.status_code = status_code
            self.content = content

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

    def mock_get(url, headers, timeout):
        if "bad" in url:
            return MockResp(502, b"Bad Gateway")
        rss = (
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<rss version="2.0">\n'
            b"<channel><title>Feed</title>\n"
            b"  <item><title>Item 1</title><link>https://ex.com/1</link><description>Valid summary context with more than eighty characters for parsing requirements.</description></item>\n"
            b"</channel></rss>"
        )
        return MockResp(200, rss)

    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("time.sleep", lambda s: None)

    cfg = {
        "feeds": {"request_timeout": 5, "max_retries": 1, "max_age_hours": 96.0},
        "themes": {
            "theme_a": {
                "name": "Theme A",
                "sources": [
                    {"name": "Good Source 1", "url": "https://example.com/feed1.xml"},
                    {"name": "Bad Source", "url": "https://example.com/bad.xml"},
                ],
            },
            "theme_b": {
                "name": "Theme B",
                "sources": [
                    {"name": "Good Source 2", "url": "https://example.com/feed2.xml"},
                ],
            },
        },
    }

    report = check_all_sources_health(cfg)
    assert report["total_sources"] == 3
    assert report["healthy_sources"] == 2
    assert report["failed_sources"] == 1
    assert "theme_a" in report["themes"]
    assert len(report["themes"]["theme_a"]) == 2
