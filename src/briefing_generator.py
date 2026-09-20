"""
LLM Briefing Generator Module
Handles Ollama curation of stories, text digest generation, spoken script generation,
and audio text sanitization.
"""

from __future__ import annotations

from datetime import datetime
import json
import logging
import re
from typing import Any

import requests

logger = logging.getLogger("ai_briefing")


def clean_script_for_audio(raw_script: str) -> str:
    """Remove URLs, bracketed paths, markdown formatting, and technical metadata from spoken scripts."""
    if not raw_script:
        return ""
    text = re.sub(r"(?i)\b(Article URL|Comments URL|Points|# Comments)\b:?\s*\S*", "", raw_script)
    text = re.sub(r"(?i)\b(URL|Link)\b:?\s*", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    text = re.sub(r"\[[a-zA-Z0-9\.\-/_ ]+\]", "", text)
    text = re.sub(r"(?i)(The link to the original source is|available at|you can read more at)\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"[*_#`~>|-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


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
    model = llm_cfg.get("model", "phi4-mini:3.8b")
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
    Call local Ollama endpoint to produce:
    1. text_digest: markdown summary with links for Telegram, prefixed with Theme header.
    2. audio_script: ~750 words podcast host script adhering to the theme's tone.
    """
    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "phi4-mini:3.8b")
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
        f"- For each of the {len(stories)} stories, write a section with a header using ONLY the markdown link format: `## [Story Title](URL)`. Do NOT repeat the title outside the brackets.\n"
        f"- Follow the header with a 2-sentence technical breakdown explaining why it matters.\n"
        f"- Do NOT add a separate 'Article URL', 'Link', or '[Read more]' line.\n"
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
            cleaned_digest = re.sub(r"```(?:markdown)?\s*", "", raw_digest, flags=re.IGNORECASE)
            cleaned_digest = re.sub(r"(?i)\n*(?:This (?:concise )?briefing encapsulates|This briefing provides).*$", "", cleaned_digest)
            text_digest = cleaned_digest.strip()
    except Exception as e:
        logger.error(f"Error generating text digest: {e}")

    if not text_digest:
        digest_lines = [f"### Daily AI Tech Briefing\n"]
        for idx, s in enumerate(stories, 1):
            digest_lines.append(f"## [{s['title']}]({s['link']})\n({s['source']})\n{s['summary']}\n")
        digest_lines.append("Stay curious and keep shipping.")
        text_digest = "\n".join(digest_lines)

    full_text_digest = f"{theme_badge}\n{text_digest.strip()}"

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
