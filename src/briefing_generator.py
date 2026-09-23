"""
LLM Briefing Generator Module
Handles Ollama curation of stories, text digest generation, spoken script generation,
and audio text sanitization.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import requests
from pydantic import BaseModel, Field

from story import BriefingOutput, Story

logger = logging.getLogger("ai_briefing")


class StorySelectionJustification(BaseModel):
    index: int = Field(description="1-based integer index of the candidate story")
    reasoning: str = Field(description="Brief technical justification for why this story was selected")


class CurationResponse(BaseModel):
    evaluation_criteria: str = Field(
        description="Summary of theme evaluation criteria applied when curating candidate stories"
    )
    justifications: list[StorySelectionJustification] = Field(
        description="Step-by-step justification for each selected story before outputting final indices"
    )
    selected: list[int] = Field(
        description="List of 1-based integer candidate indices of selected stories in priority order"
    )


def clean_script_for_audio(raw_script: str) -> str:
    """Remove URLs, bracketed paths, markdown formatting, and technical metadata from spoken scripts."""
    if not raw_script:
        return ""
    text = re.sub(r"(?i)\b(Article URL|Comments URL|Points|# Comments)\b:?\s*\S*", "", raw_script)
    text = re.sub(r"(?i)\b(URL|Link)\b:?\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    text = re.sub(r"\[[a-zA-Z0-9\.\-/_ ]+\]", "", text)
    text = re.sub(r"(?i)(The link to the original source is|available at|you can read more at)\s*", "", text)
    text = re.sub(r"[*_#`~>|-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def llm_curate_stories(
    candidates: list[Story | dict[str, Any]],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
) -> list[Story]:
    """
    Stage 2 story selection: ask local SLM (Ollama) to pick the top max_stories
    matching the current theme using Pydantic schema-constrained CoT curation.
    """
    typed_candidates = [c if isinstance(c, Story) else Story.from_dict(c) for c in candidates]

    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "phi4-mini:3.8b")
    max_stories = config.get("feeds", {}).get("max_stories", 5)

    if len(typed_candidates) <= max_stories:
        return typed_candidates

    story_list = ""
    for idx, s in enumerate(typed_candidates, 1):
        story_list += f"{s.to_prompt_context(idx=idx, max_summary_chars=200)}\n\n"

    prompt = (
        f"You are an expert AI technical editor curating a daily briefing for senior engineers.\n"
        f"Theme Name: '{theme_dict.get('name')}'\n"
        f"Theme Description: {theme_dict.get('description')}\n"
        f"Target Audience & Tone: {theme_dict.get('tone')}\n\n"
        f"Task:\n"
        f"Select the top {max_stories} stories from the {len(typed_candidates)} candidate stories below.\n"
        f"Favor concrete technical implementations, open-source tools, system architectures, or major breakthroughs.\n"
        f"Exclude generic hype, corporate press releases, or non-technical funding announcements.\n\n"
        f"Instructions:\n"
        f"1. State your specific 'evaluation_criteria' for this theme.\n"
        f"2. Provide step-by-step 'justifications' explaining why each candidate story was chosen.\n"
        f"3. Output the final top {max_stories} 1-based integer indices in 'selected' in priority order.\n\n"
        f"Candidate Stories:\n{story_list}"
    )

    logger.info(f"LLM curation: querying {model} with CoT schema for theme '{theme_dict.get('name')}'...")
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": CurationResponse.model_json_schema(),
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 4096},
            },
            timeout=120,
        )
        response.raise_for_status()
        raw = response.json().get("response", "").strip()
        curation_data = json.loads(raw)
        curation_res = CurationResponse.model_validate(curation_data)

        # Print / Log Chain-of-Thought Evaluation Criteria & Justifications
        logger.info(f"\n=== LLM CURATION CRITERIA ({theme_dict.get('name')}) ===")
        logger.info(f"Evaluation Criteria: {curation_res.evaluation_criteria}\n")

        for j in curation_res.justifications:
            if 1 <= j.index <= len(typed_candidates):
                cand_title = typed_candidates[j.index - 1].title
                logger.info(f"  • Story #{j.index} [{cand_title[:50]}...]: {j.reasoning}")

        # Defensive Post-Processing: Deduplicate, Bounds-check, and Pad
        valid_indices: list[int] = []
        seen: set[int] = set()
        for idx in curation_res.selected:
            if isinstance(idx, int) and 1 <= idx <= len(typed_candidates) and idx not in seen:
                valid_indices.append(idx)
                seen.add(idx)

        # Fallback / Deterministic padding if LLM selected fewer than max_stories
        if len(valid_indices) < max_stories:
            logger.warning(
                f"LLM returned {len(valid_indices)} valid unique indices out of {max_stories}. Deterministically padding with top-scored candidate stories."
            )
            # Rank candidates by score to fill remaining slots
            sorted_candidates_by_score = sorted(
                enumerate(typed_candidates, 1), key=lambda pair: pair[1].score, reverse=True
            )
            for idx, _ in sorted_candidates_by_score:
                if idx not in seen:
                    valid_indices.append(idx)
                    seen.add(idx)
                    if len(valid_indices) >= max_stories:
                        break

        curated = [typed_candidates[i - 1] for i in valid_indices[:max_stories]]
        logger.info(f"\nLLM curated top {len(curated)} stories successfully.")
        return curated

    except Exception as e:
        logger.warning(
            f"LLM curation schema parsing/generation failed ({e}). Falling back to top-{max_stories} by score."
        )
        sorted_candidates = sorted(typed_candidates, key=lambda s: s.score, reverse=True)
        return sorted_candidates[:max_stories]


class StorySummaryResponse(BaseModel):
    analysis: str = Field(
        description="Brief step-by-step analysis of facts, figures, and concepts explicitly stated in the source text"
    )
    summary: str = Field(
        description="EXACTLY 2 short sentences summarizing the story for a senior technical audience, using ONLY facts from the source text"
    )


# Fallback text used when a story's summary cannot pass fact-checking after all retries.
STORY_FALLBACK_SUMMARY = "⚠️ Failed to generate a reliable summary. Read the original article."


def generate_story_summary(
    story: Story | dict[str, Any],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
    correction_hint: str = "",
) -> str:
    """
    Generate a concise 2-sentence markdown summary for a single story.

    If *correction_hint* is provided (from a failed fact-check), it is injected
    into the prompt so the model can correct the previous attempt.
    Returns the raw summary text (no header), or "" on LLM failure.
    """
    s_obj = story if isinstance(story, Story) else Story.from_dict(story)

    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "phi4-mini:3.8b")

    correction_block = (
        f"\n\nCRITICAL FIX NEEDED FOR PREVIOUS FAILING ATTEMPT:\n"
        f"Fact-checker error reasoning: {correction_hint}\n"
        f"You MUST fix this. Strictly rely ONLY on text present in the Title and Summary above. "
        f"Remove all figures, technical terms, background domain knowledge, or links not explicitly mentioned in the source."
        if correction_hint.strip()
        else ""
    )

    prompt = (
        f"You are an expert AI tech writer. Briefing theme: '{theme_dict.get('name')}'.\n\n"
        f"Story Source:\n"
        f"  Title: {s_obj.title}\n"
        f"  Source: {s_obj.source}\n"
        f"  Summary: {s_obj.summary}\n\n"
        f"Task:\n"
        f"First, write a brief step-by-step 'analysis' of key facts stated in the source.\n"
        f"Then, write 'summary': EXACTLY 2 short sentences summarizing this story for a senior technical audience.\n\n"
        f"STRICT RULES:\n"
        f"1. Use ONLY facts, figures, and concepts explicitly stated in the Story Source above.\n"
        f"2. DO NOT use your outside knowledge or add extra medical/scientific background terms.\n"
        f"3. DO NOT include markdown links, URLs, or any numbers/figures that do not appear verbatim in the source."
        f"{correction_block}"
    )

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": StorySummaryResponse.model_json_schema(),
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 2048},
            },
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        data = json.loads(raw)
        res_obj = StorySummaryResponse.model_validate(data)
        return res_obj.summary.strip()
    except Exception as exc:
        logger.warning(f"generate_story_summary failed for '{s_obj.title[:50]}': {exc}")
        return ""


# Maximum number of summary regeneration attempts per story before using the fallback.
_VALIDATION_MAX_RETRIES = 3


def generate_story_summary_validated(
    story: Story | dict[str, Any],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
) -> str:
    """
    Generate a 2-sentence markdown summary for a single story with an inline
    anti-hallucination retry loop (runs immediately after summary generation).
    """
    from validator import validate_story

    s_obj = story if isinstance(story, Story) else Story.from_dict(story)

    title = s_obj.title
    link = s_obj.link
    current_section = ""
    hint = ""

    for attempt in range(1, _VALIDATION_MAX_RETRIES + 1):
        summary_text = generate_story_summary(s_obj, theme_dict, config, correction_hint=hint)
        if not summary_text:
            summary_text = s_obj.summary[:200]

        current_section = f"## [{title}]({link})\n{summary_text}\n"

        result = validate_story(s_obj, current_section, config, run_llm_check=True)
        status_str = "✅ PASSED" if result.passed else "FAILED / WARN"

        logger.info(
            f"Story [{title[:40]}...] "
            f"Attempt {attempt}/{_VALIDATION_MAX_RETRIES} Fact-Check: {status_str} "
            f"(Overlap: {result.keyword_overlap_score:.2f})"
        )

        if result.passed:
            s_obj.validated_summary = summary_text
            return summary_text

        for w in result.fabrication_warnings:
            logger.warning(f"  └─ {w}")
        if not result.llm_fact_check_passed:
            logger.warning(f"  └─ LLM Fact-Check Reasoning: {result.llm_reasoning}")

        hint = result.llm_reasoning
        if attempt < _VALIDATION_MAX_RETRIES:
            logger.info(f"  ↻ Regenerating summary for story [{title[:30]}...] with correction hint...")

    logger.warning(
        f"❌ Story [{title[:40]}...] failed fact-check after {_VALIDATION_MAX_RETRIES} attempts. Using fallback."
    )
    s_obj.validated_summary = STORY_FALLBACK_SUMMARY
    return STORY_FALLBACK_SUMMARY


def validate_and_correct_audio_script(
    stories: list[Story | dict[str, Any]],
    audio_script: str,
    config: dict[str, Any],
) -> tuple[bool, str]:
    """Validate audio script against source stories using LLM fact-checker."""
    from validator import llm_fact_check

    typed_stories = [s if isinstance(s, Story) else Story.from_dict(s) for s in stories]

    source_text = "\n\n".join([f"Title: {s.title}\nSummary: {s.summary}" for s in typed_stories])
    passed, reasoning = llm_fact_check(source_text, audio_script, config)
    return passed, reasoning


def generate_briefing_llm(
    stories: list[Story | dict[str, Any]],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
    text_only: bool = False,
) -> BriefingOutput:
    """
    Call local Ollama endpoint to produce:
    1. text_digest: validated story summaries prefixed with Theme header.
    2. audio_script: validated ~750 words podcast host script adhering to theme's tone.
    Returns a structured BriefingOutput class guaranteeing consistent markdown layout.
    """
    typed_stories = [s if isinstance(s, Story) else Story.from_dict(s) for s in stories]

    llm_cfg = config.get("llm", {})
    ollama_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
    model = llm_cfg.get("model", "phi4-mini:3.8b")
    word_target = llm_cfg.get("script_word_target", 750)

    theme_badge = (
        f"{theme_dict.get('emoji', '🎙️')} **{theme_dict.get('name', 'Daily Briefing')}**\n"
        f"_{theme_dict.get('description', '')}_\n"
    )

    logger.info(f"Generating validated text digest for theme '{theme_dict.get('name')}' per story...")
    digest_sections = []
    stories_context = []

    for idx, s in enumerate(typed_stories, 1):
        # 1. Generate & validate each story summary immediately
        validated_summary = generate_story_summary_validated(s, theme_dict, config)
        section = f"## [{s.title}]({s.link})\n{validated_summary}\n"
        digest_sections.append(section)

        stories_context.append(
            f"Story {idx}:\n"
            f"- Title: {s.title}\n"
            f"- Source: {s.source}\n"
            f"- Link: {s.link}\n"
            f"- Summary: {validated_summary}\n"
        )

    text_digest = "\n\n".join(digest_sections)
    full_text_digest = f"{theme_badge}\n{text_digest.strip()}"

    stories_block = "\n".join(stories_context)
    audio_script = ""

    if not text_only:
        logger.info(f"Generating spoken audio script (~{word_target} words) for theme '{theme_dict.get('name')}'...")

        audio_hint = ""
        for attempt in range(1, _VALIDATION_MAX_RETRIES + 1):
            correction_block = (
                f"\n\nCRITICAL FIX NEEDED FOR PREVIOUS AUDIO SCRIPT:\n"
                f"Fact-checker error feedback: {audio_hint}\n"
                f"Fix all errors. Rely strictly on facts from the stories above."
                if audio_hint.strip()
                else ""
            )

            script_prompt = (
                f"You are a professional tech podcast host briefing an engineering peer. "
                f"Today's thematic lens is: '{theme_dict.get('name')}'. Tone: {theme_dict.get('tone')}.\n\n"
                f"Here are the stories to cover:\n{stories_block}\n\n"
                f"Task:\n"
                f"Write a complete, natural spoken podcast monologue script of approximately {word_target} words.\n"
                f"STRICT RULES:\n"
                f"- Open smoothly with today's theme (e.g., 'Welcome back. Today we're looking through our {theme_dict.get('name')} lens...').\n"
                f"- Walk through all {len(typed_stories)} stories with natural conversational transitions and genuine technical depth.\n"
                f"- Write phonetically clean spoken English: absolutely NO markdown asterisks, hashes, bullets, brackets, or code symbols.\n"
                f"- Absolutely NO URLs, domain names, links, or 'available at' phrases.\n"
                f"- Conclude with a warm, professional wrap-up.\n"
                f"Output ONLY the spoken script text."
                f"{correction_block}"
            )

            candidate_script = ""
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
                candidate_script = clean_script_for_audio(raw_audio)
            except Exception as e:
                logger.error(f"Error generating audio script attempt {attempt}: {e}")

            if candidate_script and len(candidate_script.split()) >= 40:
                script_passed, reasoning = validate_and_correct_audio_script(typed_stories, candidate_script, config)
                status_str = "✅ PASSED" if script_passed else "FAILED / WARN"
                logger.info(f"Audio Script Attempt {attempt}/{_VALIDATION_MAX_RETRIES} Fact-Check: {status_str}")

                if script_passed:
                    audio_script = candidate_script
                    break
                else:
                    logger.warning(f"  └─ Audio Script Fact-Check Reasoning: {reasoning}")
                    audio_hint = reasoning
                    if attempt < _VALIDATION_MAX_RETRIES:
                        logger.info("  ↻ Regenerating audio script with correction hint...")

        if not audio_script:
            logger.warning("❌ Using fallback audio script from stories after validation failures.")
            script_parts = [f"Welcome to today's {theme_dict.get('name')} briefing. "]
            for idx, s in enumerate(typed_stories, 1):
                clean_t = clean_script_for_audio(s.title)
                clean_s = clean_script_for_audio(s.summary)
                script_parts.append(f"Story number {idx}. From {s.source}. {clean_t}. {clean_s}. ")
            script_parts.append("That concludes today's theme update.")
            audio_script = clean_script_for_audio(" ".join(script_parts))

    logger.info(f"Generated text digest and audio script (~{len(audio_script.split())} words).")
    return BriefingOutput(
        theme_name=str(theme_dict.get("name", "Daily Briefing")),
        theme_emoji=str(theme_dict.get("emoji", "🎙️")),
        theme_description=str(theme_dict.get("description", "")),
        stories=typed_stories,
        text_digest=full_text_digest,
        audio_script=audio_script,
    )
