"""
News Fetcher Module
Handles fetching, HTML cleaning, scoring, filtering, and deduplicating RSS feed entries.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from difflib import SequenceMatcher
from typing import Any

import feedparser
import requests

from story import Story

logger = logging.getLogger("ai_briefing")

# Minimum cleaned-summary length before we attempt a live article fetch.
_SNIPPET_MIN_CHARS = 50
# Max characters extracted from a fetched article body.
_ARTICLE_EXCERPT_CHARS = 300


def fetch_article_excerpt(url: str, max_chars: int = _ARTICLE_EXCERPT_CHARS) -> str:
    """
    Fetch the article at *url* and return a clean plain-text excerpt of up to
    *max_chars* characters from the page body.

    Called eagerly during feed ingestion to enrich stories whose RSS summary
    is too short to provide meaningful curation context.

    Targets content containers (<article>, <main>, or paragraphs) and filters
    common cookie consent notices and navigation headers.

    Designed to fail silently: any network or parsing error returns ""
    so it never blocks the fetch pipeline.
    """
    if not url:
        return ""
    try:
        resp = requests.get(
            url,
            timeout=6,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AIBriefingBot/1.0)"},
            allow_redirects=True,
        )
        resp.raise_for_status()
        html = resp.text

        # Remove <script>, <style>, <nav>, <footer>, and <head> blocks wholesale.
        html = re.sub(r"(?is)<(script|style|head|nav|footer|header|aside)[^>]*>.*?</\1>", " ", html)

        # Look for content-rich semantic tags first (<article>, <main>)
        content_match = re.search(r"(?is)<(article|main)[^>]*>(.*?)</\1>", html)
        candidate_html = content_match.group(2) if content_match else html

        # Extract text from paragraphs if available
        paragraphs = re.findall(r"(?is)<p[^>]*>(.*?)</p>", candidate_html)
        filtered_paras = []
        cookie_pattern = re.compile(r"(?i)(cookie|privacy policy|terms of service|consent|subscribe to our newsletter)")
        for p in paragraphs:
            # Strip tags from paragraph
            clean_p = re.sub(r"<[^>]+>", " ", p)
            clean_p = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean_p)
            clean_p = re.sub(r"\s+", " ", clean_p).strip()
            # Discard boilerplate cookie or subscription text
            if len(clean_p) >= 25 and not cookie_pattern.search(clean_p):
                filtered_paras.append(clean_p)

        if filtered_paras:
            text = " ".join(filtered_paras)
        else:
            # Fallback: strip remaining HTML tags from candidate HTML
            text = re.sub(r"<[^>]+>", " ", candidate_html)
            text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"fetch_article_excerpt failed for {url}: {exc}")
        return ""


def clean_html_text(raw_html: str) -> str:
    """Strip basic HTML tags, metadata lines, and excessive whitespace."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)
    text = re.sub(r"(?i)\b(Article URL|Comments URL|Points|# Comments)\b:?\s*\S*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_similar_title(title1: str, title2: str, threshold: float = 0.65) -> bool:
    """Check if two story titles are fuzzy duplicates."""
    t1 = re.sub(r"[^\w\s]", "", title1.lower()).strip()
    t2 = re.sub(r"[^\w\s]", "", title2.lower()).strip()
    if not t1 or not t2:
        return False
    if t1 in t2 or t2 in t1:
        return True
    return SequenceMatcher(None, t1, t2).ratio() >= threshold


def score_entry(entry: Story | dict[str, Any]) -> float:
    """
    Compute a relevance score for a feed entry.
    Hacker News entries are boosted by popularity (points).
    All entries are boosted by recency (newer = higher score).
    """
    if isinstance(entry, Story):
        pub_dt = entry.pub_dt or datetime.now(UTC)
        source = entry.source
        points = entry.points
        summary = entry.summary
    else:
        pub_dt = entry.get("pub_dt") or datetime.now(UTC)
        source = entry.get("source", "")
        points = entry.get("points", 0)
        summary = entry.get("summary", "")

    now = datetime.now(UTC)
    age_hours = max(0.0, (now - pub_dt).total_seconds() / 3600)
    recency_score = max(0.0, 1.0 - (age_hours / 48.0))

    popularity_score = 0.0
    if "Hacker News" in source:
        if not points:
            points_match = re.search(r"Points:\s*(\d+)", summary)
            if points_match:
                points = int(points_match.group(1))
        if points:
            popularity_score = min(1.0, points / 200.0)

    return (0.6 * recency_score) + (0.4 * popularity_score)


def matches_hard_filters(title: str, summary: str, hard_filters: list[str]) -> bool:
    """
    Check if title or summary contains any excluded terms, quote prefixes,
    or low-context placeholders.
    """
    t_lower = title.lower().strip()
    # Filter out quote posts, links, and non-technical observations
    if re.match(r"^(quoting\s|quote:\s|re:\s|sighting\s)", t_lower):
        return True

    # Require at least 25 characters of summary text if title is vague (< 20 chars)
    if len(t_lower) < 20 and len(summary.strip()) < 25:
        return True

    full_text = f"{title} {summary}".lower()
    for term in hard_filters:
        if term.lower() in full_text:
            return True
    return False


def parse_feed_entry(
    entry: Any, name: str, hard_filters: list[str], now: datetime, max_age_hours: float = 48.0
) -> Story | None:
    """Parse, clean, filter, and enrich a single feed entry."""
    pub_parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    pub_dt = datetime(*pub_parsed[:6], tzinfo=UTC) if pub_parsed else now

    # Enforce strict staleness cutoff: reject items older than max_age_hours
    if pub_parsed:
        age_hours = (now - pub_dt).total_seconds() / 3600.0
        if age_hours > max_age_hours:
            logger.debug(
                f"Filtering out stale story ({age_hours:.1f}h old > {max_age_hours}h): '{getattr(entry, 'title', '')[:40]}'"
            )
            return None

    raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
    points_match = re.search(r"Points:\s*(\d+)", raw_summary)
    points = int(points_match.group(1)) if points_match else 0

    summary = clean_html_text(raw_summary)
    title = clean_html_text(getattr(entry, "title", "Untitled"))
    link = getattr(entry, "link", "")

    if not title or not link or matches_hard_filters(title, summary, hard_filters):
        return None

    if len(summary.strip()) < _SNIPPET_MIN_CHARS:
        fetched = fetch_article_excerpt(link)
        if fetched:
            summary = fetched
            logger.debug(f"Summary enriched via live fetch: '{title[:55]}'")

    return Story(
        source=name,
        title=title,
        link=link,
        summary=summary[:400] if summary else "",
        pub_dt=pub_dt,
        points=points,
    )


def fetch_entries_from_source(src: dict[str, Any], hard_filters: list[str], now: datetime) -> list[Story]:
    """Fetch and parse all valid entries from a single RSS feed source."""
    name = src.get("name", "Unknown")
    url = src.get("url", "")
    if not url:
        return []

    entries: list[Story] = []
    try:
        logger.info(f"Querying feed: {name}...")
        parsed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0 (compatible; AIBriefingBot/1.0)"})

        if parsed.bozo and not parsed.entries:
            logger.warning(f"Could not parse entries from {name}: {parsed.bozo_exception}")
            return []

        for entry in parsed.entries:
            parsed_item = parse_feed_entry(entry, name, hard_filters, now)
            if parsed_item:
                entries.append(parsed_item)

    except Exception as e:
        logger.warning(f"Error fetching from {name}: {e}")

    return entries


def build_candidate_pool(all_entries: list[Story], candidate_pool_size: int, max_per_source: int = 2) -> list[Story]:
    """Filter duplicates, apply per-source limits, and select top candidate stories."""
    for entry in all_entries:
        entry.score = score_entry(entry)
    all_entries.sort(key=lambda x: x.score, reverse=True)

    candidate_pool: list[Story] = []
    source_counts: dict[str, int] = {}

    # Primary pass: enforce per-source limit and title deduplication
    for item in all_entries:
        src = item.source
        if source_counts.get(src, 0) >= max_per_source:
            continue

        if any(is_similar_title(item.title, existing.title) for existing in candidate_pool):
            logger.debug(f"Skipping duplicate: '{item.title[:60]}...' (source: {item.source})")
            continue

        candidate_pool.append(item)
        source_counts[src] = source_counts.get(src, 0) + 1
        if len(candidate_pool) >= candidate_pool_size:
            break

    # Secondary fallback pass: backfill if pool size target wasn't met
    if len(candidate_pool) < candidate_pool_size:
        for item in all_entries:
            if item in candidate_pool:
                continue
            if not any(is_similar_title(item.title, existing.title) for existing in candidate_pool):
                candidate_pool.append(item)
                if len(candidate_pool) >= candidate_pool_size:
                    break

    return candidate_pool


def fetch_stories_for_theme(theme_dict: dict[str, Any], config: dict[str, Any]) -> list[Story]:
    """
    Fetch AI stories from RSS feeds specific to a chosen theme.
    Filters out noise using hard_filters, scores remaining stories,
    deduplicates fuzzy titles, caps per-source entries, and returns a candidate pool.
    """
    sources = theme_dict.get("sources", [])
    hard_filters = theme_dict.get("hard_filters", [])
    candidate_pool_size = config.get("feeds", {}).get("candidate_pool_size", 15)

    all_entries: list[Story] = []
    now = datetime.now(UTC)

    logger.info(f"Fetching from {len(sources)} sources for theme '{theme_dict.get('name')}'...")
    for src in sources:
        all_entries.extend(fetch_entries_from_source(src, hard_filters, now))

    candidate_pool = build_candidate_pool(all_entries, candidate_pool_size)

    logger.info(f"Built candidate pool of {len(candidate_pool)} unique stories for '{theme_dict.get('name')}'.")
    return candidate_pool
