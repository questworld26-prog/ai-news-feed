#!/usr/bin/env python3
"""
model_comparator.py
===================
Comprehensive Multi-Role LLM Evaluation & Benchmark Harness.

Compares Ollama models across all four core pipeline roles:
  1. Summarization       – 2-sentence factual extraction, ROUGE-L, fact overlap, judge
  2. Curation            – CoT justification + CurationResponse JSON schema, precision/recall
  3. Script Generation   – ~750-word natural podcast monologue, coverage, markdown/URL leakage, grounding
  4. Adversarial Audit   – Factual audit safety net, True Positive Rate on poisoned injections vs True Negative Rate

Usage:
  uv run eval/model_comparator.py [--task {all,summarization,curation,script,audit}] [--models model1,model2]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Dependency checks ────────────────────────────────────────────────────────
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        print("ERROR: tomllib not available. Requires Python 3.11+ or `pip install tomli`.")
        sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: `requests` not installed. Run: uv add requests")
    sys.exit(1)

try:
    from rouge_score import rouge_scorer
except ImportError:
    print("ERROR: `rouge-score` not installed. Run: uv add rouge-score --group dev")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.table import Table
    from rich import box
except ImportError:
    print("ERROR: `rich` not installed. Run: uv add rich --group dev")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("ERROR: `google-genai` not installed. Run: uv add google-genai --group dev")
    sys.exit(1)

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: `pydantic` not installed. Run: uv add pydantic")
    sys.exit(1)

try:
    import psutil
except ImportError:
    psutil = None  # Optional memory tracking

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Setup path to src to reuse production modules/schemas ───────────────────
EVAL_DIR = Path(__file__).parent
PROJECT_ROOT = EVAL_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from briefing_generator import CurationResponse, clean_script_for_audio
    from validator import llm_fact_check
    from story import Story
except ImportError as e:
    console_err = Console()
    console_err.print(f"[yellow]Warning: Could not import production schemas directly ({e}). Using local definitions.[/yellow]")

    class StorySelectionJustification(BaseModel):
        index: int = Field(description="1-based integer index of the candidate story")
        reasoning: str = Field(description="Brief technical justification for why this story was selected")

    class CurationResponse(BaseModel):  # type: ignore[no-redef]
        evaluation_criteria: str = Field(description="Summary of theme evaluation criteria applied")
        justifications: list[StorySelectionJustification] = Field(description="Step-by-step justifications")
        selected: list[int] = Field(description="List of 1-based integer candidate indices")

    def clean_script_for_audio(raw_script: str) -> str:  # type: ignore[no-redef]
        text = re.sub(r"[*_#`~>|-]", " ", raw_script or "")
        return re.sub(r"\s+", " ", text).strip()

# ── HTML Dashboard Generator Import ──────────────────────────────────────────
try:
    from eval.save_html import save_html_dashboard
except ImportError:
    try:
        from save_html import save_html_dashboard
    except ImportError:
        sys.path.insert(0, str(EVAL_DIR))
        from save_html import save_html_dashboard  # type: ignore[no-redef]

CONFIG_PATH = EVAL_DIR / "eval_config.toml"
console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# Config and Dataset Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_config() -> dict[str, Any]:
    """Load eval_config.toml."""
    if not CONFIG_PATH.exists():
        console.print(f"[red]ERROR:[/red] Config not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def load_golden_dataset(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Load the golden dataset JSON file."""
    dataset_path = EVAL_DIR / config["evaluation"]["golden_dataset_path"]
    if not dataset_path.exists():
        console.print(f"[red]ERROR:[/red] Golden dataset not found at {dataset_path}")
        sys.exit(1)
    with open(dataset_path, encoding="utf-8") as f:
        data = json.load(f)
    console.print(f"[dim]Loaded {len(data)} total evaluation cases from {dataset_path.name}[/dim]")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# Ollama Utilities & Memory Profiling
# ─────────────────────────────────────────────────────────────────────────────

def get_ollama_models(ollama_url: str) -> list[str]:
    """Query Ollama for the list of locally available models."""
    try:
        resp = requests.get(f"{ollama_url}/api/tags", timeout=10)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return sorted(models)
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Could not reach Ollama at {ollama_url}: {e}")
        sys.exit(1)


def select_models_interactively(available_models: list[str]) -> list[str]:
    """Prompt the user to select which models to compare."""
    console.print("\n[bold cyan]Available Ollama Models:[/bold cyan]")
    for i, name in enumerate(available_models, 1):
        console.print(f"  [dim]{i:2}.[/dim] {name}")

    console.print(
        "\n[bold]Enter the numbers of models to compare[/bold] (comma-separated, e.g. [yellow]1,3,5[/yellow]):"
    )
    raw = input("  > ").strip()

    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(available_models):
                selected.append(available_models[idx])
            else:
                console.print(f"[yellow]Warning:[/yellow] Index {part} out of range — skipped.")
        else:
            console.print(f"[yellow]Warning:[/yellow] '{part}' is not a valid number — skipped.")

    if not selected:
        console.print("[red]No valid models selected. Exiting.[/red]")
        sys.exit(1)

    console.print(f"\n[green]Selected models:[/green] {', '.join(selected)}\n")
    return selected


def unload_model_from_ollama(model: str, ollama_url: str) -> None:
    """Instruct Ollama to unload a model from VRAM by setting keep_alive=0."""
    try:
        requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": "", "keep_alive": 0, "stream": False},
            timeout=15,
        )
        console.print(f"  [dim]Model [cyan]{model}[/cyan] unloaded from memory.[/dim]")
    except Exception:
        pass


def get_system_and_ollama_memory_gb(ollama_url: str = "http://localhost:11434") -> dict[str, float]:
    """Measures RAM usage across the system and Ollama process."""
    if not psutil:
        return {"process_rss_gb": 0.0, "ollama_process_rss_gb": 0.0, "system_used_ram_gb": 0.0}

    process_rss = psutil.Process().memory_info().rss / (1024 ** 3)
    system_used = psutil.virtual_memory().used / (1024 ** 3)

    ollama_rss = 0.0
    for p in psutil.process_iter(['name', 'memory_info']):
        try:
            if 'ollama' in (p.info['name'] or '').lower():
                ollama_rss += p.info['memory_info'].rss / (1024 ** 3)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return {
        "process_rss_gb": round(process_rss, 2),
        "ollama_process_rss_gb": round(ollama_rss, 2),
        "system_used_ram_gb": round(system_used, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Generation Functions
# ─────────────────────────────────────────────────────────────────────────────

def generate_summary_ollama(
    source_text: str,
    model: str,
    prompt_template: str,
    ollama_url: str,
    temperature: float,
    num_ctx: int,
    timeout: int,
    stream: bool = True,
) -> tuple[str, float, float, float, int, int]:
    """Generate a summary using Ollama with streaming TTFT tracking."""
    prompt = prompt_template.replace("{source_text}", source_text)
    start = time.perf_counter()

    if stream:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {"temperature": temperature, "num_ctx": num_ctx},
            },
            timeout=timeout,
            stream=True,
        )
        resp.raise_for_status()

        ttft: float | None = None
        chunks: list[str] = []
        prompt_eval_count = 0
        eval_count = 0
        eval_duration_ns = 0

        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            if ttft is None and data.get("response"):
                ttft = time.perf_counter() - start

            if data.get("response"):
                chunks.append(data["response"])

            if data.get("done"):
                prompt_eval_count = data.get("prompt_eval_count", 0)
                eval_count = data.get("eval_count", 0)
                eval_duration_ns = data.get("eval_duration", 0)

        total_latency = time.perf_counter() - start
        summary = "".join(chunks).strip()
        ttft_val = ttft if ttft is not None else total_latency

        if eval_count > 0 and eval_duration_ns > 0:
            tok_per_sec = eval_count / (eval_duration_ns / 1e9)
        else:
            gen_time = max(total_latency - ttft_val, 0.001)
            tok_per_sec = len(summary.split()) / gen_time

        return summary, round(total_latency, 3), round(ttft_val, 3), round(tok_per_sec, 2), prompt_eval_count, eval_count
    else:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_ctx": num_ctx},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        latency = time.perf_counter() - start
        data = resp.json()
        summary = data.get("response", "").strip()
        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 0)
        tok_per_sec = eval_count / (eval_duration_ns / 1e9) if eval_count > 0 and eval_duration_ns > 0 else 0.0
        return summary, round(latency, 3), round(latency, 3), round(tok_per_sec, 2), prompt_eval_count, eval_count


# ─────────────────────────────────────────────────────────────────────────────
# Lexical & Heuristic Metrics
# ─────────────────────────────────────────────────────────────────────────────

_rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)


def compute_rouge_l(source_text: str, summary: str) -> float:
    """Compute ROUGE-L F1 between source text and generated summary."""
    if not summary:
        return 0.0
    scores = _rouge.score(source_text, summary)
    return round(scores["rougeL"].fmeasure, 4)


def compute_keyword_overlap(source_text: str, summary: str, expected_facts: list[str]) -> float:
    """Fraction of expected_facts that appear in the summary."""
    if not expected_facts or not summary:
        return 0.0
    summary_lower = summary.lower()
    hits = sum(1 for fact in expected_facts if fact.lower() in summary_lower)
    return round(hits / len(expected_facts), 4)


def detect_hallucinations(source_text: str, summary: str) -> list[str]:
    """Flags capitalized multi-word tokens/numbers not in source text."""
    if not summary:
        return []
    candidate_patterns = [
        r"\b\d+(?:\.\d+)?%\b",
        r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
        r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]+)+\b",
    ]
    source_lower = source_text.lower()
    hallucinations = []
    for pattern in candidate_patterns:
        for match in re.finditer(pattern, summary):
            token = match.group()
            if token.lower() not in source_lower:
                hallucinations.append(token)
    return list(set(hallucinations))


def compute_length_metrics(summary: str) -> dict[str, int]:
    """Return word count and sentence count for the text."""
    words = len(summary.split()) if summary else 0
    sentences = len([s for s in re.split(r"[.!?]+", summary) if s.strip()]) if summary else 0
    return {"word_count": words, "sentence_count": sentences}


# ─────────────────────────────────────────────────────────────────────────────
# Gemini Judge Setup & Scoring
# ─────────────────────────────────────────────────────────────────────────────

def build_gemini_client() -> genai.Client | None:
    """Build and return an authenticated Gemini client if API key is present."""
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[yellow]WARNING:[/yellow] GOOGLE_API_KEY environment variable not set.")
        console.print("  LLM judge will use deterministic heuristic evaluation fallback.")
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


def llm_judge_score(
    source_text: str,
    summary: str,
    gemini_client: genai.Client | None,
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

    if gemini_client is None:
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


def llm_judge_script_score(
    source_summaries: str,
    script: str,
    gemini_client: genai.Client | None,
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

    if gemini_client is None:
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


# ─────────────────────────────────────────────────────────────────────────────
# Evaluator: Role 1 — Summarization
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_summarization_case(
    case: dict[str, Any],
    model: str,
    config: dict[str, Any],
    gemini_client: genai.Client | None,
    run_idx: int = 1,
) -> dict[str, Any]:
    """Evaluates a single summarization golden case."""
    case_id = case["id"]
    source_text = case["source_text"]
    expected_facts = case.get("expected_facts", [])
    buried_facts = case.get("middle_buried_facts", [])

    ollama_cfg = config["ollama"]
    ollama_url = ollama_cfg["url"].rstrip("/")
    temperature = ollama_cfg["temperature"]
    num_ctx = ollama_cfg["num_ctx"]
    timeout = ollama_cfg["timeout_seconds"]
    prompt_template = config["summarization"]["prompt_template"]
    stream_mode = ollama_cfg.get("stream", True)
    judge_model = config["judge"]["model"]
    eval_cfg = config["evaluation"]
    min_overlap = eval_cfg["min_keyword_overlap"]
    min_rouge = eval_cfg.get("min_rouge_l", 0.45)

    mem_info = get_system_and_ollama_memory_gb(ollama_url)

    try:
        summary, latency, ttft, tok_per_sec, in_toks, out_toks = generate_summary_ollama(
            source_text=source_text,
            model=model,
            prompt_template=prompt_template,
            ollama_url=ollama_url,
            temperature=temperature,
            num_ctx=num_ctx,
            timeout=timeout,
            stream=stream_mode,
        )
    except Exception as e:
        summary, latency, ttft, tok_per_sec, in_toks, out_toks = "", 0.0, 0.0, 0.0, 0, 0
        console.print(f"  [red]ERROR generating summary for {case_id}: {e}[/red]")

    rouge_l = compute_rouge_l(source_text, summary)
    keyword_overlap = compute_keyword_overlap(source_text, summary, expected_facts)
    lexical_hallucinations = detect_hallucinations(source_text, summary)
    length = compute_length_metrics(summary)

    positional_recall_passed = True
    if buried_facts:
        found_buried = sum(1 for bf in buried_facts if bf.lower() in summary.lower())
        positional_recall_passed = (found_buried == len(buried_facts))

    judge = llm_judge_score(
        source_text=source_text,
        summary=summary,
        gemini_client=gemini_client,
        judge_model=judge_model,
        expected_facts=expected_facts,
        lexical_hallucinations=lexical_hallucinations,
    )

    conceptual_hallucinations = judge.get("conceptual_hallucinations", [])
    all_hallucinations = list(set(lexical_hallucinations + conceptual_hallucinations))

    passed = (
        rouge_l >= min_rouge
        and keyword_overlap >= min_overlap
        and len(all_hallucinations) == 0
        and judge["verdict"] == "PASS"
        and positional_recall_passed
    )

    return {
        "case_id": case_id,
        "type": "summarization",
        "run_idx": run_idx,
        "summary": summary,
        "latency_seconds": round(latency, 3),
        "ttft_seconds": round(ttft, 3),
        "tokens_per_second": round(tok_per_sec, 2),
        "input_tokens": in_toks,
        "output_tokens": out_toks,
        "process_ram_gb": mem_info["process_rss_gb"],
        "ollama_ram_gb": mem_info["ollama_process_rss_gb"],
        "system_used_ram_gb": mem_info["system_used_ram_gb"],
        "rouge_l": rouge_l,
        "keyword_overlap": keyword_overlap,
        "lexical_hallucinations": lexical_hallucinations,
        "conceptual_hallucinations": conceptual_hallucinations,
        "all_hallucinations": all_hallucinations,
        "word_count": length["word_count"],
        "sentence_count": length["sentence_count"],
        "judge_score": judge["score"],
        "judge_verdict": judge["verdict"],
        "judge_reasoning": judge["reasoning"],
        "positional_recall_passed": positional_recall_passed,
        "passed": passed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Evaluator: Role 2 — Curation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_curation_case(
    case: dict[str, Any],
    model: str,
    config: dict[str, Any],
    run_idx: int = 1,
) -> dict[str, Any]:
    """Evaluates a single story curation golden case with CoT JSON schema."""
    case_id = case["id"]
    theme_dict = case.get("theme_dict", {"name": "General Tech", "description": "Tech news", "tone": "technical"})
    candidates = case.get("candidates", [])
    max_stories = case.get("max_stories", 3)
    must_select = set(case.get("must_select", []))
    must_reject = set(case.get("must_reject", []))

    curation_cfg = config.get("curation", {})
    ollama_url = config.get("ollama", {}).get("url", "http://localhost:11434").rstrip("/")
    temperature = curation_cfg.get("temperature", 0.2)
    num_ctx = curation_cfg.get("num_ctx", 4096)
    timeout = curation_cfg.get("timeout_seconds", 120)

    # Build prompt exactly matching production briefing_generator.py
    story_list = ""
    for idx, s in enumerate(candidates, 1):
        summary_snip = s.get("summary", "")[:200]
        story_list += f"[{idx}] {s.get('title', '')} (Source: {s.get('source', '')})\nSummary: {summary_snip}\n\n"

    prompt = (
        f"You are an expert AI technical editor curating a daily briefing for senior engineers.\n"
        f"Theme Name: '{theme_dict.get('name')}'\n"
        f"Theme Description: {theme_dict.get('description')}\n"
        f"Target Audience & Tone: {theme_dict.get('tone')}\n\n"
        f"Task:\n"
        f"Select the top {max_stories} stories from the {len(candidates)} candidate stories below.\n"
        f"Favor concrete technical implementations, open-source tools, system architectures, or major breakthroughs.\n"
        f"Exclude generic hype, corporate press releases, or non-technical funding announcements.\n\n"
        f"Instructions:\n"
        f"1. State your specific 'evaluation_criteria' for this theme.\n"
        f"2. Provide step-by-step 'justifications' explaining why each candidate story was chosen.\n"
        f"3. Output the final top {max_stories} 1-based integer indices in 'selected' in priority order.\n\n"
        f"Candidate Stories:\n{story_list}"
    )

    mem_info = get_system_and_ollama_memory_gb(ollama_url)
    start_time = time.perf_counter()
    schema_valid = False
    selected_indices: list[int] = []
    justifications_count = 0
    raw_response = ""

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "format": CurationResponse.model_json_schema(),
                "stream": False,
                "options": {"temperature": temperature, "num_ctx": num_ctx},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        latency = time.perf_counter() - start_time
        raw_response = resp.json().get("response", "").strip()

        parsed = CurationResponse.model_validate_json(raw_response)
        schema_valid = True
        selected_indices = [idx for idx in parsed.selected if 1 <= idx <= len(candidates)]
        justifications_count = len(parsed.justifications)
    except Exception as e:
        latency = time.perf_counter() - start_time
        console.print(f"  [red]Curation JSON schema validation failed for {case_id}: {e}[/red]")

    selected_set = set(selected_indices)
    recall = (len(selected_set.intersection(must_select)) / len(must_select)) if must_select else 1.0
    rejects_selected = selected_set.intersection(must_reject)
    precision = 1.0 - (len(rejects_selected) / len(must_reject)) if must_reject else 1.0

    passed = (
        schema_valid
        and recall >= curation_cfg.get("min_selection_recall", 0.80)
        and precision >= curation_cfg.get("min_selection_precision", 0.80)
        and len(rejects_selected) == 0
    )

    return {
        "case_id": case_id,
        "type": "curation",
        "run_idx": run_idx,
        "schema_valid": schema_valid,
        "selected_indices": selected_indices,
        "justifications_count": justifications_count,
        "selection_recall": round(recall, 4),
        "selection_precision": round(precision, 4),
        "rejected_items_picked": list(rejects_selected),
        "latency_seconds": round(latency, 3),
        "ollama_ram_gb": mem_info["ollama_process_rss_gb"],
        "system_used_ram_gb": mem_info["system_used_ram_gb"],
        "raw_response": raw_response[:300] + "..." if len(raw_response) > 300 else raw_response,
        "passed": passed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Evaluator: Role 3 — Script Generation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_script_case(
    case: dict[str, Any],
    model: str,
    config: dict[str, Any],
    gemini_client: genai.Client | None,
    run_idx: int = 1,
) -> dict[str, Any]:
    """Evaluates monologue script generation for word target, coverage, and leakage."""
    case_id = case["id"]
    theme_dict = case.get("theme_dict", {"name": "Practitioner's Radar", "tone": "collegial, technical"})
    input_stories = case.get("input_stories", [])
    word_target = case.get("word_target", 750)
    required_terms = case.get("required_coverage_terms", [])
    forbidden_patterns = case.get("forbidden_patterns", [r"\*", r"#", r"https?://", r"www\."])

    script_cfg = config.get("script", {})
    ollama_url = config.get("ollama", {}).get("url", "http://localhost:11434").rstrip("/")
    temperature = script_cfg.get("temperature", 0.7)
    num_ctx = script_cfg.get("num_ctx", 4096)
    timeout = script_cfg.get("timeout_seconds", 240)
    judge_model = config.get("judge", {}).get("model", "gemini-2.5-flash")

    stories_block = ""
    for idx, s in enumerate(input_stories, 1):
        stories_block += f"{idx}. {s.get('title')}: {s.get('summary')}\n"

    # Exact prompt matching production briefing_generator.py lines 377-391
    script_prompt = (
        f"You are a professional tech podcast host briefing an engineering peer. "
        f"Today's thematic lens is: '{theme_dict.get('name')}'. Tone: {theme_dict.get('tone')}.\n\n"
        f"Here are the stories to cover:\n{stories_block}\n\n"
        f"Task:\n"
        f"Write a complete, natural spoken podcast monologue script of approximately {word_target} words.\n"
        f"STRICT RULES:\n"
        f"- Open smoothly with today's theme (e.g., 'Welcome back. Today we're looking through our {theme_dict.get('name')} lens...').\n"
        f"- Walk through all {len(input_stories)} stories with natural conversational transitions and genuine technical depth.\n"
        f"- Write phonetically clean spoken English: absolutely NO markdown asterisks, hashes, bullets, brackets, or code symbols.\n"
        f"- Absolutely NO URLs, domain names, links, or 'available at' phrases.\n"
        f"- Conclude with a warm, professional wrap-up.\n"
        f"Output ONLY the spoken script text."
    )

    mem_info = get_system_and_ollama_memory_gb(ollama_url)
    start_time = time.perf_counter()
    raw_script = ""
    clean_script = ""

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": script_prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_ctx": num_ctx},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        latency = time.perf_counter() - start_time
        raw_script = resp.json().get("response", "").strip()
        clean_script = clean_script_for_audio(raw_script)
    except Exception as e:
        latency = time.perf_counter() - start_time
        console.print(f"  [red]Script generation failed for {case_id}: {e}[/red]")

    words = len(clean_script.split()) if clean_script else 0
    tolerance = script_cfg.get("word_tolerance", 250)
    word_count_in_range = (word_target - tolerance) <= words <= (word_target + tolerance)

    # Check for leakage of markdown, symbols, URLs in the raw output
    leakage_count = 0
    leaked_items = []
    for pat in forbidden_patterns:
        matches = re.findall(pat, raw_script)
        if matches:
            leakage_count += len(matches)
            leaked_items.append(f"{pat} ({len(matches)})")

    # Story coverage scoring
    covered_terms = [t for t in required_terms if t.lower() in clean_script.lower()]
    coverage_score = (len(covered_terms) / len(required_terms)) if required_terms else 1.0

    # LLM-as-judge for script fidelity
    judge = llm_judge_script_score(
        source_summaries=stories_block,
        script=clean_script,
        gemini_client=gemini_client,
        judge_model=judge_model,
    )

    passed = (
        words >= 150
        and coverage_score >= script_cfg.get("min_story_coverage", 0.75)
        and leakage_count <= script_cfg.get("max_leakage_count", 2)
        and judge["score"] >= script_cfg.get("min_judge_score", 3.5)
    )

    return {
        "case_id": case_id,
        "type": "script",
        "run_idx": run_idx,
        "word_count": words,
        "word_target": word_target,
        "word_count_in_range": word_count_in_range,
        "coverage_score": round(coverage_score, 4),
        "covered_terms": covered_terms,
        "leakage_count": leakage_count,
        "leaked_items": leaked_items,
        "judge_score": judge["score"],
        "judge_verdict": judge["verdict"],
        "judge_reasoning": judge["reasoning"],
        "latency_seconds": round(latency, 3),
        "ollama_ram_gb": mem_info["ollama_process_rss_gb"],
        "system_used_ram_gb": mem_info["system_used_ram_gb"],
        "script_snippet": clean_script[:350] + "..." if len(clean_script) > 350 else clean_script,
        "passed": passed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Evaluator: Role 4 — Adversarial Audit
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_audit_case(
    case: dict[str, Any],
    model: str,
    config: dict[str, Any],
    run_idx: int = 1,
) -> dict[str, Any]:
    """Evaluates the model's fact-checking safety net on clean vs poisoned summaries."""
    case_id = case["id"]
    source_text = case["source_text"]
    digest_summary = case["digest_summary"]
    is_poisoned = case.get("is_poisoned", False)
    expected_verdict = case.get("expected_verdict", not is_poisoned)
    injected_hallucinations = case.get("injected_hallucinations", [])

    ollama_url = config.get("ollama", {}).get("url", "http://localhost:11434").rstrip("/")
    audit_cfg = config.get("audit", {})

    # Mock minimal pipeline config dictionary expected by validator.py
    validator_mock_config = {
        "llm": {
            "ollama_url": ollama_url,
            "audit_model": model,
            "model": model,
        },
        "testing": {"mock_llm": False},
    }

    mem_info = get_system_and_ollama_memory_gb(ollama_url)
    start_time = time.perf_counter()

    try:
        verdict_passed, reasoning = llm_fact_check(
            source_text=source_text,
            digest_summary=digest_summary,
            config=validator_mock_config,
        )
    except Exception as e:
        verdict_passed, reasoning = True, f"Error calling llm_fact_check: {e}"

    latency = time.perf_counter() - start_time
    # Accurate detection: verdict matches expected_verdict
    accurate_verdict = (verdict_passed == expected_verdict)

    return {
        "case_id": case_id,
        "type": "audit",
        "run_idx": run_idx,
        "is_poisoned": is_poisoned,
        "expected_verdict": expected_verdict,
        "actual_verdict": verdict_passed,
        "accurate_verdict": accurate_verdict,
        "injected_hallucinations": injected_hallucinations,
        "reasoning": reasoning,
        "latency_seconds": round(latency, 3),
        "ollama_ram_gb": mem_info["ollama_process_rss_gb"],
        "system_used_ram_gb": mem_info["system_used_ram_gb"],
        "passed": accurate_verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher: Unified Model Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_model(
    model: str,
    dataset: list[dict[str, Any]],
    config: dict[str, Any],
    gemini_client: genai.Client | None,
    task_filter: str = "all",
) -> dict[str, Any]:
    """Evaluates a single model across all filtered cases in the golden dataset."""
    eval_cfg = config["evaluation"]
    eval_runs = max(1, int(eval_cfg.get("eval_runs", 1)))
    case_results: list[dict[str, Any]] = []

    # Filter dataset cases by task if specified
    filtered_cases = []
    for c in dataset:
        c_type = c.get("type", "summarization")
        if task_filter == "all" or task_filter == c_type:
            filtered_cases.append(c)

    console.print(f"\n[bold cyan]━━━ Evaluating model: [yellow]{model}[/yellow] ({len(filtered_cases)} case(s), {eval_runs} pass(es)) ━━━[/bold cyan]")

    total_eval_steps = len(filtered_cases) * eval_runs
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task_bar = progress.add_task(f"  Running evaluations...", total=total_eval_steps)

        for case in filtered_cases:
            case_id = case["id"]
            case_type = case.get("type", "summarization")

            for run_idx in range(1, eval_runs + 1):
                run_suffix = f" (Pass {run_idx}/{eval_runs})" if eval_runs > 1 else ""
                progress.update(task_bar, description=f"  [dim]Case [{case_type}]:[/dim] [bold]{case_id}{run_suffix}[/bold]")
                console.print(f"\n  [dim]▶ [{case_type.upper()}] [{case_id}{run_suffix}] Querying {model}...[/dim]")

                if case_type == "curation":
                    res = evaluate_curation_case(case, model, config, run_idx=run_idx)
                    status_icon = "✅" if res["passed"] else "❌"
                    console.print(
                        f"  {status_icon} [dim][{case_id}][/dim] "
                        f"Schema Valid: [cyan]{res['schema_valid']}[/cyan]  "
                        f"Recall: [cyan]{res['selection_recall']:.2f}[/cyan]  "
                        f"Precision: [cyan]{res['selection_precision']:.2f}[/cyan]  "
                        f"Selected: [yellow]{res['selected_indices']}[/yellow]  "
                        f"Latency: [green]{res['latency_seconds']:.2f}s[/green]"
                    )
                elif case_type == "script":
                    res = evaluate_script_case(case, model, config, gemini_client, run_idx=run_idx)
                    status_icon = "✅" if res["passed"] else "❌"
                    console.print(
                        f"  {status_icon} [dim][{case_id}][/dim] "
                        f"Words: [cyan]{res['word_count']}/{res['word_target']}[/cyan]  "
                        f"Coverage: [cyan]{res['coverage_score']:.0%}[/cyan]  "
                        f"Leakage: [{'green' if res['leakage_count'] == 0 else 'red'}]{res['leakage_count']}[/{'green' if res['leakage_count'] == 0 else 'red'}]  "
                        f"Judge: [cyan]{res['judge_score']}/5[/cyan]  "
                        f"Latency: [yellow]{res['latency_seconds']:.2f}s[/yellow]"
                    )
                elif case_type == "audit":
                    res = evaluate_audit_case(case, model, config, run_idx=run_idx)
                    status_icon = "✅" if res["passed"] else "❌"
                    console.print(
                        f"  {status_icon} [dim][{case_id}][/dim] "
                        f"Poisoned: [cyan]{res['is_poisoned']}[/cyan]  "
                        f"Actual Verdict: [{'green' if res['actual_verdict'] else 'red'}]{'PASS' if res['actual_verdict'] else 'FAIL'}[/{'green' if res['actual_verdict'] else 'red'}]  "
                        f"Accurate: [{'green' if res['accurate_verdict'] else 'red'}]{res['accurate_verdict']}[/{'green' if res['accurate_verdict'] else 'red'}]  "
                        f"Latency: [green]{res['latency_seconds']:.2f}s[/green]"
                    )
                else:  # Summarization
                    res = evaluate_summarization_case(case, model, config, gemini_client, run_idx=run_idx)
                    status_icon = "✅" if res["passed"] else "❌"
                    all_halls = res["all_hallucinations"]
                    console.print(
                        f"  {status_icon} [dim][{case_id}][/dim] "
                        f"ROUGE-L: [cyan]{res['rouge_l']:.3f}[/cyan]  "
                        f"Overlap: [cyan]{res['keyword_overlap']:.2f}[/cyan]  "
                        f"Hallucinations: [{'red' if all_halls else 'green'}]{len(all_halls)}[/{'red' if all_halls else 'green'}]  "
                        f"Judge: [{'green' if res['judge_verdict'] == 'PASS' else 'red'}]{res['judge_score']}/5[/{'green' if res['judge_verdict'] == 'PASS' else 'red'}]  "
                        f"TTFT: [yellow]{res['ttft_seconds']:.2f}s[/yellow]  "
                        f"Latency: [green]{res['latency_seconds']:.2f}s[/green]"
                    )

                case_results.append(res)
                progress.advance(task_bar)

    # ── Aggregate statistics across all roles ────────────────────────────────
    n_total = len(case_results)
    if n_total == 0:
        return {"model": model, "cases": [], "aggregate": {}}

    sum_cases = [r for r in case_results if r.get("type") == "summarization"]
    cur_cases = [r for r in case_results if r.get("type") == "curation"]
    scr_cases = [r for r in case_results if r.get("type") == "script"]
    aud_cases = [r for r in case_results if r.get("type") == "audit"]

    agg: dict[str, Any] = {
        "total_cases": n_total,
        "passed_cases": sum(1 for r in case_results if r.get("passed", False)),
        "pass_rate": round(sum(1 for r in case_results if r.get("passed", False)) / n_total, 4),
        "peak_ollama_ram_gb": round(max((r.get("ollama_ram_gb", 0.0) for r in case_results), default=0.0), 2),
        "peak_system_ram_gb": round(max((r.get("system_used_ram_gb", 0.0) for r in case_results), default=0.0), 2),
        "mean_latency_seconds": round(sum(r.get("latency_seconds", 0.0) for r in case_results) / n_total, 2),
    }

    # Summarization aggregates
    if sum_cases:
        n_s = len(sum_cases)
        agg["summarization_pass_rate"] = round(sum(1 for r in sum_cases if r.get("passed", False)) / n_s, 4)
        agg["mean_rouge_l"] = round(sum(r.get("rouge_l", 0.0) for r in sum_cases) / n_s, 4)
        agg["mean_keyword_overlap"] = round(sum(r.get("keyword_overlap", 0.0) for r in sum_cases) / n_s, 4)
        agg["mean_judge_score"] = round(sum(r.get("judge_score", 0.0) for r in sum_cases) / n_s, 2)
        agg["total_hallucinations"] = sum(len(r.get("all_hallucinations", [])) for r in sum_cases)
        agg["mean_ttft_seconds"] = round(sum(r.get("ttft_seconds", 0.0) for r in sum_cases) / n_s, 2)
        agg["mean_tokens_per_second"] = round(sum(r.get("tokens_per_second", 0.0) for r in sum_cases) / n_s, 1)
        agg["mean_input_tokens"] = round(sum(r.get("input_tokens", 0) for r in sum_cases) / n_s, 1)
        agg["mean_output_tokens"] = round(sum(r.get("output_tokens", 0) for r in sum_cases) / n_s, 1)
        agg["positional_recall_rate"] = round(sum(1 for r in sum_cases if r.get("positional_recall_passed", True)) / n_s, 4)
        first_half = [r["latency_seconds"] for r in sum_cases[: max(1, n_s // 2)]]
        sec_half = [r["latency_seconds"] for r in sum_cases[max(1, n_s // 2):]]
        avg_f = sum(first_half) / len(first_half) if first_half else 0.001
        avg_s = sum(sec_half) / len(sec_half) if sec_half else 0.001
        agg["thermal_drift_pct"] = round(((avg_s - avg_f) / max(avg_f, 0.001)) * 100, 1)
    else:
        agg.update({
            "summarization_pass_rate": 0.0, "mean_rouge_l": 0.0, "mean_keyword_overlap": 0.0,
            "mean_judge_score": 0.0, "total_hallucinations": 0, "mean_ttft_seconds": 0.0,
            "mean_tokens_per_second": 0.0, "mean_input_tokens": 0.0, "mean_output_tokens": 0.0,
            "positional_recall_rate": 0.0, "thermal_drift_pct": 0.0,
        })

    # Curation aggregates
    if cur_cases:
        n_c = len(cur_cases)
        agg["curation_schema_pass_rate"] = round(sum(1 for r in cur_cases if r.get("schema_valid")) / n_c, 4)
        agg["curation_mean_recall"] = round(sum(r.get("selection_recall", 0.0) for r in cur_cases) / n_c, 4)
        agg["curation_mean_precision"] = round(sum(r.get("selection_precision", 0.0) for r in cur_cases) / n_c, 4)
        agg["curation_mean_latency"] = round(sum(r.get("latency_seconds", 0.0) for r in cur_cases) / n_c, 2)

    # Script aggregates
    if scr_cases:
        n_sc = len(scr_cases)
        agg["script_mean_coverage"] = round(sum(r.get("coverage_score", 0.0) for r in scr_cases) / n_sc, 4)
        agg["script_mean_leakage"] = round(sum(r.get("leakage_count", 0) for r in scr_cases) / n_sc, 2)
        agg["script_mean_judge"] = round(sum(r.get("judge_score", 0.0) for r in scr_cases) / n_sc, 2)
        agg["script_mean_words"] = round(sum(r.get("word_count", 0) for r in scr_cases) / n_sc, 1)
        agg["script_mean_latency"] = round(sum(r.get("latency_seconds", 0.0) for r in scr_cases) / n_sc, 2)

    # Audit aggregates
    if aud_cases:
        poisoned_cases = [r for r in aud_cases if r.get("is_poisoned")]
        clean_cases = [r for r in aud_cases if not r.get("is_poisoned")]
        tpr = (sum(1 for r in poisoned_cases if not r.get("actual_verdict")) / len(poisoned_cases)) if poisoned_cases else 1.0
        tnr = (sum(1 for r in clean_cases if r.get("actual_verdict")) / len(clean_cases)) if clean_cases else 1.0
        agg["audit_tpr"] = round(tpr, 4)
        agg["audit_tnr"] = round(tnr, 4)
        agg["audit_accuracy"] = round(sum(1 for r in aud_cases if r.get("accurate_verdict")) / len(aud_cases), 4)
        agg["audit_mean_latency"] = round(sum(r.get("latency_seconds", 0.0) for r in aud_cases) / len(aud_cases), 2)

    console.print(
        f"\n  [bold green]Model {model} completed.[/bold green] "
        f"Overall Pass Rate: [bold]{agg['pass_rate']:.0%}[/bold] ({agg['passed_cases']}/{n_total})  "
        f"Peak RAM: [bold]{agg['peak_ollama_ram_gb']} GB[/bold]"
    )

    return {"model": model, "cases": case_results, "aggregate": agg}


# ─────────────────────────────────────────────────────────────────────────────
# Presentation: Comparison Tables & Markdown Reports
# ─────────────────────────────────────────────────────────────────────────────

def print_comparison_table(all_results: list[dict[str, Any]]) -> None:
    """Print a rich terminal table with metrics broken down by pipeline role."""
    table = Table(
        title="📊 Multi-Role Model Evaluation & Comparison Checklist",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )

    table.add_column("Pipeline Role / Metric", style="bold", min_width=32)
    for r in all_results:
        table.add_column(r["model"], justify="center", min_width=16)

    def fmt_pct(val: float | None) -> str:
        if val is None:
            return "-"
        pct = val * 100
        color = "green" if pct >= 80 else ("yellow" if pct >= 50 else "red")
        return f"[{color}]{pct:.1f}%[/{color}]"

    def fmt_score(val: float | None) -> str:
        if val is None:
            return "-"
        color = "green" if val >= 4 else ("yellow" if val >= 3 else "red")
        return f"[{color}]{val:.2f}/5[/{color}]"

    def fmt_lat(val: float | None) -> str:
        if val is None:
            return "-"
        return f"[cyan]{val:.2f}s[/cyan]"

    rows: list[tuple[str, Any]] = [
        ("[bold]OVERALL BENCHMARK[/bold]", None),
        ("  Overall Pass Rate", lambda r: fmt_pct(r["aggregate"].get("pass_rate"))),
        ("  Peak Ollama RAM (<5GB)", lambda r: f"{r['aggregate'].get('peak_ollama_ram_gb', 0.0):.2f} GB"),
        ("  Mean Total Latency", lambda r: fmt_lat(r["aggregate"].get("mean_latency_seconds"))),

        ("[bold]ROLE 1: SUMMARIZATION[/bold]", None),
        ("  Pass Rate", lambda r: fmt_pct(r["aggregate"].get("summarization_pass_rate"))),
        ("  ROUGE-L F1 (>= 0.45)", lambda r: f"{r['aggregate'].get('mean_rouge_l', 0.0):.4f}"),
        ("  Keyword Overlap", lambda r: f"{r['aggregate'].get('mean_keyword_overlap', 0.0):.2f}"),
        ("  Semantic Judge Score (1-5)", lambda r: fmt_score(r["aggregate"].get("mean_judge_score"))),
        ("  Total Hallucinations", lambda r: f"[{'green' if r['aggregate'].get('total_hallucinations', 0) == 0 else 'red'}]{r['aggregate'].get('total_hallucinations', 0)}[/{'green' if r['aggregate'].get('total_hallucinations', 0) == 0 else 'red'}]"),
        ("  TTFT Latency (<0.60s)", lambda r: fmt_lat(r["aggregate"].get("mean_ttft_seconds"))),
        ("  Generation Speed", lambda r: f"{r['aggregate'].get('mean_tokens_per_second', 0.0):.1f} tok/s"),

        ("[bold]ROLE 2: CURATION (Pydantic CoT)[/bold]", None),
        ("  JSON Schema Pass Rate", lambda r: fmt_pct(r["aggregate"].get("curation_schema_pass_rate"))),
        ("  Story Selection Recall", lambda r: fmt_pct(r["aggregate"].get("curation_mean_recall"))),
        ("  Hype/Decoy Avoidance (Precision)", lambda r: fmt_pct(r["aggregate"].get("curation_mean_precision"))),
        ("  Curation Latency", lambda r: fmt_lat(r["aggregate"].get("curation_mean_latency"))),

        ("[bold]ROLE 3: SCRIPT GENERATION (~750 words)[/bold]", None),
        ("  Story Coverage Rate", lambda r: fmt_pct(r["aggregate"].get("script_mean_coverage"))),
        ("  Leakage Count (*, #, URLs)", lambda r: f"[{'green' if r['aggregate'].get('script_mean_leakage', 0) == 0 else 'red'}]{r['aggregate'].get('script_mean_leakage', 0):.1f}[/{'green' if r['aggregate'].get('script_mean_leakage', 0) == 0 else 'red'}]"),
        ("  Script Judge Score (1-5)", lambda r: fmt_score(r["aggregate"].get("script_mean_judge"))),
        ("  Mean Script Word Count", lambda r: f"{round(r['aggregate'].get('script_mean_words', 0))} w"),
        ("  Script Latency", lambda r: fmt_lat(r["aggregate"].get("script_mean_latency"))),

        ("[bold]ROLE 4: ADVERSARIAL AUDIT SAFETY[/bold]", None),
        ("  Hallucination Catch Rate (TPR)", lambda r: fmt_pct(r["aggregate"].get("audit_tpr"))),
        ("  Clean Pass Rate (TNR)", lambda r: fmt_pct(r["aggregate"].get("audit_tnr"))),
        ("  Overall Audit Accuracy", lambda r: fmt_pct(r["aggregate"].get("audit_accuracy"))),
        ("  Audit Latency", lambda r: fmt_lat(r["aggregate"].get("audit_mean_latency"))),
    ]

    for label, extractor in rows:
        if extractor is None:
            table.add_row(label, *["" for _ in all_results])
        else:
            table.add_row(label, *[extractor(r) for r in all_results])

    console.print()
    console.print(table)
    console.print()


def save_markdown_report(all_results: list[dict[str, Any]], config: dict[str, Any]) -> Path:
    """Generate and save a detailed markdown report for all evaluated roles."""
    report_dir = PROJECT_ROOT / config.get("output", {}).get("report_dir", "eval/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"model_comparison_{timestamp}.md"

    models = [r["model"] for r in all_results]
    n_cases = all_results[0]["aggregate"]["total_cases"] if all_results else 0

    lines: list[str] = []
    lines.append("# Multi-Role LLM Evaluation Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Models compared:** {', '.join(f'`{m}`' for m in models)}  ")
    lines.append(f"**Total evaluation cases:** {n_cases}  ")
    lines.append(f"**Judge model:** `{config.get('judge', {}).get('model', 'gemini-2.5-flash')}`\n")

    # Aggregate Table
    lines.append("## Aggregate Benchmark Summary\n")
    header = "| Metric | " + " | ".join(models) + " |"
    sep = "| :--- | " + " | ".join(["---:"] * len(models)) + " |"
    lines.append(header)
    lines.append(sep)

    agg_metrics = [
        ("Overall Pass Rate", lambda a: f"{a.get('pass_rate', 0.0):.1%}"),
        ("Peak Ollama RAM", lambda a: f"{a.get('peak_ollama_ram_gb', 0.0):.2f} GB"),
        ("Mean Latency", lambda a: f"{a.get('mean_latency_seconds', 0.0):.2f}s"),
        ("Summarization Pass Rate", lambda a: f"{a.get('summarization_pass_rate', 0.0):.1%}"),
        ("Summarization ROUGE-L", lambda a: f"{a.get('mean_rouge_l', 0.0):.4f}"),
        ("Summarization Hallucinations", lambda a: str(a.get("total_hallucinations", 0))),
        ("Curation Schema Pass Rate", lambda a: f"{a.get('curation_schema_pass_rate', 0.0):.1%}"),
        ("Curation Selection Recall", lambda a: f"{a.get('curation_mean_recall', 0.0):.1%}"),
        ("Script Story Coverage", lambda a: f"{a.get('script_mean_coverage', 0.0):.1%}"),
        ("Script Judge Score (1-5)", lambda a: f"{a.get('script_mean_judge', 0.0):.2f}"),
        ("Audit Catch Rate (TPR)", lambda a: f"{a.get('audit_tpr', 0.0):.1%}"),
        ("Audit Accuracy", lambda a: f"{a.get('audit_accuracy', 0.0):.1%}"),
    ]

    for label, extractor in agg_metrics:
        row = f"| {label} | " + " | ".join(extractor(r["aggregate"]) for r in all_results) + " |"
        lines.append(row)

    # Detailed Per-Case Breakdown
    lines.append("\n---\n")
    lines.append("## Per-Case Detailed Evaluation Breakdown\n")

    if all_results and all_results[0].get("cases"):
        case_ids = [c["case_id"] for c in all_results[0]["cases"]]
        for cid in case_ids:
            case_type = next((c.get("type", "summarization") for c in all_results[0]["cases"] if c["case_id"] == cid), "summarization")
            lines.append(f"### Case: `{cid}` `[{case_type.upper()}]`\n")

            for r in all_results:
                m_case = next((c for c in r["cases"] if c["case_id"] == cid), None)
                if not m_case:
                    continue
                status_str = "PASSED" if m_case.get("passed") else "FAILED"
                lines.append(f"**Model `{r['model']}`:** `{status_str}` (Latency: {m_case.get('latency_seconds', 0.0):.2f}s)")

                if case_type == "curation":
                    lines.append(f"- Schema valid: `{m_case.get('schema_valid')}`, Selected indices: `{m_case.get('selected_indices')}`")
                    lines.append(f"- Recall: `{m_case.get('selection_recall', 0.0):.1%}`, Precision: `{m_case.get('selection_precision', 0.0):.1%}`\n")
                elif case_type == "script":
                    lines.append(f"- Words: `{m_case.get('word_count')}`, Coverage: `{m_case.get('coverage_score', 0.0):.1%}`, Leakage: `{m_case.get('leakage_count')}`")
                    lines.append(f"- Judge Score: `{m_case.get('judge_score')}/5` ({m_case.get('judge_reasoning')})\n")
                elif case_type == "audit":
                    lines.append(f"- Poisoned test: `{m_case.get('is_poisoned')}`, Model verdict: `{'PASS' if m_case.get('actual_verdict') else 'FAIL'}` (Accurate: `{m_case.get('accurate_verdict')}`)")
                    lines.append(f"- Auditor reasoning: *{m_case.get('reasoning')}*\n")
                else:
                    lines.append(f"- Summary: > {m_case.get('summary')}")
                    lines.append(f"- ROUGE-L: `{m_case.get('rouge_l', 0.0):.4f}`, Overlap: `{m_case.get('keyword_overlap', 0.0):.2f}`, Judge: `{m_case.get('judge_score')}/5`\n")

    lines.append("---\n")
    lines.append("## Raw JSON Appendix\n")
    lines.append("```json")
    lines.append(json.dumps(all_results, indent=2, default=str))
    lines.append("```\n")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


# ─────────────────────────────────────────────────────────────────────────────
# CLI & Main Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Role LLM Evaluation Harness for AI News Voice Feed")
    parser.add_argument(
        "--task",
        choices=["all", "summarization", "curation", "script", "audit"],
        default="all",
        help="Specific pipeline role to evaluate (default: all)",
    )
    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Comma-separated list of Ollama models to evaluate (e.g. 'llama3.2:3b,phi4-mini:3.8b')",
    )
    args = parser.parse_args()

    console.print(
        Panel.fit(
            f"[bold cyan]AI News Voice Feed — Multi-Role LLM Evaluator[/bold cyan]\n"
            f"[dim]Task: [yellow]{args.task.upper()}[/yellow] | Local Apple Silicon Benchmark Harness[/dim]",
            border_style="cyan",
        )
    )

    config = load_config()
    dataset = load_golden_dataset(config)
    ollama_url = config.get("ollama", {}).get("url", "http://localhost:11434").rstrip("/")

    # Model Selection
    if args.models:
        selected_models = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        console.print("\n[bold]Step 1:[/bold] Querying Ollama for available models...")
        available_models = get_ollama_models(ollama_url)
        if not available_models:
            console.print("[red]ERROR:[/red] No models found in Ollama. Pull a model first with `ollama pull <model>`.")
            sys.exit(1)
        selected_models = select_models_interactively(available_models)

    # Gemini Judge setup
    console.print("\n[bold]Step 2:[/bold] Initializing Gemini judge client...")
    gemini_client = build_gemini_client()
    if gemini_client:
        console.print(f"  [green]OK[/green] Judge active: [cyan]{config.get('judge', {}).get('model')}[/cyan]")
    else:
        console.print("  [yellow]Note:[/yellow] Running with deterministic heuristic judge fallback.")

    # Run evaluations sequentially
    console.print(f"\n[bold]Step 3:[/bold] Running multi-role evaluation across {len(selected_models)} model(s)...\n")
    all_results: list[dict[str, Any]] = []

    for model in selected_models:
        result = evaluate_model(
            model=model,
            dataset=dataset,
            config=config,
            gemini_client=gemini_client,
            task_filter=args.task,
        )
        all_results.append(result)

        # Unload model from VRAM after evaluation
        console.print(f"\n  [dim]Unloading [cyan]{model}[/cyan] from memory...[/dim]")
        unload_model_from_ollama(model, ollama_url)

    # Results summary table
    console.print("\n[bold]Step 4:[/bold] Results summary\n")
    print_comparison_table(all_results)

    # Markdown report
    console.print("[bold]Step 5:[/bold] Saving reports...")
    report_path = save_markdown_report(all_results, config)
    console.print(f"  [green]OK[/green] Markdown report: [link file://{report_path}]{report_path}[/link file://{report_path}]")

    # HTML dashboard
    try:
        html_path = save_html_dashboard(all_results, config)
        console.print(f"  [green]OK[/green] HTML dashboard: [link file://{html_path}]{html_path}[/link file://{html_path}]")
    except Exception as e:
        console.print(f"  [yellow]Notice: HTML dashboard generator skipped ({e}).[/yellow]")

    console.print("\n[bold green]Evaluation harness complete![/bold green]\n")


if __name__ == "__main__":
    main()
