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
    generate_briefing_llm,
    llm_curate_stories,
)
from news_fetcher import fetch_stories_for_theme
from notifier import send_to_telegram, synthesize_audio
from quality_tracker import QualityTracker, get_current_git_commit
from telemetry import PipelineTracker

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
    parser.add_argument(
        "--theme",
        default="auto",
        help="Specify theme key, 'auto' (LAYA story-driven dynamic routing), or 'random'",
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

    tracker = PipelineTracker()

    theme_choice = args.theme.strip().lower() if args.theme else "auto"
    theme_key = None

    with tracker.track_stage("Phase 0: Theme Selection", {"strategy": theme_choice}) as stage:
        if theme_choice in themes:
            theme_key = theme_choice
            logger.info(f"Explicit theme selected via CLI: '{theme_key}'")
            stage.set_metric("method", "CLI Explicit")
        elif theme_choice == "random":
            theme_key = random.choice(list(themes.keys()))
            logger.info(f"Random theme selected: '{theme_key}'")
            stage.set_metric("method", "Random")
        else:
            # Option 5: Story-Driven Dynamic Theme Routing via LAYA System 1
            laya_cfg = config.get("laya", {})
            if laya_cfg.get("enabled", True) and laya_cfg.get("enable_theme_routing", True):
                try:
                    from news_fetcher import sample_breaking_headlines
                    from laya_decision import get_laya_engine

                    logger.info("📡 Sampling breaking headlines for LAYA dynamic theme routing...")
                    samples = sample_breaking_headlines(config, max_items=12)
                    if samples:
                        engine = get_laya_engine(config)
                        theme_key, score_dist = engine.route_theme_from_stories(samples, themes, config)
                        logger.info(f"🎯 LAYA dynamic theme routing selected: '{theme_key}' (Signal distribution: {score_dist})")
                        stage.set_metric("method", "LAYA System 1")
                        stage.set_metric("headlines_sampled", len(samples))
                except Exception as exc:
                    logger.warning(f"LAYA theme routing error: {exc}. Falling back to random choice.")

            if not theme_key or theme_key not in themes:
                theme_key = random.choice(list(themes.keys()))
                stage.set_metric("method", "Fallback Random")

        stage.set_metric("selected_theme", theme_key)

    theme_dict = themes[theme_key]
    logger.info("=" * 60)
    logger.info(f"🎙️  AI NEWS DAILY BRIEFING PIPELINE — {today_str}")
    logger.info(f"🎯 Selected Theme: {theme_dict.get('emoji')} {theme_dict.get('name')}")
    logger.info("=" * 60)

    # -------------------------------------------------------------
    # PHASE 1: RSS Ingestion & Pre-Filtering
    # -------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("📡 PHASE 1: RSS Ingestion & Feed Aggregation")
    logger.info("=" * 60)
    with tracker.track_stage("Phase 1: RSS Ingestion", {"sources": len(theme_dict.get("sources", []))}) as stage:
        candidates = fetch_stories_for_theme(theme_dict, config)
        stage.set_metric("candidates_pool", len(candidates))

    if not candidates:
        logger.error(f"No stories retrieved for theme {theme_key}. Exiting.")
        tracker.print_summary_dashboard()
        sys.exit(1)

    # -------------------------------------------------------------
    # PHASE 2: LLM Curation & Prioritization
    # -------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("🧠 PHASE 2: LLM Story Curation & Theme Prioritization")
    logger.info("=" * 60)
    with tracker.track_stage("Phase 2: Story Curation", {"candidates_in": len(candidates)}) as stage:
        stories = llm_curate_stories(candidates, theme_dict, config)
        stage.set_metric("curated_stories", len(stories))

    # -------------------------------------------------------------
    # PHASE 3 & 4: Validated Summaries & Spoken Script Generation
    # -------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("📝 PHASE 3 & 4: Story Summaries Validation & Audio Scripting")
    logger.info("=" * 60)
    with tracker.track_stage("Phase 3 & 4: Synthesis & Validation", {"curated_stories": len(stories)}) as stage:
        briefing_data = generate_briefing_llm(stories, theme_dict, config)
        text_digest = briefing_data.text_digest
        audio_script = briefing_data.audio_script
        stage.set_metric("digest_words", len(text_digest.split()))
        stage.set_metric("script_words", len(audio_script.split()))

    summary_file = output_dir / f"{today_str}_{theme_key}_summary.md"
    summary_file.write_text(briefing_data.to_markdown(), encoding="utf-8")
    logger.info(f"💾 Saved markdown briefing digest to: {summary_file}")

    # Log quality metrics into SQLite database (eval/quality.db)
    try:
        qt = QualityTracker()
        run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"run_{run_ts}_{theme_key}"
        git_commit = get_current_git_commit()

        models_used = {
            "curation": config.get("llm", {}).get("curation_model") or config.get("llm", {}).get("model", "phi4-mini:3.8b"),
            "summary": config.get("llm", {}).get("summary_model") or config.get("llm", {}).get("model", "qwen2.5:3b"),
            "script": config.get("llm", {}).get("script_model") or config.get("llm", {}).get("model", "phi4-mini:3.8b"),
            "audit": config.get("testing", {}).get("audit_model", "qwen2.5:3b"),
            "theme_router": config.get("laya", {}).get("model_id", "convaiinnovations/laya"),
            "tts_voice": config.get("tts", {}).get("voice", "bm_george"),
        }

        total_duration = sum(r.duration_s for r in tracker.records)
        p3_record = next((r for r in tracker.records if "Phase 3" in r.name), None)
        phase3_dur = p3_record.duration_s if p3_record else 0.0
        phase3_delta = p3_record.mem_delta_mb if p3_record else 0.0
        phase3_rss = p3_record.mem_end_mb if p3_record else 0.0

        metadata = getattr(briefing_data, "metadata", {}) or {}
        factcheck_passed = metadata.get("audio_factcheck_passed", True)
        factcheck_retries = metadata.get("audio_factcheck_attempts", 1)

        qt.log_run(
            run_id=run_id,
            run_date=today_str,
            git_commit=git_commit,
            models_used=models_used,
            theme=theme_key,
            strategy=theme_choice,
            total_duration_s=total_duration,
            phase3_duration_s=phase3_dur,
            phase3_mem_delta_mb=phase3_delta,
            phase3_mem_rss_mb=phase3_rss,
            stories=briefing_data.stories,
            audio_script=briefing_data.audio_script,
            audio_script_target=config.get("llm", {}).get("script_word_target", 750),
            factcheck_passed=factcheck_passed,
            factcheck_retries=factcheck_retries,
            theme_dict=theme_dict,
        )
        logger.info(f"📈 Quality metrics logged to SQLite (eval/quality.db) [Run ID: {run_id}]")
    except Exception as exc:
        logger.warning(f"Failed to record quality metrics to database: {exc}")

    if args.dry_run:
        logger.info("\n" + "=" * 60)
        logger.info("🏁 DRY-RUN MODE COMPLETE")
        logger.info("=" * 60)
        print("\n=== TEXT DIGEST ===\n")
        print(text_digest)
        print("\n=== AUDIO SCRIPT (First 300 words) ===\n")
        print(" ".join(audio_script.split()[:300]) + "...\n")
        tracker.print_summary_dashboard()
        logger.info("Dry-run finished. Exiting without TTS or Telegram.")
        return

    # -------------------------------------------------------------
    # PHASE 5: Local TTS Audio Synthesis
    # -------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("🔊 PHASE 5: Local Voice Audio Synthesis (kokoro-mlx)")
    logger.info("=" * 60)
    audio_files: list[Path] = []
    if not args.skip_tts:
        with tracker.track_stage("Phase 5: Local TTS Audio Synthesis", {"voice": config.get("tts", {}).get("voice", "bm_george")}) as stage:
            audio_files = synthesize_audio(audio_script, output_dir, config, today_str)
            total_audio_mb = sum(f.stat().st_size for f in audio_files) / (1024 * 1024) if audio_files else 0.0
            stage.set_metric("audio_clips", len(audio_files))
            stage.set_metric("total_audio_mb", f"{total_audio_mb:.2f} MB")
    else:
        logger.info("⏩ Skipping TTS synthesis per --skip-tts flag.")

    # -------------------------------------------------------------
    # PHASE 6: Telegram Dispatch
    # -------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("🚀 PHASE 6: Telegram Notification & Media Upload")
    logger.info("=" * 60)
    with tracker.track_stage("Phase 6: Telegram Dispatch", {"audio_clips": len(audio_files)}) as stage:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        send_to_telegram(text_digest, audio_files, bot_token, chat_id)
        stage.set_metric("status", "Sent" if (bot_token and chat_id) else "Mocked / Skipped")

    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)
    tracker.print_summary_dashboard()


if __name__ == "__main__":
    main()
