"""
AI News Voice Briefing Pipeline — Main Orchestrator
Fetches AI headlines from theme-based RSS feeds, curates & formats with Ollama,
synthesizes voice audio locally with kokoro-mlx on Apple Silicon Metal,
and delivers markdown summaries + audio briefings to Telegram and local storage.
"""

from __future__ import annotations

import argparse
import logging
import os
import random
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from briefing_generator import (
    STORY_FALLBACK_SUMMARY,
    generate_briefing_llm,
    generate_story_summary,
    llm_curate_stories,
)
from news_fetcher import fetch_stories_for_theme
from notifier import send_to_telegram, synthesize_audio
from validator import validate_story

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ai_briefing")


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from TOML file."""
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    with open(config_path, "rb") as f:
        return tomllib.load(f)


# Maximum number of summary regeneration attempts per story before using the fallback.
_VALIDATION_MAX_RETRIES = 3


def _validate_and_correct_digest(
    stories: list[dict[str, Any]],
    text_digest: str,
    theme_dict: dict[str, Any],
    config: dict[str, Any],
) -> str:
    """
    Validate each story's section in the generated digest for factual accuracy.

    For each story that fails:
      - Retry generating its summary up to _VALIDATION_MAX_RETRIES times,
        passing the fact-checker's reasoning as a correction hint each attempt.
      - If still failing after all retries, replace the summary with a
        standardised fallback notice (the title link is already in the header).

    Returns a corrected, fully assembled text_digest.
    """
    logger.info("=== Running Anti-Hallucination Validation ===")

    # Split bulk digest into: header block + per-story sections (ordered by position).
    # Format: "## [Title](url)\nSummary text.\n"
    parts = text_digest.split("\n## [")
    header = parts[0].strip()
    raw_sections = parts[1:]  # section[i] corresponds to stories[i]

    corrected_sections: list[str] = []

    for idx, story in enumerate(stories, 1):
        title = story.get("title", "")
        link = story.get("link", "")

        # Start with the bulk-generated section; fall back to empty if missing.
        if idx - 1 < len(raw_sections):
            current_section = f"## [{raw_sections[idx - 1]}"
        else:
            current_section = f"## [{title}]({link})\n"

        passed = False
        hint = ""

        for attempt in range(1, _VALIDATION_MAX_RETRIES + 1):
            result = validate_story(story, current_section, config, run_llm_check=True)
            status = "PASSED" if result.passed else "FAILED / WARN"

            logger.info(
                f"Story {idx} [{title[:40]}...] "
                f"Attempt {attempt}/{_VALIDATION_MAX_RETRIES} Fact-Check: {status} "
                f"(Overlap: {result.keyword_overlap_score:.2f})"
            )

            if result.passed:
                passed = True
                break

            # Surface failure details for observability.
            for w in result.fabrication_warnings:
                logger.warning(f"  └─ {w}")
            if not result.llm_fact_check_passed:
                logger.warning(f"  └─ LLM Fact-Check Reasoning: {result.llm_reasoning}")

            hint = result.llm_reasoning

            if attempt < _VALIDATION_MAX_RETRIES:
                logger.info(f"  ↻ Regenerating summary for story {idx} with correction hint...")
                new_summary = generate_story_summary(story, theme_dict, config, correction_hint=hint)
                if new_summary:
                    current_section = f"## [{title}]({link})\n{new_summary}\n"

        if not passed:
            logger.warning(
                f"Story {idx} [{title[:40]}...] failed after {_VALIDATION_MAX_RETRIES} attempts. Using fallback."
            )
            current_section = f"## [{title}]({link})\n{STORY_FALLBACK_SUMMARY}\n"

        corrected_sections.append(current_section)

    return header + "\n\n" + "\n\n".join(corrected_sections)


def run_all_themes(config: dict[str, Any], output_dir: Path, today_str: str) -> None:
    """
    Generate a comprehensive multi-theme digest covering all configured themes.
    Intended for catch-up reviews or dry-run evaluation (no TTS or Telegram).
    """
    themes = config.get("themes", {})
    if not themes:
        logger.error("No themes configured in config.toml.")
        return

    logger.info(f"=== Running All Themes Review ({len(themes)} themes) ===")
    combined_report = [f"# 🌐 All-Themes AI Comprehensive Briefing — {today_str}\n\n"]

    for key, theme_dict in themes.items():
        logger.info(f"\n--- Processing Theme: {theme_dict.get('name')} ---")
        candidates = fetch_stories_for_theme(theme_dict, config)
        if not candidates:
            logger.warning(f"No candidate stories found for theme {key}. Skipping.")
            continue

        curated = llm_curate_stories(candidates, theme_dict, config)
        briefing = generate_briefing_llm(curated, theme_dict, config, text_only=True)
        text_digest = briefing.get("text_digest", "")
        text_digest = _validate_and_correct_digest(curated, text_digest, theme_dict, config)
        combined_report.append(text_digest + "\n\n---\n\n")

    out_file = output_dir / f"{today_str}_all_themes.md"
    out_file.write_text("".join(combined_report), encoding="utf-8")
    logger.info(f"Successfully saved all-themes report to {out_file}")
    print("\n" + "".join(combined_report))


def main() -> None:
    parser = argparse.ArgumentParser(description="AI News Daily Voice Briefing Pipeline")
    parser.add_argument("--config", default="config.toml", help="Path to configuration TOML file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and generate script only; skip TTS synthesis and Telegram dispatch",
    )
    parser.add_argument(
        "--skip-tts",
        action="store_true",
        help="Skip audio synthesis and dispatch only the markdown text digest to Telegram",
    )
    parser.add_argument(
        "--all-themes", action="store_true", help="Generate full digest for all 4 themes in dry-run mode"
    )
    parser.add_argument("--force", action="store_true", help="Force execution even on weekends")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    config_path = project_root / args.config
    config = load_config(config_path)

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = project_root / config.get("output", {}).get("dir", "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all_themes:
        run_all_themes(config, output_dir, today_str)
        return

    weekday = datetime.now().weekday()
    weekdays_only = config.get("schedule", {}).get("weekdays_only", True)
    if weekdays_only and weekday >= 5 and not args.dry_run and not args.force:
        logger.info(
            f"Today is {'Saturday' if weekday == 5 else 'Sunday'} and weekdays_only is enabled. Skipping scheduled briefing."
        )
        sys.exit(0)

    themes = config.get("themes", {})
    if not themes:
        logger.error("No themes found in config.toml under [themes].")
        sys.exit(1)

    theme_key = random.choice(list(themes.keys()))
    theme_dict = themes[theme_key]
    logger.info(f"=== Selected Daily Theme: {theme_dict.get('emoji')} {theme_dict.get('name')} ===")

    # Step 1: RSS Aggregation -> candidate pool
    candidates = fetch_stories_for_theme(theme_dict, config)
    if not candidates:
        logger.error(f"No stories retrieved for theme {theme_key}. Exiting.")
        sys.exit(1)

    # Step 2: LLM Curation -> pick top max_stories
    stories = llm_curate_stories(candidates, theme_dict, config)

    # Step 3: LLM Briefing Digest & Monologue Script
    briefing_data = generate_briefing_llm(stories, theme_dict, config)
    text_digest = briefing_data.get("text_digest", "")
    audio_script = briefing_data.get("audio_script", "")

    # Validate and correct per-story summaries; failed stories get fallback notice.
    text_digest = _validate_and_correct_digest(stories, text_digest, theme_dict, config)

    summary_file = output_dir / f"{today_str}_{theme_key}_summary.md"
    summary_file.write_text(f"{text_digest}\n\n## Spoken Audio Script\n\n{audio_script}", encoding="utf-8")
    logger.info(f"Saved text digest & script to {summary_file}")

    if args.dry_run:
        logger.info("--- [DRY-RUN MODE] ---")
        print("\n=== TEXT DIGEST ===\n")
        print(text_digest)
        print("\n=== AUDIO SCRIPT (First 300 words) ===\n")
        print(" ".join(audio_script.split()[:300]) + "...\n")
        logger.info("Dry-run complete. Exiting without TTS or Telegram.")
        return

    # Step 4: Local TTS Audio Synthesis
    audio_files: list[Path] = []
    if not args.skip_tts:
        audio_files = synthesize_audio(audio_script, output_dir, config, today_str)
    else:
        logger.info("Skipping TTS synthesis per --skip-tts flag.")

    # Step 5: Dispatch to Telegram
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    send_to_telegram(text_digest, audio_files, bot_token, chat_id)

    logger.info("=== AI News Daily Briefing Pipeline Finished Successfully ===")


if __name__ == "__main__":
    main()
