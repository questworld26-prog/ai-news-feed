"""
Notifier Module
Handles local audio synthesis with kokoro-mlx and Telegram dispatch (text digest + audio uploads).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import requests
import soundfile as sf

from model_provider import ModelProviderFactory

logger = logging.getLogger("ai_briefing")


def chunk_text(text: str, max_words: int = 150) -> list[str]:
    """
    Split script into sentence-bounded chunks of ~max_words
    to limit peak memory usage per synthesis call.
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


def unload_ollama_models(ollama_url: str = "http://localhost:11434", config: dict[str, Any] | None = None) -> None:
    """
    Explicitly offload any active LLM models from Ollama VRAM/unified memory
    to ensure full memory headroom for kokoro-mlx audio synthesis.
    """
    if config:
        try:
            provider = ModelProviderFactory.get_provider(config)
            provider.unload_models()
            return
        except Exception as e:
            logger.warning(f"Could not offload models via provider: {e}")

    cleaned_url = ollama_url.rstrip("/")
    try:
        ps_resp = requests.get(f"{cleaned_url}/api/ps", timeout=5)
        if ps_resp.ok:
            models = ps_resp.json().get("models", [])
            if not models:
                logger.debug("No active Ollama models loaded in memory.")
                return

            for m in models:
                m_name = m.get("name")
                if m_name:
                    logger.info(f"🧹 Offloading LLM '{m_name}' from unified memory for TTS headroom...")
                    requests.post(
                        f"{cleaned_url}/api/generate",
                        json={"model": m_name, "keep_alive": 0},
                        timeout=5,
                    )
    except Exception as e:
        logger.warning(f"Could not offload Ollama models: {e}")


def clear_mlx_memory() -> None:
    """Free MLX intermediate tensor buffers and run Python garbage collection."""
    import gc

    gc.collect()
    try:
        import mlx.core as mx

        if hasattr(mx, "clear_cache"):
            mx.clear_cache()
        elif hasattr(mx, "metal") and hasattr(mx.metal, "clear_cache"):
            mx.metal.clear_cache()
    except Exception as e:
        logger.debug(f"MLX cache clear skipped: {e}")


def synthesize_audio(
    script: str,
    output_dir: Path,
    config: dict[str, Any],
    date_str: str,
) -> list[Path]:
    """
    Synthesize speech using kokoro-mlx on Apple Silicon Metal.
    Offloads LLM models prior to synthesis and frees Metal tensor cache between chunks.
    Returns list of generated audio file paths (split if > max_file_size_mb).
    """
    # Step 1: Offload LLM weights from unified memory before allocating TTS models
    unload_ollama_models(config=config)
    clear_mlx_memory()

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
        finally:
            clear_mlx_memory()

    # Release TTS instance from memory after completion
    del tts
    clear_mlx_memory()

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
        logger.info(f"Saved audio briefing to {out_path} ({out_path.stat().st_size / (1024 * 1024):.1f} MB)")
    else:
        logger.info(
            f"Audio size ({raw_size_bytes / (1024 * 1024):.1f} MB) exceeds {max_mb} MB limit. Splitting into 2 parts."
        )
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
    Returns True if all dispatches succeeded, False otherwise.
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
    text_chunks = [text_digest[i : i + max_tg_len] for i in range(0, len(text_digest), max_tg_len)]

    overall_success = True

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
            overall_success = False

    audio_endpoint = f"{base_url}/sendAudio"
    for audio_path in audio_files:
        if not audio_path.exists():
            continue
        logger.info(f"Uploading audio file: {audio_path.name} ({audio_path.stat().st_size / (1024 * 1024):.1f} MB)...")
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
            overall_success = False

    return overall_success
