"""
AI News Voice Briefing Pipeline
Fetches AI headlines from curated RSS feeds, summarizes & formats with Ollama,
synthesizes voice audio locally with kokoro-mlx on Apple Silicon Metal,
and delivers markdown summaries + audio briefings to Telegram and local storage.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from difflib import SequenceMatcher
import json
import logging
import os
from pathlib import Path
import random
import re
import sys
import time
import tomllib
from typing import Any

from dotenv import load_dotenv
import feedparser
import numpy as np
import requests
import soundfile as sf

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


def clean_html_text(raw_html: str) -> str:
    """Strip basic HTML tags, metadata lines, and excessive whitespace."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)
    # Strip common RSS boilerplate lines from HN/aggregators
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


def clean_script_for_audio(raw_script: str) -> str:
    """Remove URLs, bracketed paths, markdown formatting, and technical metadata from spoken scripts."""
    if not raw_script:
        return ""
    # Remove metadata lines first
    text = re.sub(r"(?i)\b(Article URL|Comments URL|Points|# Comments)\b:?\s*\S*", "", raw_script)
    text = re.sub(r"(?i)\b(URL|Link)\b:?\s*", "", text)
    # Remove URLs (http, https, www)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    # Remove bracketed domain paths e.g. [simonwillison.net/2026/Sep/18/...]
    text = re.sub(r"\[[a-zA-Z0-9\.\-/_ ]+\]", "", text)
    # Remove phrases like "The link to the original source is on ... at" or "available at"
    text = re.sub(r"(?i)(The link to the original source is|available at|you can read more at)\s*", "", text)
    # Remove markdown links [Text](url) -> Text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove leftover markdown symbols
    text = re.sub(r"[*_#`~>|-]", " ", text)
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def score_entry(entry: dict[str, Any]) -> float:
    """
    Compute a relevance score for a feed entry.
    Hacker News entries are boosted by popularity (points).
    All entries are boosted by recency (newer = higher score).
    """
    now = datetime.now(timezone.utc)
    age_hours = max(0.0, (now - entry["pub_dt"]).total_seconds() / 3600)
    # Recency score: decays over 48h window
    recency_score = max(0.0, 1.0 - (age_hours / 48.0))

    # Popularity boost: use entry['points'] if available or regex fallback
    popularity_score = 0.0
    if "Hacker News" in entry.get("source", ""):
        points = entry.get("points", 0)
        if not points:
            points_match = re.search(r"Points:\s*(\d+)", entry.get("summary", ""))
            if points_match:
                points = int(points_match.group(1))
        if points:
            popularity_score = min(1.0, points / 200.0)

    # Combined score: 60% recency, 40% popularity
    return (0.6 * recency_score) + (0.4 * popularity_score)


def matches_hard_filters(title: str, summary: str, hard_filters: list[str]) -> bool:
    """Check if title or summary contains any excluded terms."""
    full_text = f"{title} {summary}".lower()
    for term in hard_filters:
        if term.lower() in full_text:
            return True
    return False


def fetch_stories_for_theme(theme_dict: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Fetch AI stories from RSS feeds specific to a chosen theme.
    Filters out noise using hard_filters, scores remaining stories,
    deduplicates fuzzy titles, and returns a candidate pool.
    """
    sources = theme_dict.get("sources", [])
    hard_filters = theme_dict.get("hard_filters", [])
    candidate_pool_size = config.get("feeds", {}).get("candidate_pool_size", 15)

    all_entries = []
    now = datetime.now(timezone.utc)

    logger.info(f"Fetching from {len(sources)} sources for theme '{theme_dict.get('name')}'...")
    for src in sources:
        name = src.get("name", "Unknown")
        url = src.get("url", "")
        if not url:
            continue

        try:
            logger.info(f"Querying feed: {name}...")
            parsed = feedparser.parse(
                url,
                request_headers={"User-Agent": "Mozilla/5.0 (compatible; AIBriefingBot/1.0)"}
            )

            if parsed.bozo and not parsed.entries:
                logger.warning(f"Could not parse entries from {name}: {parsed.bozo_exception}")
                continue

            for entry in parsed.entries:
                pub_parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
                if pub_parsed:
                    pub_dt = datetime(*pub_parsed[:6], tzinfo=timezone.utc)
                else:
                    pub_dt = now

                raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                points_match = re.search(r"Points:\s*(\d+)", raw_summary)
                points = int(points_match.group(1)) if points_match else 0

                summary = clean_html_text(raw_summary)
                title = clean_html_text(getattr(entry, "title", "Untitled"))
                link = getattr(entry, "link", "")

                if not title or not link:
                    continue

                if matches_hard_filters(title, summary, hard_filters):
                    logger.debug(f"Filtered out by theme hard filter: {title}")
                    continue

                all_entries.append({
                    "source": name,
                    "title": title,
                    "link": link,
                    "summary": summary[:400] if summary else "",
                    "pub_dt": pub_dt,
                    "points": points,
                })
        except Exception as e:
            logger.warning(f"Error fetching from {name}: {e}")

    # Score and sort: highest score first
    for entry in all_entries:
        entry["score"] = score_entry(entry)
    all_entries.sort(key=lambda x: x["score"], reverse=True)

    # Fuzzy title deduplication and source-diversity capping -> build candidate pool
    candidate_pool = []
    source_counts: dict[str, int] = {}
    max_per_source = 2  # Max stories from any single RSS feed in candidate pool

    for item in all_entries:
        src = item["source"]
        if source_counts.get(src, 0) >= max_per_source:
            continue

        is_dup = any(is_similar_title(item["title"], existing["title"]) for existing in candidate_pool)
        if is_dup:
            logger.debug(f"Skipping duplicate: '{item['title'][:60]}...' (source: {item['source']})")
            continue

        candidate_pool.append(item)
        source_counts[src] = source_counts.get(src, 0) + 1
        if len(candidate_pool) >= candidate_pool_size:
            break

    # If pool is smaller than candidate_pool_size, backfill from remaining entries
    if len(candidate_pool) < candidate_pool_size:
        for item in all_entries:
            if item in candidate_pool:
                continue
            is_dup = any(is_similar_title(item["title"], existing["title"]) for existing in candidate_pool)
            if not is_dup:
                candidate_pool.append(item)
                if len(candidate_pool) >= candidate_pool_size:
                    break

    logger.info(f"Built candidate pool of {len(candidate_pool)} unique stories across {len(source_counts)} sources for '{theme_dict.get('name')}'.")
    return candidate_pool


def llm_curate_stories(
    candidates: list[dict[str, Any]],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Stage 2 story selection: ask Ollama to pick the most relevant stories
    matching the current theme. Returns max_stories entries.
    """
    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "qwen2.5:3b")
    max_stories = config.get("feeds", {}).get("max_stories", 5)

    if len(candidates) <= max_stories:
        return candidates

    story_list = ""
    for idx, s in enumerate(candidates, 1):
        story_list += f"{idx}. [{s['source']}] {s['title']}\n   {s['summary'][:200]}\n\n"

    prompt = (
        f"You are an expert AI engineer curating a briefing on the theme '{theme_dict.get('name')}'.\n"
        f"Theme Description: {theme_dict.get('description')}\n"
        f"Audience & Tone: {theme_dict.get('tone')}\n\n"
        f"From the {len(candidates)} candidate stories below, select the top {max_stories} stories "
        f"that BEST fit this theme. Favor concrete technical implementations, tools, real architectural patterns, "
        f"or creative breakthroughs. Exclude hype, trivial announcements, or funding deals.\n\n"
        f"Return ONLY a JSON object with a single key 'selected' containing a list of {max_stories} "
        f"integer indices (1-based) in priority order.\n"
        f"Example: {{\"selected\": [3, 1, 7, 12, 5]}}\n\n"
        f"Stories:\n{story_list}"
    )

    logger.info(f"LLM curation: asking {model} to pick {max_stories} stories for theme '{theme_dict.get('name')}'...")
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 4096},
            },
            timeout=120,
        )
        response.raise_for_status()
        raw = response.json().get("response", "").strip()
        data = json.loads(raw)
        indices = data.get("selected", [])

        valid_indices = [i for i in indices if isinstance(i, int) and 1 <= i <= len(candidates)]
        if len(valid_indices) < max_stories:
            logger.warning(f"LLM returned {len(valid_indices)} valid indices, expected {max_stories}. Padding with top-scored.")
            seen = set(valid_indices)
            for i in range(1, len(candidates) + 1):
                if i not in seen:
                    valid_indices.append(i)
                    if len(valid_indices) >= max_stories:
                        break

        curated = [candidates[i - 1] for i in valid_indices[:max_stories]]
        titles = [f"  {i}. {s['title'][:55]}..." for i, s in zip(valid_indices, curated)]
        logger.info(f"LLM curated {max_stories} stories:\n" + "\n".join(titles))
        return curated

    except Exception as e:
        logger.warning(f"LLM curation failed ({e}). Falling back to top-{max_stories} by popularity/recency score.")
        return candidates[:max_stories]


def generate_briefing_llm(
    stories: list[dict[str, Any]],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
    text_only: bool = False,
) -> dict[str, str]:
    """
    Call local Ollama endpoint with qwen2.5:3b to produce:
    1. text_digest: markdown summary with links for Telegram, prefixed with Theme header.
    2. audio_script: ~750 words podcast host script adhering to the theme's tone.
    """
    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "qwen2.5:3b")
    word_target = llm_cfg.get("script_word_target", 750)

    theme_badge = f"{theme_dict.get('emoji', '🎙️')} **{theme_dict.get('name', 'Daily Briefing')}**\n_{theme_dict.get('description', '')}_\n"

    stories_context = []
    for idx, s in enumerate(stories, 1):
        stories_context.append(
            f"Story {idx}:\n"
            f"- Title: {s['title']}\n"
            f"- Source: {s['source']}\n"
            f"- Link: {s['link']}\n"
            f"- Summary: {s['summary']}\n"
        )
    stories_block = "\n".join(stories_context)

    logger.info(f"Generating text digest for theme '{theme_dict.get('name')}'...")
    text_digest = ""
    audio_script = ""

    today_date = datetime.now().strftime("%B %d, %Y")
    digest_prompt = (
        f"You are an expert AI systems engineer and tech writer. Today's theme: '{theme_dict.get('name')}'.\n"
        f"Theme Description: {theme_dict.get('description')}.\n"
        f"Date: {today_date}\n\n"
        f"Here are the top AI stories:\n{stories_block}\n\n"
        f"Task:\n"
        f"Write a rich, concise markdown briefing suitable for Telegram:\n"
        f"- Start directly with a sharp headline and today's date ({today_date}). Never write '[Current Date]'.\n"
        f"- For each of the {len(stories)} stories, write a 2-sentence technical breakdown explaining why it matters and include the markdown link to the source.\n"
        f"- Output raw markdown only. Do NOT enclose in markdown code blocks (no ```). Do NOT add closing meta-commentary."
    )

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": digest_prompt,
                "stream": False,
                "options": {"temperature": 0.4, "num_ctx": 4096},
            },
            timeout=180,
        )
        resp.raise_for_status()
        raw_digest = resp.json().get("response", "").strip()
        if raw_digest:
            # Strip enclosing markdown code fences anywhere in the string
            cleaned_digest = re.sub(r"```(?:markdown)?\s*", "", raw_digest, flags=re.IGNORECASE)
            # Remove trailing meta commentary like "This briefing provides a concise yet..."
            cleaned_digest = re.sub(r"(?i)\n*(?:This (?:concise )?briefing encapsulates|This briefing provides).*$", "", cleaned_digest)
            text_digest = cleaned_digest.strip()
    except Exception as e:
        logger.error(f"Error generating text digest: {e}")

    # Fallback text digest if generation failed
    if not text_digest:
        digest_lines = [f"### Daily AI Tech Briefing\n"]
        for idx, s in enumerate(stories, 1):
            digest_lines.append(f"**{idx}. [{s['title']}]({s['link']})** ({s['source']})\n{s['summary']}\n")
        digest_lines.append("Stay curious and keep shipping.")
        text_digest = "\n".join(digest_lines)

    full_text_digest = f"{theme_badge}\n{text_digest.strip()}"

    # Step 2: Audio Script Generation (if not text_only)
    if not text_only:
        logger.info(f"Generating spoken audio script (~{word_target} words) for theme '{theme_dict.get('name')}'...")
        script_prompt = (
            f"You are a professional tech podcast host briefing an engineering peer. "
            f"Today's thematic lens is: '{theme_dict.get('name')}'. Tone: {theme_dict.get('tone')}.\n\n"
            f"Here are the stories to cover:\n{stories_block}\n\n"
            f"Task:\n"
            f"Write a complete, natural spoken podcast monologue script of approximately {word_target} words.\n"
            f"STRICT RULES:\n"
            f"- Open smoothly with today's theme (e.g., 'Welcome back. Today we're looking through our {theme_dict.get('name')} lens...').\n"
            f"- Walk through all {len(stories)} stories with natural conversational transitions and genuine technical depth.\n"
            f"- Write phonetically clean spoken English: absolutely NO markdown asterisks, hashes, bullets, brackets, or code symbols.\n"
            f"- Absolutely NO URLs, domain names, links, or 'available at' phrases.\n"
            f"- Conclude with a warm, professional wrap-up.\n"
            f"Output ONLY the spoken script text."
        )
        try:
            resp_audio = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": script_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_ctx": 4096},
                },
                timeout=240,
            )
            resp_audio.raise_for_status()
            raw_audio = resp_audio.json().get("response", "").strip()
            audio_script = clean_script_for_audio(raw_audio)
        except Exception as e:
            logger.error(f"Error generating audio script: {e}")

        # Fallback audio script if failed
        if not audio_script or len(audio_script.split()) < 40:
            logger.warning("Using fallback audio script from stories.")
            script_parts = [f"Welcome to today's {theme_dict.get('name')} briefing. "]
            for idx, s in enumerate(stories, 1):
                clean_t = clean_script_for_audio(s['title'])
                clean_s = clean_script_for_audio(s['summary'])
                script_parts.append(f"Story number {idx}. From {s['source']}. {clean_t}. {clean_s}. ")
            script_parts.append("That concludes today's theme update.")
            audio_script = clean_script_for_audio(" ".join(script_parts))

    logger.info(f"Generated text digest and audio script (~{len(audio_script.split())} words).")
    return {"text_digest": full_text_digest, "audio_script": audio_script}


def chunk_text(text: str, max_words: int = 150) -> list[str]:
    """
    Split script into sentence-bounded chunks of ~max_words
    to keep memory footprint minimal on 8GB Apple Silicon M1.
    """
    sentences = re.split(r"(?<=[.?!])\s+", text.strip())
    chunks = []
    curr_chunk = []
    curr_words = 0

    for sentence in sentences:
        words = len(sentence.split())
        if curr_words + words > max_words and curr_chunk:
            chunks.append(" ".join(curr_chunk))
            curr_chunk = [sentence]
            curr_words = words
        else:
            curr_chunk.append(sentence)
            curr_words += words

    if curr_chunk:
        chunks.append(" ".join(curr_chunk))

    return [c.strip() for c in chunks if c.strip()]


def synthesize_audio(
    script: str,
    output_dir: Path,
    config: dict[str, Any],
    date_str: str,
) -> list[Path]:
    """
    Synthesize speech using kokoro-mlx on Apple Silicon Metal.
    Returns list of generated audio file paths (split if > max_file_size_mb).
    """
    tts_cfg = config.get("tts", {})
    voice = tts_cfg.get("voice", "bm_george")
    speed = float(tts_cfg.get("speed", 1.0))
    sample_rate = int(tts_cfg.get("sample_rate", 24000))
    chunk_words = int(tts_cfg.get("chunk_words", 150))
    max_mb = float(config.get("output", {}).get("max_file_size_mb", 45.0))

    logger.info(f"Initializing KokoroTTS (voice={voice}, speed={speed})...")
    from kokoro_mlx import KokoroTTS
    tts = KokoroTTS.from_pretrained()

    chunks = chunk_text(script, max_words=chunk_words)
    logger.info(f"Synthesizing {len(chunks)} chunks sequentially for memory efficiency...")

    audio_segments = []
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Generating audio chunk {i}/{len(chunks)} ({len(chunk.split())} words)...")
        try:
            res = tts.generate(text=chunk, voice=voice, speed=speed, sample_rate=sample_rate)
            audio_segments.append(np.array(res.audio, dtype=np.float32))
        except Exception as e:
            logger.warning(f"Failed to synthesize chunk {i}: {e}")

    if not audio_segments:
        logger.error("No audio segments synthesized.")
        return []

    combined_audio = np.concatenate(audio_segments)
    duration_secs = len(combined_audio) / sample_rate
    logger.info(f"Total audio synthesized: {duration_secs:.1f} seconds ({duration_secs / 60:.1f} minutes).")

    raw_size_bytes = len(combined_audio) * 2
    max_bytes = max_mb * 1024 * 1024

    output_files = []
    if raw_size_bytes <= max_bytes:
        out_path = output_dir / f"{date_str}_briefing.wav"
        sf.write(str(out_path), combined_audio, sample_rate, subtype="PCM_16")
        output_files.append(out_path)
        logger.info(f"Saved audio briefing to {out_path} ({out_path.stat().st_size / (1024*1024):.1f} MB)")
    else:
        logger.info(f"Audio size ({raw_size_bytes / (1024*1024):.1f} MB) exceeds {max_mb} MB limit. Splitting into 2 parts.")
        midpoint = len(combined_audio) // 2
        part1_path = output_dir / f"{date_str}_briefing_part1.wav"
        part2_path = output_dir / f"{date_str}_briefing_part2.wav"

        sf.write(str(part1_path), combined_audio[:midpoint], sample_rate, subtype="PCM_16")
        sf.write(str(part2_path), combined_audio[midpoint:], sample_rate, subtype="PCM_16")

        output_files.extend([part1_path, part2_path])
        logger.info(f"Saved split audio: {part1_path.name} and {part2_path.name}")

    return output_files


def send_to_telegram(
    text_digest: str,
    audio_files: list[Path],
    bot_token: str,
    chat_id: str,
) -> bool:
    """
    Send formatted markdown summary and audio files to Telegram bot.
    """
    bot_token = bot_token.strip().strip("'").strip('"')
    chat_id = chat_id.strip().strip("'").strip('"')

    if not bot_token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not provided. Skipping Telegram dispatch.")
        return False

    base_url = f"https://api.telegram.org/bot{bot_token}"

    # 1. Send Text Digest (split if > 4000 chars)
    logger.info(f"Sending text summary to Telegram chat {chat_id}...")
    text_endpoint = f"{base_url}/sendMessage"
    
    max_tg_len = 4000
    text_chunks = [text_digest[i:i + max_tg_len] for i in range(0, len(text_digest), max_tg_len)]

    for idx, chunk in enumerate(text_chunks):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }
        try:
            r = requests.post(text_endpoint, json=payload, timeout=30)
            if not r.ok:
                logger.warning(f"Telegram sendMessage failed ({r.text}). Retrying with plain text...")
                payload.pop("parse_mode", None)
                r = requests.post(text_endpoint, json=payload, timeout=30)
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send Telegram text message: {e}")

    # 2. Send Audio Files
    audio_endpoint = f"{base_url}/sendAudio"
    for audio_path in audio_files:
        if not audio_path.exists():
            continue
        logger.info(f"Uploading audio file: {audio_path.name} ({audio_path.stat().st_size / (1024*1024):.1f} MB)...")
        try:
            with open(audio_path, "rb") as f:
                files = {"audio": (audio_path.name, f, "audio/wav")}
                data = {
                    "chat_id": chat_id,
                    "title": audio_path.stem.replace("_", " ").title(),
                    "performer": "AI Daily Briefing",
                }
                r = requests.post(audio_endpoint, data=data, files=files, timeout=120)
                r.raise_for_status()
                logger.info(f"Successfully uploaded {audio_path.name} to Telegram!")
        except Exception as e:
            logger.error(f"Failed to upload audio {audio_path.name} to Telegram: {e}")

    return True


def run_all_themes(config: dict[str, Any], output_dir: Path, today_str: str) -> None:
    """
    Generate a comprehensive multi-theme digest covering all themes.
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
    parser.add_argument("--config", default="config.toml", help="Path to config.toml")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and generate script only; skip TTS and Telegram")
    parser.add_argument("--skip-tts", action="store_true", help="Skip audio synthesis and only send text digest")
    parser.add_argument("--all-themes", action="store_true", help="Generate full digest for all 4 themes in dry-run mode")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    config_path = project_root / args.config
    config = load_config(config_path)

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = project_root / config.get("output", {}).get("dir", "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # All-themes mode branch (bypasses weekday gate for deliberate manual runs)
    if args.all_themes:
        run_all_themes(config, output_dir, today_str)
        return

    # Check weekday gate (0=Monday, 6=Sunday)
    weekday = datetime.now().weekday()
    weekdays_only = config.get("schedule", {}).get("weekdays_only", True)
    if weekdays_only and weekday >= 5 and not args.dry_run:
        logger.info(f"Today is {'Saturday' if weekday == 5 else 'Sunday'} and weekdays_only is enabled. Skipping scheduled briefing.")
        sys.exit(0)

    # Pick random theme for the day
    themes = config.get("themes", {})
    if not themes:
        logger.error("No themes found in config.toml under [themes].")
        sys.exit(1)

    theme_key = random.choice(list(themes.keys()))
    theme_dict = themes[theme_key]
    logger.info(f"=== Selected Daily Theme: {theme_dict.get('emoji')} {theme_dict.get('name')} ===")

    # Step 1: RSS Aggregation for selected theme -> candidate pool
    candidates = fetch_stories_for_theme(theme_dict, config)
    if not candidates:
        logger.error(f"No stories retrieved for theme {theme_key}. Exiting.")
        sys.exit(1)

    # Step 2: LLM Curation -> pick top max_stories
    stories = llm_curate_stories(candidates, theme_dict, config)

    # Step 3: LLM Script & Digest Generation via Ollama
    briefing_data = generate_briefing_llm(stories, theme_dict, config)
    text_digest = briefing_data.get("text_digest", "")
    audio_script = briefing_data.get("audio_script", "")

    # Save outputs locally
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
