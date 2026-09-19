"""
AI News Voice Briefing Pipeline
Fetches AI headlines from curated RSS feeds, summarizes & formats with Ollama,
synthesizes voice audio locally with kokoro-mlx on Apple Silicon Metal,
and delivers markdown summaries + audio briefings to Telegram and local storage.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
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
    """Strip basic HTML tags and excessive whitespace."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_stories(config: dict[str, Any]) -> list[dict[str, str]]:
    """
    Fetch and prioritize AI stories across configured RSS feeds.
    Returns up to config['feeds']['max_stories'] articles.
    """
    feeds = config.get("feeds", {})
    sources = feeds.get("sources", [])
    max_stories = feeds.get("max_stories", 5)

    all_entries = []
    now = datetime.now(timezone.utc)

    logger.info(f"Fetching from {len(sources)} RSS feeds...")
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

                summary = clean_html_text(getattr(entry, "summary", "") or getattr(entry, "description", ""))
                title = clean_html_text(getattr(entry, "title", "Untitled"))
                link = getattr(entry, "link", "")

                if not title or not link:
                    continue

                all_entries.append({
                    "source": name,
                    "title": title,
                    "link": link,
                    "summary": summary[:400] if summary else "",
                    "pub_dt": pub_dt,
                })
        except Exception as e:
            logger.warning(f"Error fetching from {name}: {e}")

    # Sort newest first
    all_entries.sort(key=lambda x: x["pub_dt"], reverse=True)

    # Pick unique stories by link/title
    seen_urls = set()
    selected_stories = []
    for item in all_entries:
        if item["link"] in seen_urls:
            continue
        seen_urls.add(item["link"])
        selected_stories.append(item)
        if len(selected_stories) >= max_stories:
            break

    logger.info(f"Selected top {len(selected_stories)} stories for briefing.")
    return selected_stories


def generate_briefing_llm(stories: list[dict[str, str]], config: dict[str, Any]) -> dict[str, str]:
    """
    Call local Ollama endpoint with qwen2.5:3b to produce:
    1. text_digest: markdown summary with links for Telegram
    2. audio_script: ~1,400 words podcast host script, spoken English, no URLs or markdown
    """
    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "qwen2.5:3b")
    word_target = llm_cfg.get("script_word_target", 1400)

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

    system_prompt = (
        "You are a professional tech podcast host and senior AI systems engineer briefing an engineering colleague. "
        "Your style is conversational, sharp, engaging, and authoritative. "
        "You must output STRICT, VALID JSON with exactly two fields: 'text_digest' and 'audio_script'. "
        "Do NOT enclose the JSON in markdown code blocks like ```json ... ```. Return raw JSON only."
    )

    user_prompt = f"""Here are the top AI stories for today:

{stories_block}

Task:
Produce a JSON object with exactly two keys:
1. "text_digest": A rich markdown brief intended for reading on Telegram.
   - Start with a punchy title and date.
   - For each story, provide an insightful 2-sentence breakdown explaining why it matters technically, along with a markdown hyperlink to the original source.
   - End with a one-line conclusion.

2. "audio_script": A complete conversational monologue script for spoken audio (~{word_target} words).
   - Tone: Friendly, sharp colleague hosting a morning podcast briefing.
   - Spoken cadence: Natural transitions, conversational pacing ("Welcome back", "Let's dive into", "Now onto our next story").
   - STRICT RULES FOR AUDIO_SCRIPT:
     * Write purely phonetically friendly spoken words.
     * Absolutely NO markdown (no asterisks, hash signs, bullet points, brackets).
     * Absolutely NO URLs or website links (speak names of sources naturally instead, e.g., "reported on Simon Willison's blog" or "according to Anthropic").
     * Pronounce acronyms or clarify them naturally if needed.
     * Provide substantive depth for each of the {len(stories)} stories so the listener gets genuine technical takeaways.

Return ONLY the raw JSON object with keys "text_digest" and "audio_script".
"""

    logger.info(f"Calling Ollama ({model}) at {ollama_url}...")
    endpoint = f"{ollama_url}/api/generate"
    payload = {
        "model": model,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 8192,
        },
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=300)
        response.raise_for_status()
        result_json = response.json()
        raw_response = result_json.get("response", "").strip()

        # Parse JSON from model output
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                raise ValueError("Could not parse JSON from Ollama response")

        # Flexible key search (handling case differences or nested structure)
        text_digest = (
            data.get("text_digest")
            or data.get("textDigest")
            or data.get("digest")
            or data.get("summary")
        )
        audio_script = (
            data.get("audio_script")
            or data.get("audioScript")
            or data.get("script")
            or data.get("podcast_script")
        )

        if not text_digest or not audio_script:
            # Check if keys are nested under an outer key
            for k, v in data.items():
                if isinstance(v, dict):
                    if not text_digest:
                        text_digest = v.get("text_digest") or v.get("digest") or v.get("summary")
                    if not audio_script:
                        audio_script = v.get("audio_script") or v.get("script")

        if not text_digest or not audio_script:
            raise KeyError(f"JSON missing expected keys. Received keys: {list(data.keys())}")

        logger.info(f"Ollama generated script: ~{len(audio_script.split())} words.")
        return {"text_digest": text_digest, "audio_script": audio_script}

    except Exception as e:
        logger.error(f"Error during Ollama inference: {e}")
        # Graceful fallback: construct basic digest & script from raw stories
        logger.warning("Generating fallback digest & script from fetched stories.")
        digest_lines = ["# 🎙️ Daily AI Engineering Briefing\n"]
        script_parts = ["Good morning. Here is your daily artificial intelligence news briefing.\n"]
        for idx, s in enumerate(stories, 1):
            digest_lines.append(f"**{idx}. [{s['title']}]({s['link']})** ({s['source']})\n{s['summary']}\n")
            script_parts.append(f"Story number {idx}. From {s['source']}. {s['title']}. {s['summary']}. ")
        script_parts.append("That wraps up today's briefing. Have a productive day.")
        return {
            "text_digest": "\n".join(digest_lines),
            "audio_script": " ".join(script_parts),
        }


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

    # Estimate size in bytes for 16-bit PCM WAV (sample_rate * 2 bytes/sample)
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
    
    # Chunk text if exceeds Telegram 4096 limit
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
                # Retry without markdown parse_mode if formatting had invalid tags
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


def main() -> None:
    parser = argparse.ArgumentParser(description="AI News Daily Voice Briefing Pipeline")
    parser.add_argument("--config", default="config.toml", help="Path to config.toml")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and generate script only; skip TTS and Telegram")
    parser.add_argument("--skip-tts", action="store_true", help="Skip audio synthesis and only send text digest")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    config_path = project_root / args.config
    config = load_config(config_path)

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = project_root / config.get("output", {}).get("dir", "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== Starting AI News Daily Briefing Pipeline ===")

    # Step 1: RSS Aggregation
    stories = fetch_stories(config)
    if not stories:
        logger.error("No stories retrieved from any feeds. Exiting.")
        sys.exit(1)

    # Step 2: LLM Inference via Ollama
    briefing_data = generate_briefing_llm(stories, config)
    text_digest = briefing_data.get("text_digest", "")
    audio_script = briefing_data.get("audio_script", "")

    # Save outputs locally
    summary_file = output_dir / f"{today_str}_summary.md"
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

    # Step 3: Local TTS Audio Synthesis
    audio_files: list[Path] = []
    if not args.skip_tts:
        audio_files = synthesize_audio(audio_script, output_dir, config, today_str)
    else:
        logger.info("Skipping TTS synthesis per --skip-tts flag.")

    # Step 4: Dispatch to Telegram
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    send_to_telegram(text_digest, audio_files, bot_token, chat_id)

    logger.info("=== AI News Daily Briefing Pipeline Finished Successfully ===")


if __name__ == "__main__":
    main()
