"""
Story History Module for AI News Voice Feed Pipeline.
Manages persistent cross-day story history in SQLite, enables sliding-window lookback,
and provides soft score decay and update tracking for recurring stories.
"""

from __future__ import annotations

import hashlib
import logging
import re
import sqlite3
from datetime import UTC, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from story import Story

logger = logging.getLogger("ai_briefing")

DEFAULT_DB_PATH = Path("eval/quality.db")

# Common URL query parameters used purely for tracking/referrals
_TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "source",
    "fbclid",
    "gclid",
    "ncid",
    "feature",
    "feed",
}

# Prefixes often prepended to titles by aggregators or community feeds
_TITLE_PREFIX_PATTERN = re.compile(
    r"^(?:\[(?:show\s+hn|ask\s+hn|paper|pdf|video|release)\]|\b(?:show\s+hn|ask\s+hn|announcing|release):\s*)",
    re.IGNORECASE,
)


def normalize_url(raw_url: str) -> str:
    """
    Clean and canonicalize a URL by removing marketing tracking parameters,
    anchors/fragments, and standardizing host and trailing slashes.
    """
    if not raw_url:
        return ""
    try:
        parsed = urlparse(raw_url.strip())
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        # Filter out tracking query params
        query_pairs = parse_qs(parsed.query, keep_blank_values=False)
        cleaned_query = {k: v for k, v in query_pairs.items() if k.lower() not in _TRACKING_PARAMS}
        # Sort query keys for deterministic representation
        query_string = urlencode(cleaned_query, doseq=True)

        return urlunparse((scheme, netloc, path, "", query_string, ""))
    except Exception:
        return raw_url.strip()


def normalize_title(raw_title: str) -> str:
    """
    Normalize title by stripping feed prefix tags, lowercasing,
    and removing non-alphanumeric noise for reliable fuzzy matching.
    """
    if not raw_title:
        return ""
    t = _TITLE_PREFIX_PATTERN.sub("", raw_title.strip()).lower()
    # Replace punctuation and special characters with spaces
    t = re.sub(r"[^\w\s]", " ", t)
    # Collapse multiple whitespaces
    return " ".join(t.split())


def compute_story_hash(canonical_url: str, clean_title: str) -> str:
    """Compute deterministic SHA-256 hash for a canonical URL and title."""
    composite = f"{canonical_url.strip()}|{clean_title.strip()}".encode()
    return hashlib.sha256(composite).hexdigest()[:24]


class StoryHistoryManager:
    """
    Manages historical briefed stories in SQLite to support
    sliding-window recurrence detection and soft score decay.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def _init_db(self) -> None:
        """Create the briefed_story_history table and performance indexes."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS briefed_story_history (
                    story_hash       TEXT PRIMARY KEY,
                    canonical_url    TEXT NOT NULL,
                    clean_title      TEXT NOT NULL,
                    raw_title        TEXT NOT NULL,
                    theme_name       TEXT NOT NULL,
                    briefed_at       TEXT NOT NULL,
                    briefed_date     TEXT NOT NULL,
                    summary_excerpt  TEXT
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_briefed_at ON briefed_story_history(briefed_at);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_canonical_url ON briefed_story_history(canonical_url);"
            )

    def record_briefed_stories(
        self,
        stories: list[Story],
        theme_name: str,
        briefed_at: datetime | None = None,
    ) -> int:
        """
        Record final briefed stories into persistent history.
        Returns the number of stories inserted or updated.
        """
        if not stories:
            return 0

        ts = briefed_at or datetime.now(UTC)
        ts_iso = ts.isoformat()
        date_str = ts.strftime("%Y-%m-%d")

        inserted = 0
        with self._get_connection() as conn:
            for s in stories:
                c_url = normalize_url(s.link)
                c_title = normalize_title(s.title)
                s_hash = compute_story_hash(c_url, c_title)
                excerpt = (s.validated_summary or s.summary or "")[:300]

                conn.execute(
                    """
                    INSERT OR REPLACE INTO briefed_story_history (
                        story_hash, canonical_url, clean_title, raw_title,
                        theme_name, briefed_at, briefed_date, summary_excerpt
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (s_hash, c_url, c_title, s.title, theme_name, ts_iso, date_str, excerpt),
                )
                inserted += 1
            conn.commit()

        logger.info(f"Recorded {inserted} briefed stories into history database ({self.db_path}).")
        return inserted

    def get_recent_briefed_stories(self, lookback_days: int = 7) -> list[dict[str, Any]]:
        """Retrieve all stories briefed within the lookback window."""
        cutoff_dt = datetime.now(UTC) - timedelta(days=lookback_days)
        cutoff_iso = cutoff_dt.isoformat()

        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT story_hash, canonical_url, clean_title, raw_title,
                       theme_name, briefed_at, briefed_date, summary_excerpt
                FROM briefed_story_history
                WHERE briefed_at >= ?
                ORDER BY briefed_at DESC
                """,
                (cutoff_iso,),
            )
            return [dict(row) for row in cur.fetchall()]

    def check_recurrence(
        self,
        story: Story,
        lookback_days: int = 7,
        title_threshold: float = 0.80,
    ) -> tuple[bool, str | None]:
        """
        Check if a candidate story matches any story briefed in the lookback window.
        Returns:
            (is_recurring, previous_briefed_date)
        """
        recent = self.get_recent_briefed_stories(lookback_days=lookback_days)
        if not recent:
            return False, None

        cand_url = normalize_url(story.link)
        cand_title = normalize_title(story.title)

        # 1. Exact Canonical URL match
        if cand_url:
            for row in recent:
                if row["canonical_url"] == cand_url:
                    return True, row["briefed_date"]

        # 2. Fuzzy Title similarity match
        if cand_title:
            for row in recent:
                past_title = row["clean_title"]
                sim = SequenceMatcher(None, cand_title, past_title).ratio()
                if sim >= title_threshold:
                    return True, row["briefed_date"]

        return False, None

    def apply_soft_decay(
        self,
        entries: list[Story],
        config: dict[str, Any] | None = None,
    ) -> list[Story]:
        """
        Inspect all candidate stories against the history window.
        If a story was previously briefed:
        - Flags `story.is_update = True`
        - Sets `story.original_briefed_date = previous_briefed_date`
        - Decays `story.score` by `decay_factor`
        """
        if not entries:
            return entries

        dedup_cfg = (config or {}).get("deduplication", {})
        if not dedup_cfg.get("enable_recurrence_filter", True):
            return entries

        lookback_days = int(dedup_cfg.get("lookback_days", 7))
        decay_factor = float(dedup_cfg.get("decay_factor", 0.25))
        title_threshold = float(dedup_cfg.get("title_similarity_threshold", 0.80))

        recent = self.get_recent_briefed_stories(lookback_days=lookback_days)
        if not recent:
            return entries

        decayed_count = 0
        for item in entries:
            cand_url = normalize_url(item.link)
            cand_title = normalize_title(item.title)
            matched_date: str | None = None

            # Check exact URL
            if cand_url:
                for row in recent:
                    if row["canonical_url"] == cand_url:
                        matched_date = row["briefed_date"]
                        break

            # Check fuzzy title if URL didn't match
            if not matched_date and cand_title:
                for row in recent:
                    past_title = row["clean_title"]
                    if SequenceMatcher(None, cand_title, past_title).ratio() >= title_threshold:
                        matched_date = row["briefed_date"]
                        break

            if matched_date:
                old_score = item.score
                item.is_update = True
                item.original_briefed_date = matched_date
                item.score = round(item.score * decay_factor, 4)
                item.extra_metadata["recurrence_decayed"] = True
                item.extra_metadata["original_score"] = old_score
                decayed_count += 1
                logger.info(
                    f"🔄 Recurrence detected: '{item.title[:45]}...' "
                    f"[Score decayed: {old_score:.3f} -> {item.score:.3f}, Briefed on {matched_date}]"
                )

        if decayed_count > 0:
            logger.info(
                f"Sliding-window recurrence filter applied soft decay ({decay_factor}) to {decayed_count} stories."
            )

        return entries

    def clear_history(self) -> None:
        """Clear all records from the briefed_story_history table (useful for testing)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM briefed_story_history;")
            conn.commit()
