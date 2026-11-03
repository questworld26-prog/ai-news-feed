"""
LLM Briefing Generator Module
Handles Ollama curation of stories, text digest generation, spoken script generation,
and audio text sanitization.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from pydantic import BaseModel, Field

from model_provider import ModelProviderFactory
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


# [spec: AUDIO-002]
def extract_clean_sentence_excerpt(text: str, max_chars: int = 220) -> str:
    """
    Extract up to max_chars from text, truncating strictly at the last complete sentence.
    Avoids trailing fragments, dangling conjunctions, or broken punctuation like 'intention that they .'.
    """
    if not text:
        return ""
    clean = re.sub(r"\s+", " ", text).strip()
    clean = re.sub(r"\s+they\s*\.$", ".", clean)
    clean = re.sub(r"\s+that\s*\.$", ".", clean)

    # 1. Look for a complete sentence within max_chars
    match = re.search(r"([.!?])(?:\s+|$)", clean[:max_chars])
    if match and match.start() >= 35:
        return clean[: match.start() + 1].strip()

    # 2. Otherwise truncate at last clean word boundary and strip dangling conjunctions/prepositions
    snippet = clean[:max_chars]
    truncated_word = snippet.rsplit(" ", 1)[0].rstrip(",;:- ")
    dangling = {
        "and",
        "but",
        "or",
        "that",
        "with",
        "as",
        "they",
        "to",
        "of",
        "in",
        "for",
        "on",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "it",
        "its",
    }
    words = truncated_word.split()
    while words and words[-1].lower() in dangling:
        words.pop()
    result = " ".join(words).strip()
    if result and result[-1] not in {".", "!", "?"}:
        result += "."
    return result


# [spec: AUDIO-003]
def clean_script_for_audio(raw_script: str) -> str:
    """Remove URLs, bracketed paths, markdown formatting, and theatrical flattery from spoken scripts."""
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

    # Strip theatrical preamble flattery, throat-clearing, and grand introductions
    text = re.sub(r"(?i)\bWelcome back\.\s*", "", text)
    text = re.sub(
        r"(?i)\bToday we[\x27']re looking through our [^.]*lens,\s*diving into the latest[^.]*\.\s*", "", text
    )
    text = re.sub(r"(?i)\bOur journey will take us through the realms of[^.]*\.\s*", "", text)
    text = re.sub(r"(?i)\bLet[\x27']s embark on this [^.]*\.\s*", "", text)

    # Strip theatrical outro flattery and philosophical wrap-ups
    text = re.sub(
        r"(?i)\s*\bIn conclusion,\s*today[\x27']s thematic journey.*$", " That is your briefing for today.", text
    )
    text = re.sub(
        r"(?i)\s*\bThank you for joining us on this intellectual voyage.*$", " That is your briefing for today.", text
    )
    text = re.sub(r"(?i)\s*\bUntil next time,\s*keep innovating.*$", " That is your briefing for today.", text)
    text = re.sub(
        r"(?i)\s*\bAs we continue to explore and innovate,\s*let us remain.*$",
        " That is your briefing for today.",
        text,
    )

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

    # Option 1: LAYA System 1 Fast Theme Curation & Story Pre-Ranking
    laya_cfg = config.get("laya", {})
    if laya_cfg.get("enabled", True) and laya_cfg.get("enable_curation_prerank", True):
        try:
            from laya_decision import get_laya_engine

            shortlist_size = int(laya_cfg.get("curation_shortlist_size", 7))
            engine = get_laya_engine(config)
            typed_candidates = engine.rank_candidates_for_theme(
                typed_candidates, theme_dict, config, top_k=shortlist_size
            )
        except Exception as exc:
            logger.debug(f"LAYA curation pre-ranking skipped: {exc}")

    llm_cfg = config.get("llm", {})
    model = llm_cfg.get("curation_model") or llm_cfg.get("model", "phi4-mini:3.8b")
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
        provider = ModelProviderFactory.get_provider(config)
        curation_res = provider.generate_structured(
            prompt=prompt,
            schema=CurationResponse,
            model=model,
            temperature=0.2,
            num_ctx=4096,
            timeout=120,
        )

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


# [spec: SUMM-001]
class StorySummaryResponse(BaseModel):
    direct_quotes: list[str] = Field(
        description="2 to 3 verbatim sentences or phrases extracted word-for-word directly from the source text"
    )
    summary: str = Field(
        description="EXACTLY 2 concise sentences synthesizing ONLY the facts and concepts present in direct_quotes"
    )


# Fallback text used when a story's summary cannot pass fact-checking after all retries.
STORY_FALLBACK_SUMMARY = "⚠️ Failed to generate a reliable summary. Read the original article."


# [spec: SUMM-002]
def generate_story_summary(
    story: Story | dict[str, Any],
    theme_dict: dict[str, Any],
    config: dict[str, Any],
    correction_hint: str = "",
) -> str:
    """
    Generate an accurate, grounded 2-sentence summary for a single story.
    Enforces extractive anchoring (verbatim quotes first) and positive constraint framing.
    """
    s_obj = story if isinstance(story, Story) else Story.from_dict(story)

    llm_cfg = config.get("llm", {})
    # Use specialized summary_model if configured, falling back to general model
    model = llm_cfg.get("summary_model") or llm_cfg.get("model", "qwen2.5:3b")

    correction_block = (
        f"\n\nCORRECTION REQUIRED FOR PREVIOUS ATTEMPT:\n"
        f"Fact-checker finding: {correction_hint}\n"
        f"Action: Remove any unanchored terms or figures. Confine your quotes and summary strictly to the text provided below."
        if correction_hint.strip()
        else ""
    )

    prompt = (
        f"You are a factual AI technical journalist preparing an executive digest for theme '{theme_dict.get('name')}'.\n\n"
        f"SOURCE ARTICLE:\n"
        f"Title: {s_obj.title}\n"
        f"Source: {s_obj.source}\n"
        f"Text:\n{s_obj.summary}\n\n"
        f"TASK & EXECUTION ORDER:\n"
        f"1. Extract 2 to 3 verbatim sentences or key phrases directly from the Text above into 'direct_quotes'.\n"
        f"2. Write 'summary': exactly 2 short sentences expressing only the facts stated in your 'direct_quotes'.\n\n"
        f"POSITIVE CONSTRAINTS:\n"
        f"- Confine your vocabulary strictly to the entities, benchmarks, and claims present in the Source Article.\n"
        f"- Express all metrics and quantities using the exact numbers from the Source Article.\n"
        f"- Write in clean, objective engineering prose.\n\n"
        f"EXAMPLE OF ACCEPTABLE GROUNDED SUMMARY:\n"
        f"Input Text: 'Datasette auth github 1.0 released by Simon Willison fixing session cookie expiration on Safari by setting Max-Age.'\n"
        f"direct_quotes: ['Datasette auth github 1.0 released by Simon Willison', 'fixing session cookie expiration on Safari by setting Max-Age']\n"
        f"summary: 'Simon Willison released version 1.0 of datasette-auth-github. The release configures Max-Age to resolve session cookie expiration on Safari.'\n"
        f"{correction_block}"
    )

    try:
        provider = ModelProviderFactory.get_provider(config)
        res_obj = provider.generate_structured(
            prompt=prompt,
            schema=StorySummaryResponse,
            model=model,
            temperature=0.1,
            num_ctx=2048,
            timeout=60,
        )
        if hasattr(res_obj, "direct_quotes") and res_obj.direct_quotes:
            s_obj.extra_metadata["direct_quotes"] = res_obj.direct_quotes
        return res_obj.summary.strip()
    except Exception as exc:
        logger.warning(f"generate_story_summary failed for '{s_obj.title[:50]}': {exc}")
        return ""


# Maximum number of summary regeneration attempts per story before using the fallback.
_VALIDATION_MAX_RETRIES = 3


# [spec: SUMM-003]
# [spec: SUMM-004]
# [spec: AIM-002]
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
            s_obj.extra_metadata["retry_count"] = attempt
            s_obj.extra_metadata["keyword_overlap"] = result.keyword_overlap_score
            s_obj.extra_metadata["summary_status"] = "success"
            return summary_text

        for w in result.fabrication_warnings:
            logger.warning(f"  └─ {w}")
        if not result.llm_fact_check_passed:
            logger.warning(f"  └─ LLM Fact-Check Reasoning: {result.llm_reasoning}")

        hint_parts = []
        if result.fabrication_warnings:
            hint_parts.extend(result.fabrication_warnings)
        if result.llm_reasoning and result.llm_reasoning not in hint_parts:
            hint_parts.append(result.llm_reasoning)
        hint = "; ".join(hint_parts)
        if attempt < _VALIDATION_MAX_RETRIES:
            logger.info(f"  ↻ Regenerating summary for story [{title[:30]}...] with correction hint...")

    logger.warning(
        f"❌ Story [{title[:40]}...] failed fact-check after {_VALIDATION_MAX_RETRIES} attempts. Using fallback."
    )
    s_obj.validated_summary = STORY_FALLBACK_SUMMARY
    s_obj.extra_metadata["retry_count"] = _VALIDATION_MAX_RETRIES
    s_obj.extra_metadata["keyword_overlap"] = 0.0
    s_obj.extra_metadata["summary_status"] = "failed"
    return STORY_FALLBACK_SUMMARY


def validate_and_correct_audio_script(
    stories: list[Story | dict[str, Any]],
    audio_script: str,
    config: dict[str, Any],
) -> tuple[bool, str]:
    """
    Validate audio script against verified stories using the Hierarchy of Truth:
    Source text is built from verified summaries and titles rather than raw noisy RSS text.
    Enforces CGAP (Capability-Grounded Agentic Planning) deterministic grounding and plan coverage.
    """
    from cgap_planner import compile_story_predicates, format_cgap_feedback_hint, verify_cgap_grounding
    from validator import detect_fabrications, llm_fact_check

    typed_stories = [s if isinstance(s, Story) else Story.from_dict(s) for s in stories]

    # 1. Deterministic CGAP Grounding and Plan Coverage Pre-Gate
    predicates = compile_story_predicates(typed_stories)
    cgap_result = verify_cgap_grounding(audio_script, predicates, config)
    if not cgap_result.passed:
        hint = format_cgap_feedback_hint(cgap_result)
        return False, f"CGAP Grounding failure: {hint}"

    # 2. Ground truth for audio script is the already-validated story summaries
    source_text = "\n\n".join(
        [f"Title: {s.title}\nValidated Summary: {s.validated_summary or s.summary}" for s in typed_stories]
    )
    fab_warnings = detect_fabrications(source_text, audio_script)
    if fab_warnings:
        return False, f"Deterministic gate failure in audio script: {'; '.join(fab_warnings)}"

    passed, reasoning = llm_fact_check(source_text, audio_script, config)
    return passed, reasoning


# [spec: AUDIO-001]
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
    model = llm_cfg.get("script_model") or llm_cfg.get("model", "phi4-mini:3.8b")
    word_target = llm_cfg.get("script_word_target", 750)

    theme_badge = (
        f"{theme_dict.get('emoji', '🎙️')} **{theme_dict.get('name', 'Daily Briefing')}**\n"
        f"_{theme_dict.get('description', '')}_\n"
    )

    logger.info(f"Generating validated text digest for theme '{theme_dict.get('name')}' per story...")
    digest_sections = []
    stories_context = []

    # Process per-story summary synthesis and validation (parallelizable when OLLAMA_NUM_PARALLEL > 1)
    from concurrent.futures import ThreadPoolExecutor

    def process_story(s: Story) -> tuple[Story, str]:
        try:
            val_summary = generate_story_summary_validated(s, theme_dict, config)
            return s, val_summary
        except Exception as exc:
            logger.warning(f"Unexpected error synthesizing summary for story '{s.title[:40]}': {exc}")
            s.validated_summary = STORY_FALLBACK_SUMMARY
            return s, STORY_FALLBACK_SUMMARY

    # Default max_workers=1 to be safe with default single-threaded Ollama setups,
    # or configurable up to 3 via config.toml [llm] synthesis_concurrency
    synthesis_concurrency = config.get("llm", {}).get("synthesis_concurrency", 1)
    with ThreadPoolExecutor(max_workers=max(1, synthesis_concurrency)) as executor:
        results = list(executor.map(process_story, typed_stories))

    for idx, (s, validated_summary) in enumerate(results, 1):
        if getattr(s, "is_update", False):
            prev_d = getattr(s, "original_briefed_date", None)
            update_line = (
                f"_🔄 Follow-up to our {prev_d} briefing._\n\n"
                if prev_d
                else "_🔄 Follow-up to our earlier briefing._\n\n"
            )
            section = f"## [{s.title}]({s.link})\n{update_line}{validated_summary}\n"
        else:
            section = f"## [{s.title}]({s.link})\n{validated_summary}\n"
        digest_sections.append(section)

        # Sanitize summary for audio script generation so fallback error text is never read on air
        audio_story_summary = validated_summary
        if STORY_FALLBACK_SUMMARY in validated_summary or "⚠️" in validated_summary:
            clean_raw = s.summary.strip()
            if len(clean_raw) >= 40 and "failed to generate" not in clean_raw.lower():
                audio_story_summary = clean_raw[:200]
            else:
                audio_story_summary = f"Focuses on recent developments and updates regarding {s.title}."

        update_flag_str = ""
        if getattr(s, "is_update", False):
            prev_d = getattr(s, "original_briefed_date", None)
            update_flag_str = (
                f"- Status: UPDATE / Follow-up (previously briefed on {prev_d})\n"
                if prev_d
                else "- Status: UPDATE / Follow-up\n"
            )

        stories_context.append(
            f"Story {idx}:\n"
            f"- Title: {s.title}\n"
            f"- Source: {s.source}\n"
            f"{update_flag_str}"
            f"- Link: {s.link}\n"
            f"- Summary: {audio_story_summary}\n"
        )

    text_digest = "\n\n".join(digest_sections)
    full_text_digest = f"{theme_badge}\n{text_digest.strip()}"

    audio_script = ""
    audio_passed = False
    audio_attempts = 0

    if not text_only:
        from cgap_planner import build_cgap_script_plan, compile_story_predicates

        # Recommendation 1: Exclude stories whose Level 2 summary failed fact-checking
        # A spoken podcast should only present stories with 100% verified factual summaries
        verified_audio_stories = [
            s
            for s in typed_stories
            if s.validated_summary
            and not s.validated_summary.startswith("⚠️")
            and "failed to generate" not in s.validated_summary.lower()
        ]

        if not verified_audio_stories:
            logger.warning("⚠️ No stories passed Level 2 validation. Using headline notices for all stories.")
            target_audio_stories = typed_stories
        elif len(verified_audio_stories) < len(typed_stories):
            excluded_count = len(typed_stories) - len(verified_audio_stories)
            logger.info(
                f"🎙️ Audio Script Curation: {len(verified_audio_stories)}/{len(typed_stories)} stories verified for spoken monologue (excluding {excluded_count} unverified story)."
            )
            target_audio_stories = verified_audio_stories
        else:
            target_audio_stories = typed_stories

        story_predicates = compile_story_predicates(target_audio_stories)
        cgap_plan = build_cgap_script_plan(story_predicates, theme_dict.get("name", "Daily Briefing"))

        logger.info(
            f"Generating spoken audio script (~{word_target} words) across {len(target_audio_stories)} stories for theme '{theme_dict.get('name')}'..."
        )

        audio_hint = ""
        for attempt in range(1, _VALIDATION_MAX_RETRIES + 1):
            audio_attempts = attempt
            correction_block = (
                f"\n\nCRITICAL FIX NEEDED FOR PREVIOUS AUDIO SCRIPT:\n"
                f"Fact-checker error feedback: {audio_hint}\n"
                f"Fix all errors. Rely strictly on facts from the stories above."
                if audio_hint.strip()
                else ""
            )

            script_prompt = (
                f"You are a concise, sharp technical news presenter briefing a software engineer or CTO. "
                f"Today's thematic lens is: '{theme_dict.get('name')}'. Editorial tone: {theme_dict.get('tone')}.\n\n"
                f"{cgap_plan}\n\n"
                f"Task:\n"
                f"Write a spoken briefing monologue script of approximately {word_target} words following the exact CGAP Execution Steps above covering these {len(target_audio_stories)} stories.\n\n"
                f"STRICT EDITORIAL RULES:\n"
                f"- ZERO FLATTERY & ZERO PREAMBLE: Absolutely NO conversational preamble, throat-clearing, flattery, or grandiose phrases. "
                f"Never say things like 'Welcome back', 'our journey through the realms', 'intellectual voyage', 'let us embark on this mission', or 'pushing the boundaries of what is possible'.\n"
                f"- DIRECT OPENING: Start immediately with a single brief sentence identifying the theme and first story. For example: "
                f"'Today in {theme_dict.get('name')}: first up, ...' or 'Here is today's {theme_dict.get('name')} briefing. First, ...'. Jump straight into the facts with no agenda previews.\n"
                f"- TECHNICAL DEPTH: Walk through all {len(target_audio_stories)} stories focusing on concrete mechanics, benchmarks, systemic implications, and facts from the source text. Keep transitions natural, collegiate, and direct.\n"
                f"- DUAL-GROUNDING: Use each story's 'Article Context' to explain the engineering problem, mechanics, and why it matters conversationally. Anchor strictly to the 'Core Takeaway' without merely reading it word-for-word.\n"
                f"- SEQUENCE ADHERENCE: You MUST cover every story in the exact numerical order specified in the CGAP plan (Story #1, then Story #2, up to Story #{len(target_audio_stories)}). Do not omit or reorder any story.\n"
                f"- STRICT GROUNDING: Confine all claims, metrics, and entities strictly to the Allowed Facts specified in each step. Do not invent benchmark numbers, tool versions, or ungrounded organizations.\n"
                f"- UPDATES: If a story has 'Status: UPDATE / Follow-up', frame it conversationally as a follow-up or update to earlier coverage (e.g. 'Following up on our earlier coverage...', 'An update to the story we tracked earlier...'), highlighting what is new.\n"
                f"- ZERO THEATRICAL CONCLUSION: Do NOT summarize the briefing, do NOT say 'In conclusion', do NOT give philosophical send-offs, and do NOT thank the listener for an 'intellectual voyage'. End cleanly immediately after the final story with a single simple sign-off: 'That is your briefing for today.'\n"
                f"- CLEAN SPEECH: Write phonetically clean spoken English: absolutely NO markdown asterisks, hashes, bullets, brackets, or code symbols.\n"
                f"- NO LINKS: Absolutely NO URLs, domain names, links, or 'available at' phrases.\n\n"
                f"Output ONLY the spoken script text."
                f"{correction_block}"
            )

            candidate_script = ""
            try:
                provider = ModelProviderFactory.get_provider(config)
                raw_audio = provider.generate(
                    prompt=script_prompt,
                    model=model,
                    temperature=0.7,
                    num_ctx=4096,
                    timeout=240,
                )
                candidate_script = clean_script_for_audio(raw_audio)
            except Exception as e:
                logger.error(f"Error generating audio script attempt {attempt}: {e}")

            if candidate_script and len(candidate_script.split()) >= 40:
                script_passed, reasoning = validate_and_correct_audio_script(
                    target_audio_stories, candidate_script, config
                )
                status_str = "✅ PASSED" if script_passed else "FAILED / WARN"
                logger.info(f"Audio Script Attempt {attempt}/{_VALIDATION_MAX_RETRIES} Fact-Check: {status_str}")

                if script_passed:
                    audio_script = candidate_script
                    audio_passed = True
                    break
                else:
                    logger.warning(f"  └─ Audio Script Fact-Check Reasoning: {reasoning}")
                    audio_hint = reasoning
                    if attempt < _VALIDATION_MAX_RETRIES:
                        logger.info("  ↻ Regenerating audio script with correction hint...")

        if not audio_script:
            logger.warning(
                f"❌ Using emergency fallback audio script after {audio_attempts} validation failures. "
                f"Last error feedback: {audio_hint}"
            )
            script_parts = [f"Here is today's {theme_dict.get('name')} briefing. "]
            for idx, s in enumerate(target_audio_stories, 1):
                clean_t = clean_script_for_audio(s.title)
                if (
                    s.validated_summary
                    and not s.validated_summary.startswith("⚠️")
                    and "failed to generate" not in s.validated_summary.lower()
                ):
                    clean_s = clean_script_for_audio(s.validated_summary)
                elif s.summary and not s.summary.startswith("⚠️"):
                    clean_s = extract_clean_sentence_excerpt(clean_script_for_audio(s.summary))
                else:
                    clean_s = "Full details and technical coverage are available in the written digest."
                script_parts.append(f"Story number {idx}. From {s.source}. {clean_t}. {clean_s} ")
            script_parts.append("That is your briefing for today.")
            audio_script = clean_script_for_audio(" ".join(script_parts))

    logger.info(f"Generated text digest and audio script (~{len(audio_script.split())} words).")
    return BriefingOutput(
        theme_name=str(theme_dict.get("name", "Daily Briefing")),
        theme_emoji=str(theme_dict.get("emoji", "🎙️")),
        theme_description=str(theme_dict.get("description", "")),
        stories=typed_stories,
        text_digest=full_text_digest,
        audio_script=audio_script,
        metadata={
            "audio_factcheck_passed": audio_passed,
            "audio_factcheck_attempts": audio_attempts,
        },
    )
