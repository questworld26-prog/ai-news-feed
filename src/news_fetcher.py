"""
News Fetcher Module
Handles fetching, HTML cleaning, scoring, filtering, and deduplicating RSS feed entries.
"""

from __future__ import annotations

import logging
import re
import time
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
    common cookie consent notices and navigation headers. Supports OpenGraph
    meta description fallback when article bodies are dynamic or paywalled.
    """
    if not url or not url.lower().startswith(("http://", "https://")) or url.lower().endswith(".pdf"):
        return ""
    try:
        resp = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            allow_redirects=True,
        )
        resp.raise_for_status()
        resp_headers = getattr(resp, "headers", {})
        content_type = resp_headers.get("content-type", "").lower() if hasattr(resp_headers, "get") else ""
        if "application/pdf" in content_type or "application/octet-stream" in content_type:
            return ""

        raw_content = getattr(resp, "content", None)
        if isinstance(raw_content, (bytes, bytearray)):
            html = raw_content[:512_000].decode("utf-8", errors="replace")
        else:
            html = str(getattr(resp, "text", ""))[:512_000]

        # Extract OpenGraph or meta description before stripping head tags
        meta_desc = ""
        og_match = re.search(r'(?i)<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)["\']', html)
        if not og_match:
            og_match = re.search(r'(?i)<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html)
        if og_match:
            meta_desc = clean_html_text(og_match.group(1))

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
            clean_p = re.sub(r"<[^>]+>", " ", p)
            clean_p = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean_p)
            clean_p = re.sub(r"\s+", " ", clean_p).strip()
            if len(clean_p) >= 25 and not cookie_pattern.search(clean_p):
                filtered_paras.append(clean_p)

        if filtered_paras:
            text = " ".join(filtered_paras)
        elif meta_desc and len(meta_desc) >= 40:
            text = meta_desc
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
    entry: Any, name: str, hard_filters: list[str], now: datetime, max_age_hours: float = 96.0
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

    # Minimum Content Gate: discard stories with insufficient context (< 80 chars) to synthesize factually
    if len(summary.strip()) < 80:
        logger.debug(
            f"Filtering out story with insufficient context ({len(summary.strip())} chars < 80): '{title[:45]}'"
        )
        return None

    return Story(
        source=name,
        title=title,
        link=link,
        summary=summary[:400] if summary else "",
        pub_dt=pub_dt,
        points=points,
    )


def sanitize_feed_xml(raw_bytes: bytes) -> bytes:
    """Fix common RSS XML malformations such as unescaped ampersands."""
    text = raw_bytes.decode("utf-8", errors="replace")
    # Escape unescaped ampersands not part of valid XML entities
    text = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)
    return text.encode("utf-8")


def fetch_entries_from_source(
    src: dict[str, Any],
    hard_filters: list[str],
    now: datetime,
    config: dict[str, Any] | None = None,
    max_age_hours: float | None = None,
) -> list[Story]:
    """Fetch and parse all valid entries from a single RSS feed source with retry on transient network/gateway errors."""
    name = src.get("name", "Unknown")
    url = src.get("url", "")
    if not url:
        return []

    feeds_cfg = (config or {}).get("feeds", {})
    if max_age_hours is None:
        max_age_hours = float(feeds_cfg.get("max_age_hours", 96.0))
    timeout = int(feeds_cfg.get("request_timeout", 25))
    max_retries = int(feeds_cfg.get("max_retries", 3))

    entries: list[Story] = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    logger.info(f"Querying feed: {name}...")
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            # Transient server error handling
            if resp.status_code in (500, 502, 503, 504) and attempt < max_retries:
                backoff_s = attempt * 2.0
                logger.warning(
                    f"  ⚠️ {name} returned HTTP {resp.status_code} (attempt {attempt}/{max_retries}). Retrying in {backoff_s:.1f}s..."
                )
                time.sleep(backoff_s)
                continue
            resp.raise_for_status()

            # Sanitize and parse XML bytes
            sanitized_content = sanitize_feed_xml(resp.content)
            parsed = feedparser.parse(sanitized_content)

            # Fallback to direct URL parse if byte parsing produced zero entries and had bozo error
            if not parsed.entries and parsed.bozo:
                logger.debug(f"Byte parsing failed for {name} ({parsed.bozo_exception}), trying direct feedparser...")
                parsed = feedparser.parse(url, request_headers=headers)

            if not parsed.entries:
                if parsed.bozo:
                    logger.warning(f"Could not parse entries from {name}: {parsed.bozo_exception}")
                else:
                    logger.debug(f"Feed {name} returned 0 entries.")
                return []

            for entry in parsed.entries:
                parsed_item = parse_feed_entry(entry, name, hard_filters, now, max_age_hours=max_age_hours)
                if parsed_item:
                    entries.append(parsed_item)

            logger.info(f"  └─ Retrieved {len(entries)} valid stories from {name}")
            return entries

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as net_err:
            if attempt < max_retries:
                backoff_s = attempt * 2.0
                logger.warning(
                    f"  ⚠️ Timeout/Connection error on {name} (attempt {attempt}/{max_retries}): {net_err}. Retrying in {backoff_s:.1f}s..."
                )
                time.sleep(backoff_s)
            else:
                logger.warning(f"Error fetching from {name} after {max_retries} attempts: {net_err}")
        except Exception as e:
            logger.warning(f"Error fetching from {name}: {e}")
            break

    return entries


def build_candidate_pool(
    all_entries: list[Story],
    candidate_pool_size: int,
    max_per_source: int = 2,
    config: dict[str, Any] | None = None,
) -> list[Story]:
    """Filter duplicates, apply LAYA System 1 hype filter, enforce per-source limits, and select top candidate stories."""
    for entry in all_entries:
        entry.score = score_entry(entry)

    # Sliding-Window Recurrence Filter with Soft Score Decay
    dedup_cfg = (config or {}).get("deduplication", {})
    if dedup_cfg.get("enable_recurrence_filter", True):
        try:
            from story_history import StoryHistoryManager

            history_db = dedup_cfg.get("history_db_path")
            history_mgr = StoryHistoryManager(history_db)
            all_entries = history_mgr.apply_soft_decay(all_entries, config=config)
        except Exception as exc:
            logger.warning(f"Recurrence filter soft decay skipped due to error: {exc}")

    all_entries.sort(key=lambda x: x.score, reverse=True)

    # Option 4: LAYA System 1 Semantic Hype & PR Filter
    laya_cfg = (config or {}).get("laya", {})
    if laya_cfg.get("enabled", True) and laya_cfg.get("enable_hype_filter", True):
        try:
            from laya_decision import get_laya_engine

            engine = get_laya_engine(config)
            filtered_entries: list[Story] = []
            eval_cap = max(candidate_pool_size * 3, 40)
            items_to_eval = all_entries[:eval_cap]
            remaining_items = all_entries[eval_cap:]

            for item in items_to_eval:
                is_hype, conf, reason = engine.filter_hype(item.title, item.summary, config)
                if is_hype:
                    logger.info(f"🚫 LAYA Hype Filter dropped: '{item.title[:55]}' ({reason})")
                    continue
                filtered_entries.append(item)
            all_entries = filtered_entries + remaining_items
        except Exception as exc:
            logger.debug(f"LAYA hype filtering skipped due to error: {exc}")

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


def fetch_stories_for_theme(
    theme_dict: dict[str, Any], config: dict[str, Any], max_age_hours: float | None = None
) -> list[Story]:
    """
    Fetch AI stories from RSS feeds specific to a chosen theme concurrently.
    Filters out noise using hard_filters, scores remaining stories,
    deduplicates fuzzy titles, caps per-source entries, and returns a candidate pool.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    sources = theme_dict.get("sources", [])
    hard_filters = theme_dict.get("hard_filters", [])
    candidate_pool_size = config.get("feeds", {}).get("candidate_pool_size", 15)

    effective_max_age = (
        max_age_hours if max_age_hours is not None else float(config.get("feeds", {}).get("max_age_hours", 96.0))
    )

    all_entries: list[Story] = []
    now = datetime.now(UTC)

    logger.info(
        f"Fetching concurrently from {len(sources)} sources for theme '{theme_dict.get('name')}' (max_age: {effective_max_age:.1f}h)..."
    )
    max_workers = min(10, max(1, len(sources)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_src = {
            executor.submit(
                fetch_entries_from_source, src, hard_filters, now, config=config, max_age_hours=effective_max_age
            ): src
            for src in sources
        }
        for future in as_completed(future_to_src):
            src = future_to_src[future]
            try:
                entries = future.result()
                all_entries.extend(entries)
            except Exception as exc:
                logger.warning(f"Failed to fetch entries from {src.get('name', 'Unknown')}: {exc}")

    candidate_pool = build_candidate_pool(all_entries, candidate_pool_size, config=config)

    logger.info(f"Built candidate pool of {len(candidate_pool)} unique stories for '{theme_dict.get('name')}'.")
    return candidate_pool


def sample_breaking_headlines(config: dict[str, Any], max_items: int = 12, quota_per_theme: int = 2) -> list[Story]:
    """
    Fetch a balanced cross-section of top breaking headlines across all configured themes
    using Stratified Sampling (an equal quota per theme) to power
    Option 5 (LAYA Story-Driven Dynamic Theme Routing).
    """
    themes = config.get("themes", {})
    if not themes:
        return []

    laya_cfg = config.get("laya", {})
    quota = int(laya_cfg.get("theme_routing_quota_per_theme", quota_per_theme))

    from concurrent.futures import ThreadPoolExecutor, as_completed

    now = datetime.now(UTC)

    def fetch_theme_quota(theme_key: str, theme_dict: dict[str, Any]) -> list[Story]:
        sources = theme_dict.get("sources", [])
        if not sources:
            return []
        theme_entries: list[Story] = []
        # Walk sources until we satisfy quota or exhaust sources
        for src in sources:
            if len(theme_entries) >= quota:
                break
            try:
                entries = fetch_entries_from_source(src, [], now, config=config)
                theme_entries.extend(entries)
            except Exception:
                pass

        for e in theme_entries:
            e.score = score_entry(e)
            e.extra_metadata["sampled_theme"] = theme_key
        theme_entries.sort(key=lambda s: s.score, reverse=True)

        unique_theme_stories: list[Story] = []
        for s in theme_entries:
            if not any(is_similar_title(s.title, u.title) for u in unique_theme_stories):
                unique_theme_stories.append(s)
                if len(unique_theme_stories) >= quota:
                    break
        return unique_theme_stories

    balanced_samples: list[Story] = []
    with ThreadPoolExecutor(max_workers=min(4, len(themes))) as executor:
        future_to_theme = {executor.submit(fetch_theme_quota, t_key, t_dict): t_key for t_key, t_dict in themes.items()}
        for future in as_completed(future_to_theme):
            try:
                stories = future.result()
                balanced_samples.extend(stories)
            except Exception:
                pass

    logger.info(
        f"📡 Sampled {len(balanced_samples)} balanced headlines across {len(themes)} themes (quota={quota}/theme)."
    )
    return balanced_samples[:max_items]


def check_all_sources_health(config: dict[str, Any]) -> dict[str, Any]:
    """
    Diagnostic tool to concurrently ping and validate all RSS feed sources across all configured themes.
    Returns status codes, story yields within the max_age_hours cutoff, latencies, and error summaries.
    """
    from concurrent.futures import ThreadPoolExecutor

    themes = config.get("themes", {})
    feeds_cfg = config.get("feeds", {})
    now = datetime.now(UTC)
    max_age_hours = float(feeds_cfg.get("max_age_hours", 96.0))
    timeout = int(feeds_cfg.get("request_timeout", 15))

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    def check_source(src: dict[str, Any]) -> dict[str, Any]:
        src_name = src.get("name", "Unknown")
        src_url = src.get("url", "")
        t0 = time.time()
        try:
            resp = requests.get(src_url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            sanitized = sanitize_feed_xml(resp.content)
            parsed = feedparser.parse(sanitized)
            if not parsed.entries and parsed.bozo:
                parsed = feedparser.parse(src_url, request_headers=headers)
            recent_count = 0
            for entry in parsed.entries:
                pub_parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
                if pub_parsed:
                    pub_dt = datetime(*pub_parsed[:6], tzinfo=UTC)
                    age_hours = (now - pub_dt).total_seconds() / 3600.0
                    if age_hours <= max_age_hours:
                        recent_count += 1
                else:
                    recent_count += 1
            latency = time.time() - t0
            return {
                "name": src_name,
                "url": src_url,
                "status": f"HTTP {resp.status_code}",
                "stories_count": recent_count,
                "latency_s": round(latency, 2),
                "error": None,
                "is_healthy": True,
            }
        except Exception as exc:
            latency = time.time() - t0
            return {
                "name": src_name,
                "url": src_url,
                "status": "FAILED",
                "stories_count": 0,
                "latency_s": round(latency, 2),
                "error": str(exc),
                "is_healthy": False,
            }

    all_tasks = []
    for theme_key, theme_dict in themes.items():
        for src in theme_dict.get("sources", []):
            all_tasks.append((theme_key, src))

    with ThreadPoolExecutor(max_workers=min(10, max(1, len(all_tasks)))) as executor:
        futures = [(t_key, executor.submit(check_source, src)) for t_key, src in all_tasks]
        results_by_theme: dict[str, list[dict[str, Any]]] = {t_key: [] for t_key in themes}
        total_sources = len(all_tasks)
        healthy_sources = 0
        failed_sources = 0

        for t_key, f in futures:
            res = f.result()
            if res.pop("is_healthy"):
                healthy_sources += 1
            else:
                failed_sources += 1
            results_by_theme[t_key].append(res)

    return {
        "total_sources": total_sources,
        "healthy_sources": healthy_sources,
        "failed_sources": failed_sources,
        "themes": results_by_theme,
    }
