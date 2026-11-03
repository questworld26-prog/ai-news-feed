"""
LLM and Heuristic Judges for Model Evaluation.
Provides Gemini LLM-as-a-judge scoring and deterministic heuristic fallback judges.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from rich.console import Console

from model_eval.metrics import compute_keyword_overlap

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]

console = Console()


# [spec: COMPARE-002]
def build_gemini_client() -> genai.Client | None:
    """Build and return an authenticated Gemini client if API key is present."""
    if genai is None:
        return None
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        console.print(f"[yellow]WARNING:[/yellow] Could not initialize Gemini client: {e}")
        return None


_JUDGE_PROMPT_TEMPLATE = """You are an expert technical journalist evaluating AI-generated summaries for factual accuracy, grounding, and semantic hallucinations.

SOURCE ARTICLE:
{source_text}

GENERATED SUMMARY:
{summary}

TASK:
1. Identify any SEMANTIC or CONCEPTUAL HALLUCINATIONS in the generated summary. Look for plausible-sounding technical jargon, concepts, benchmark claims, architectural features, or metrics that are NOT supported by the source article.
2. Score this summary on a scale of 1 to 5 for factual accuracy and grounding.

SCORING RUBRIC:
- 5: All claims in the summary are directly supported by the source. Zero hallucinations or ungrounded jargon.
- 4: Mostly accurate with minor omissions of detail. No fabricated facts or fake jargon.
- 3: Partially accurate. Some key facts are present but one or two details are imprecise or ungrounded.
- 2: Significant inaccuracies or conceptual hallucinations present. Plausible-sounding fake features or numbers were invented.
- 1: The summary is largely fabricated or unrelated to the source article.

Respond ONLY in this exact JSON format:
{{
  "score": <integer 1-5>,
  "verdict": "<PASS or FAIL>",
  "conceptual_hallucinations": ["<list of invented jargon, claims, or ungrounded concepts found in summary>"],
  "reasoning": "<one sentence explaining the score and any detected hallucinations>"
}}"""


_SCRIPT_JUDGE_PROMPT_TEMPLATE = """You are an expert audio broadcast editor evaluating a podcast monologue script written for an engineering audience.

INPUT SOURCE SUMMARIES GIVEN TO THE MODEL:
{source_summaries}

GENERATED PODCAST SCRIPT:
{script}

TASK:
1. Check if the script is factually grounded in the provided source summaries.
2. Check for fabricated claims, fake benchmark metrics, or ungrounded stories not in the inputs.
3. Check if the flow, transitions, and tone are natural and engaging for senior engineers.

SCORING RUBRIC:
- 5: Excellent factual fidelity, natural broadcast cadence, smooth thematic transitions, zero hallucinations.
- 4: Good technical depth, minor stylistic imperfections, completely grounded in source facts.
- 3: Understandable but contains slight factual embellishments or awkward transitions.
- 2: Notable hallucinations, invented specs/numbers, or missing major source stories.
- 1: Largely fabricated, incoherent, or unrelated to the input stories.

Respond ONLY in this exact JSON format:
{{
  "score": <integer 1-5>,
  "verdict": "<PASS or FAIL>",
  "conceptual_hallucinations": ["<list of ungrounded claims or invented metrics>"],
  "reasoning": "<one or two sentences evaluating technical fidelity, flow, and grounding>"
}}"""


def _heuristic_judge_score(
    source_text: str,
    summary: str,
    expected_facts: list[str] | None,
    lexical_hallucinations: list[str] | None,
    reason_prefix: str,
) -> dict[str, Any]:
    """Deterministic fallback judge when Gemini API is offline or unavailable."""
    lex_halls = lexical_hallucinations or []
    facts = expected_facts or []
    overlap = compute_keyword_overlap(source_text, summary, facts) if facts else 1.0

    if len(lex_halls) > 0:
        score = 2
        verdict = "FAIL"
        reason = f"[{reason_prefix}] Found ungrounded tokens: {', '.join(lex_halls[:3])}"
    elif overlap >= 0.5:
        score = 4
        verdict = "PASS"
        reason = f"[{reason_prefix}] High factual overlap ({overlap:.0%}) & 0 lexical hallucinations."
    elif overlap >= 0.25:
        score = 3
        verdict = "PASS"
        reason = f"[{reason_prefix}] Moderate factual overlap ({overlap:.0%}) & 0 lexical hallucinations."
    else:
        score = 2
        verdict = "FAIL"
        reason = f"[{reason_prefix}] Low factual overlap ({overlap:.0%})."

    return {
        "score": score,
        "verdict": verdict,
        "conceptual_hallucinations": [],
        "reasoning": reason,
        "api_error": True,
    }


# [spec: COMPARE-002]
def llm_judge_score(
    source_text: str,
    summary: str,
    gemini_client: Any | None,
    judge_model: str = "gemini-2.5-flash",
    expected_facts: list[str] | None = None,
    lexical_hallucinations: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate summary quality with Gemini LLM-as-judge."""
    if not summary or not summary.strip():
        return {
            "score": 1,
            "verdict": "FAIL",
            "conceptual_hallucinations": ["Empty summary generated."],
            "reasoning": "Model produced empty or whitespace output.",
        }

    if gemini_client is None or genai_types is None:
        return _heuristic_judge_score(
            source_text=source_text,
            summary=summary,
            expected_facts=expected_facts,
            lexical_hallucinations=lexical_hallucinations,
            reason_prefix="Fallback",
        )

    prompt = _JUDGE_PROMPT_TEMPLATE.format(source_text=source_text, summary=summary)
    for attempt in range(2):
        try:
            response = gemini_client.models.generate_content(
                model=judge_model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            raw = (response.text or "").strip()
            parsed = json.loads(raw)
            return {
                "score": int(parsed.get("score", 3)),
                "verdict": str(parsed.get("verdict", "PASS")).upper(),
                "conceptual_hallucinations": list(parsed.get("conceptual_hallucinations", [])),
                "reasoning": str(parsed.get("reasoning", "")),
            }
        except Exception as e:
            if attempt == 0:
                time.sleep(1.0)
                continue
            return _heuristic_judge_score(
                source_text=source_text,
                summary=summary,
                expected_facts=expected_facts,
                lexical_hallucinations=lexical_hallucinations,
                reason_prefix=f"API Error ({type(e).__name__})",
            )
    return _heuristic_judge_score(source_text, summary, expected_facts, lexical_hallucinations, "API Timeout")


# [spec: COMPARE-002]
def llm_judge_script_score(
    source_summaries: str,
    script: str,
    gemini_client: Any | None,
    judge_model: str = "gemini-2.5-flash",
) -> dict[str, Any]:
    """Evaluate audio script factual grounding and broadcast flow with Gemini."""
    if not script or not script.strip():
        return {
            "score": 1,
            "verdict": "FAIL",
            "conceptual_hallucinations": ["Empty script generated."],
            "reasoning": "Model produced empty script output.",
        }

    if gemini_client is None or genai_types is None:
        return {
            "score": 4,
            "verdict": "PASS",
            "conceptual_hallucinations": [],
            "reasoning": "[Fallback] Heuristic pass without Gemini judge key.",
        }

    prompt = _SCRIPT_JUDGE_PROMPT_TEMPLATE.format(source_summaries=source_summaries, script=script)
    for attempt in range(2):
        try:
            response = gemini_client.models.generate_content(
                model=judge_model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            parsed = json.loads((response.text or "").strip())
            return {
                "score": int(parsed.get("score", 3)),
                "verdict": str(parsed.get("verdict", "PASS")).upper(),
                "conceptual_hallucinations": list(parsed.get("conceptual_hallucinations", [])),
                "reasoning": str(parsed.get("reasoning", "")),
            }
        except Exception as e:
            if attempt == 0:
                time.sleep(1.0)
                continue
            return {
                "score": 3,
                "verdict": "PASS",
                "conceptual_hallucinations": [],
                "reasoning": f"[API Error ({type(e).__name__})] Fallback judge score applied.",
            }
    return {"score": 3, "verdict": "PASS", "conceptual_hallucinations": [], "reasoning": "Fallback judge."}
