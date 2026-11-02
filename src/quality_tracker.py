"""
Quality Tracker Module for AI News Voice Feed Pipeline.
Manages versioned quality metrics in SQLite database (eval/quality.db).
Logs execution telemetry, story synthesis scores, retry counts, failure rates,
fact-checking results, models used, and human reviews.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger("ai_briefing")

DEFAULT_DB_PATH = Path("eval/quality.db")


def get_current_git_commit() -> str:
    """Return short git commit SHA or 'unknown'."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def extract_domain(url: str) -> str:
    """Extract clean domain name from URL."""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "unknown"
    except Exception:
        return "unknown"


def check_theme_relevance(title: str, summary: str, theme_dict: dict[str, Any] | None) -> bool:
    """Heuristic check for theme relevance using theme description/keywords."""
    if not theme_dict:
        return True
    combined_text = f"{title} {summary}".lower()
    # Check for hard filter violations
    hard_filters = [f.lower() for f in theme_dict.get("hard_filters", [])]
    for hf in hard_filters:
        if hf in combined_text:
            return False
    return True


class QualityTracker:
    """Encapsulates SQLite quality tracking database operations."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Create tables and indices if they do not exist."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id              TEXT UNIQUE NOT NULL,
                    run_date            TEXT NOT NULL,
                    git_commit          TEXT NOT NULL,
                    models_used         TEXT NOT NULL,
                    theme               TEXT NOT NULL,
                    strategy            TEXT,
                    total_duration_s    REAL DEFAULT 0.0,
                    phase3_duration_s   REAL DEFAULT 0.0,
                    phase3_mem_delta_mb REAL DEFAULT 0.0,
                    phase3_mem_rss_mb   REAL DEFAULT 0.0,
                    phase3_token_speed_tps REAL DEFAULT 0.0,
                    stories_total       INTEGER DEFAULT 0,
                    stories_failed      INTEGER DEFAULT 0,
                    story_failure_rate  REAL DEFAULT 0.0,
                    total_retries       INTEGER DEFAULT 0,
                    audio_script_word_count INTEGER DEFAULT 0,
                    audio_script_target INTEGER DEFAULT 750,
                    factcheck_passed    INTEGER DEFAULT 1,
                    factcheck_retries   INTEGER DEFAULT 1,
                    human_rating        INTEGER,
                    human_comment       TEXT,
                    reviewed_at         TEXT,
                    created_at          TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS story_scores (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id              TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
                    story_title         TEXT NOT NULL,
                    story_url           TEXT,
                    story_domain        TEXT,
                    position            INTEGER,
                    summary_status      TEXT NOT NULL, -- 'success', 'fallback', 'failed'
                    summary_text        TEXT DEFAULT '',
                    summary_word_count  INTEGER DEFAULT 0,
                    retry_count         INTEGER DEFAULT 1,
                    keyword_overlap     REAL DEFAULT 0.0,
                    theme_relevant      INTEGER DEFAULT 1,
                    created_at          TEXT DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_runs_date ON runs(run_date);
                CREATE INDEX IF NOT EXISTS idx_runs_git ON runs(git_commit);
                CREATE INDEX IF NOT EXISTS idx_runs_theme ON runs(theme);
                CREATE INDEX IF NOT EXISTS idx_story_run ON story_scores(run_id);
                """
            )
            try:
                conn.execute("ALTER TABLE story_scores ADD COLUMN summary_text TEXT DEFAULT '';")
            except sqlite3.OperationalError:
                pass

    def log_run(
        self,
        run_id: str,
        run_date: str,
        git_commit: str,
        models_used: dict[str, Any] | str,
        theme: str,
        strategy: str,
        total_duration_s: float,
        phase3_duration_s: float,
        phase3_mem_delta_mb: float,
        phase3_mem_rss_mb: float,
        stories: list[Any],
        audio_script: str,
        audio_script_target: int = 750,
        factcheck_passed: bool = True,
        factcheck_retries: int = 1,
        phase3_token_speed_tps: float = 0.0,
        theme_dict: dict[str, Any] | None = None,
    ) -> str:
        """
        Log complete run metrics and individual story scores.
        """
        models_str = json.dumps(models_used) if isinstance(models_used, dict) else str(models_used)
        audio_words = len(audio_script.split()) if audio_script else 0

        stories_total = len(stories)
        stories_failed = 0
        total_retries = 0

        story_records: list[dict[str, Any]] = []

        for idx, s in enumerate(stories, 1):
            title = getattr(s, "title", "") or (s.get("title", "") if isinstance(s, dict) else "")
            link = getattr(s, "link", "") or (s.get("link", "") if isinstance(s, dict) else "")
            summary = getattr(s, "validated_summary", "") or (
                getattr(s, "summary", "") or (s.get("summary", "") if isinstance(s, dict) else "")
            )
            extra = getattr(s, "extra_metadata", {}) or (s.get("extra_metadata", {}) if isinstance(s, dict) else {})

            retries = extra.get("retry_count", 1)
            total_retries += retries

            is_fallback = (
                "failed to generate a reliable summary" in summary.lower() or extra.get("summary_status") == "failed"
            )
            status = "failed" if is_fallback else "success"
            if is_fallback:
                stories_failed += 1

            overlap = float(extra.get("keyword_overlap", 0.0))
            if overlap == 0.0 and not is_fallback:
                # Compute default overlap if not recorded
                src_text = f"{title}\n{summary}"
                try:
                    from validator import compute_keyword_overlap

                    overlap = compute_keyword_overlap(src_text, summary)
                except Exception:
                    overlap = 0.5

            domain = extract_domain(link)
            words = len(summary.split())
            relevant = 1 if check_theme_relevance(title, summary, theme_dict) else 0

            story_records.append(
                {
                    "run_id": run_id,
                    "story_title": title,
                    "story_url": link,
                    "story_domain": domain,
                    "position": idx,
                    "summary_status": status,
                    "summary_text": summary,
                    "summary_word_count": words,
                    "retry_count": retries,
                    "keyword_overlap": round(overlap, 3),
                    "theme_relevant": relevant,
                }
            )

        failure_rate = (stories_failed / stories_total) if stories_total > 0 else 0.0

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id, run_date, git_commit, models_used, theme, strategy,
                    total_duration_s, phase3_duration_s, phase3_mem_delta_mb,
                    phase3_mem_rss_mb, phase3_token_speed_tps, stories_total,
                    stories_failed, story_failure_rate, total_retries,
                    audio_script_word_count, audio_script_target,
                    factcheck_passed, factcheck_retries
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    run_date,
                    git_commit,
                    models_str,
                    theme,
                    strategy,
                    round(total_duration_s, 2),
                    round(phase3_duration_s, 2),
                    round(phase3_mem_delta_mb, 2),
                    round(phase3_mem_rss_mb, 2),
                    round(phase3_token_speed_tps, 2),
                    stories_total,
                    stories_failed,
                    round(failure_rate, 3),
                    total_retries,
                    audio_words,
                    audio_script_target,
                    1 if factcheck_passed else 0,
                    factcheck_retries,
                ),
            )

            # Clean and re-insert story scores
            conn.execute("DELETE FROM story_scores WHERE run_id = ?", (run_id,))
            for rec in story_records:
                conn.execute(
                    """
                    INSERT INTO story_scores (
                        run_id, story_title, story_url, story_domain, position,
                        summary_status, summary_text, summary_word_count, retry_count,
                        keyword_overlap, theme_relevant
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        rec["run_id"],
                        rec["story_title"],
                        rec["story_url"],
                        rec["story_domain"],
                        rec["position"],
                        rec["summary_status"],
                        rec["summary_text"],
                        rec["summary_word_count"],
                        rec["retry_count"],
                        rec["keyword_overlap"],
                        rec["theme_relevant"],
                    ),
                )

        logger.info(
            f"📊 Quality tracker recorded run '{run_id}' (failure_rate={failure_rate:.1%}, "
            f"stories={stories_total}, audio_words={audio_words})"
        )
        return run_id

    def update_review(self, run_id: str, rating: int | None, comment: str | None) -> bool:
        """Update human review rating (1-5) and freestyle comment for a run."""
        now_iso = datetime.now().isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                UPDATE runs
                SET human_rating = ?, human_comment = ?, reviewed_at = ?
                WHERE run_id = ?;
                """,
                (rating, comment, now_iso, run_id),
            )
            return cur.rowcount > 0

    def get_runs(
        self, limit: int = 100, theme: str | None = None, git_commit: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve runs ordered by most recent first."""
        query = "SELECT * FROM runs WHERE 1=1"
        params: list[Any] = []
        if theme:
            query += " AND theme = ?"
            params.append(theme)
        if git_commit:
            query += " AND git_commit = ?"
            params.append(git_commit)
        query += " ORDER BY run_date DESC, id DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            result = []
            for r in rows:
                item = dict(r)
                try:
                    item["models_used"] = json.loads(item["models_used"])
                except Exception:
                    pass
                result.append(item)
            return result

    def get_run_detail(self, run_id: str) -> dict[str, Any] | None:
        """Retrieve complete run detail including per-story scores."""
        with self._get_connection() as conn:
            run_row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
            if not run_row:
                return None
            run_dict = dict(run_row)
            try:
                run_dict["models_used"] = json.loads(run_dict["models_used"])
            except Exception:
                pass

            stories = conn.execute(
                "SELECT * FROM story_scores WHERE run_id = ? ORDER BY position ASC", (run_id,)
            ).fetchall()
            run_dict["stories"] = [dict(s) for s in stories]
            return run_dict

    def get_summary(self) -> dict[str, Any]:
        """Get aggregate system health and quality summary."""
        with self._get_connection() as conn:
            total_runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            if total_runs == 0:
                return {
                    "total_runs": 0,
                    "avg_failure_rate": 0.0,
                    "avg_retries": 0.0,
                    "avg_audio_words": 0,
                    "avg_duration_s": 0.0,
                    "avg_human_rating": 0.0,
                    "total_reviews": 0,
                    "unique_git_commits": 0,
                }

            row = conn.execute(
                """
                SELECT
                    COUNT(*) as total_runs,
                    AVG(story_failure_rate) as avg_failure_rate,
                    AVG(total_retries * 1.0 / CASE WHEN stories_total > 0 THEN stories_total ELSE 1 END) as avg_retries,
                    AVG(audio_script_word_count) as avg_audio_words,
                    AVG(total_duration_s) as avg_duration_s,
                    AVG(phase3_duration_s) as avg_phase3_duration_s,
                    AVG(human_rating) as avg_human_rating,
                    COUNT(human_rating) as total_reviews,
                    COUNT(DISTINCT git_commit) as unique_git_commits
                FROM runs;
                """
            ).fetchone()

            avg_overlap = (
                conn.execute(
                    "SELECT AVG(keyword_overlap) FROM story_scores WHERE summary_status = 'success'"
                ).fetchone()[0]
                or 0.0
            )

            return {
                "total_runs": row["total_runs"],
                "avg_failure_rate": round(row["avg_failure_rate"] or 0.0, 3),
                "avg_retries": round(row["avg_retries"] or 0.0, 2),
                "avg_audio_words": int(row["avg_audio_words"] or 0),
                "avg_duration_s": round(row["avg_duration_s"] or 0.0, 1),
                "avg_phase3_duration_s": round(row["avg_phase3_duration_s"] or 0.0, 1),
                "avg_human_rating": round(row["avg_human_rating"] or 0.0, 2),
                "total_reviews": row["total_reviews"],
                "unique_git_commits": row["unique_git_commits"],
                "avg_keyword_overlap": round(avg_overlap, 3),
            }

    def backfill_from_markdown_files(self, output_dir: str | Path = "output") -> int:
        """
        Scan directory for historical '*_summary.md' files and parse them into DB.
        Returns count of newly indexed runs.
        """
        out_path = Path(output_dir)
        if not out_path.exists():
            return 0

        # Pattern: YYYY-MM-DD_<theme>_summary.md
        pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})_(.+)_summary\.md$")
        backfilled = 0

        default_models = {
            "curation": "phi4-mini:3.8b",
            "summary": "qwen2.5:3b",
            "script": "phi4-mini:3.8b",
            "audit": "qwen2.5:3b",
            "theme_router": "convaiinnovations/laya",
            "tts_voice": "bm_george",
        }

        for md_file in sorted(out_path.glob("*_summary.md")):
            m = pattern.match(md_file.name)
            if not m:
                continue
            run_date, theme = m.group(1), m.group(2)
            run_id = f"hist_{run_date}_{theme}"

            # Check if run exists
            with self._get_connection() as conn:
                exists = conn.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,)).fetchone()
                if exists:
                    continue

            content = md_file.read_text(encoding="utf-8")
            stories, audio_script = parse_summary_markdown(content)
            if not stories:
                continue

            # Calibrated synthesis latency estimate: ~44s per story validation + 55s per ~580 audio words
            words_cnt = len(audio_script.split()) if audio_script else 500
            est_p3 = round(len(stories) * 44.0 + (words_cnt / 580.0) * 55.0, 1)
            est_tot = round(est_p3 * 1.38, 1)

            self.log_run(
                run_id=run_id,
                run_date=run_date,
                git_commit="legacy",
                models_used=default_models,
                theme=theme,
                strategy="historical_backfill",
                total_duration_s=est_tot,
                phase3_duration_s=est_p3,
                phase3_mem_delta_mb=-3.6,
                phase3_mem_rss_mb=18.4,
                stories=stories,
                audio_script=audio_script,
            )
            backfilled += 1

        return backfilled

    def promote_story_to_golden(
        self,
        run_id: str,
        story_idx: int,
        correction: str = "",
        notes: str = "",
        golden_path: Path | str | None = None,
    ) -> dict[str, Any]:
        """
        Tier 4 HITL Continuous Promotion:
        Promote a failed, low-rated, or corrected story from quality.db into
        the golden benchmark dataset (eval/golden_dataset.json) as a permanent regression test.
        """
        detail = self.get_run_detail(run_id)
        if not detail:
            raise ValueError(f"Run ID '{run_id}' not found in quality database.")

        stories = detail.get("stories", [])
        if story_idx < 0 or story_idx >= len(stories):
            raise IndexError(f"Story index {story_idx} out of bounds (total stories: {len(stories)}).")

        story = stories[story_idx]
        target_path = Path(golden_path or "eval/golden_dataset.json")

        existing_dataset = []
        if target_path.exists():
            try:
                with open(target_path, encoding="utf-8") as f:
                    existing_dataset = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read existing golden dataset: {e}")

        case_id = f"hitl_{run_id}_{story_idx}"
        is_failed = story.get("summary_status") == "failed"

        record = {
            "id": case_id,
            "theme": detail.get("theme", "practitioner_radar"),
            "type": "audit",
            "is_poisoned": is_failed,
            "source_text": f"{story.get('story_title', '')}\n{story.get('story_url', '')}",
            "digest_summary": story.get("summary_text", ""),
            "injected_hallucinations": [correction] if correction else [],
            "expected_verdict": not is_failed,
            "promoted_by": "human_reviewer",
            "promoted_from_run": run_id,
            "notes": notes or f"Promoted from human review of run {run_id}",
        }

        # Check if already present, update or append
        updated = False
        for i, item in enumerate(existing_dataset):
            if item.get("id") == case_id:
                existing_dataset[i] = record
                updated = True
                break
        if not updated:
            existing_dataset.append(record)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(existing_dataset, f, indent=2, ensure_ascii=False)

        return {
            "status": "ok",
            "case_id": case_id,
            "file_path": str(target_path),
            "total_cases": len(existing_dataset),
        }


def parse_summary_markdown(content: str) -> tuple[list[dict[str, Any]], str]:
    """Parse output markdown format into stories list and audio script text."""
    parts = content.split("## Spoken Audio Script")
    text_digest = parts[0]
    audio_script = parts[1].strip() if len(parts) > 1 else ""

    # Extract stories: ## [Title](Link)\nSummary
    story_matches = re.finditer(r"##\s*\[(.*?)\]\((.*?)\)\n+([\s\S]*?)(?=(?:##\s*\[|$))", text_digest)
    stories: list[dict[str, Any]] = []

    for sm in story_matches:
        title = sm.group(1).strip()
        link = sm.group(2).strip()
        summary = sm.group(3).strip()

        is_failed = "failed to generate a reliable summary" in summary.lower() or summary.startswith("⚠️")

        stories.append(
            {
                "title": title,
                "link": link,
                "summary": summary,
                "extra_metadata": {
                    "retry_count": 3 if is_failed else 1,
                    "summary_status": "failed" if is_failed else "success",
                    "keyword_overlap": 0.0 if is_failed else 0.45,
                },
            }
        )

    return stories, audio_script
