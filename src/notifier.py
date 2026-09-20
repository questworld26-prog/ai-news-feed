"""
Notifier Module
Handles local audio synthesis with kokoro-mlx and Telegram dispatch (text digest + audio uploads).
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Any

import numpy as np
import requests
import soundfile as sf

logger = logging.getLogger("ai_briefing")


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

    logger.info(f"Sending text summary to Telegram chat {chat_id}...")
    text_endpoint = f"{base_url}/sendMessage"
    
    max_tg_len = 4000
    text_chunks = [text_digest[i:i + max_tg_len] for i in range(0, len(text_digest), max_tg_len)]

    for chunk in text_chunks:
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
