#!/usr/bin/env python3
"""
model_comparator.py
===================
Standalone, reusable LLM summarization benchmark module.

Compares multiple Ollama models on a golden dataset of source texts using
six evaluation dimensions:
  1. ROUGE-L F1        – measures recall of key phrase sequences
  2. Keyword Overlap   – fraction of expected facts present in the summary
  3. Hallucination     – fabricated terms not found in the source text
  4. Summary Length    – word count and sentence count
  5. Latency           – seconds taken to generate the summary
  6. LLM-as-Judge      – Gemini 2.5 Flash factual accuracy score (1–5) + verdict

Usage:
  uv run eval/model_comparator.py

The script will:
  - Query Ollama for available models and prompt you to select which to compare.
  - Run each model sequentially, unloading it from VRAM after evaluation.
  - Print a rich terminal table summary and save a markdown report.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Dependency check ────────────────────────────────────────────────────────
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
    import psutil
except ImportError:
    psutil = None  # Optional memory tracking

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional — env vars can be set in shell

# ── Import HTML Dashboard Generator ─────────────────────────────────────────
try:
    from eval.save_html import save_html_dashboard
except ImportError:
    try:
        from save_html import save_html_dashboard
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from save_html import save_html_dashboard  # type: ignore[no-redef]

# ── Constants ────────────────────────────────────────────────────────────────
EVAL_DIR = Path(__file__).parent
PROJECT_ROOT = EVAL_DIR.parent
CONFIG_PATH = EVAL_DIR / "eval_config.toml"

console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# Config Loading
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
    console.print(f"[dim]Loaded {len(data)} evaluation cases from {dataset_path.name}[/dim]")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# Ollama Utilities
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
    """
    Generate a summary using Ollama.
    Returns (summary_text, latency_seconds, ttft_seconds, tokens_per_second, input_tokens, output_tokens).
    """
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

        # Calculate tokens per second from Ollama's metadata or overall timing
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


def unload_model_from_ollama(model: str, ollama_url: str) -> None:
    """
    Instruct Ollama to unload a model from VRAM by setting keep_alive=0.
    This is important on memory-constrained machines (e.g. 8GB RAM).
    """
    try:
        requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": "", "keep_alive": 0, "stream": False},
            timeout=15,
        )
        console.print(f"  [dim]Model [cyan]{model}[/cyan] unloaded from memory.[/dim]")
    except Exception:
        pass  # Non-critical


# ─────────────────────────────────────────────────────────────────────────────
# Metric Computation
# ─────────────────────────────────────────────────────────────────────────────

_rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)


def compute_rouge_l(source_text: str, summary: str) -> float:
    """Compute ROUGE-L F1 between the source text and the generated summary."""
    if not summary:
        return 0.0
    scores = _rouge.score(source_text, summary)
    return round(scores["rougeL"].fmeasure, 4)


def compute_keyword_overlap(source_text: str, summary: str, expected_facts: list[str]) -> float:
    """
    Fraction of expected_facts that appear (case-insensitive substring match) in the summary.
    This is a targeted precision check: did the model preserve the key facts?
    """
    if not expected_facts or not summary:
        return 0.0
    summary_lower = summary.lower()
    hits = sum(1 for fact in expected_facts if fact.lower() in summary_lower)
    return round(hits / len(expected_facts), 4)


def detect_hallucinations(source_text: str, summary: str) -> list[str]:
    """
    Simple heuristic hallucination detector.
    Flags capitalized multi-word tokens (Named Entities, numbers, percentages)
    that appear in the summary but NOT in the source text.
    """
    if not summary:
        return []

    # Extract candidate hallucination tokens: numbers, percentages, capitalized proper nouns
    candidate_patterns = [
        r"\b\d+(?:\.\d+)?%\b",                 # percentages
        r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",       # numbers
        r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]+)+\b",  # Capitalized multi-word phrases
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
    """Return word count and sentence count for the summary."""
    words = len(summary.split()) if summary else 0
    sentences = len([s for s in re.split(r"[.!?]+", summary) if s.strip()]) if summary else 0
    return {"word_count": words, "sentence_count": sentences}


# ─────────────────────────────────────────────────────────────────────────────
# LLM-as-Judge (Gemini 2.5 Flash)
# ─────────────────────────────────────────────────────────────────────────────

def get_system_and_ollama_memory_gb(ollama_url: str = "http://localhost:11434") -> dict[str, float]:
    """
    Measures RAM usage across the system and Ollama process:
    - process_rss_gb: Python test runner's RSS memory
    - ollama_process_rss_gb: Cumulative RSS RAM of running Ollama processes
    - system_used_ram_gb: Total used system RAM (reflects Apple Silicon Unified Memory pressure)
    """
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
# LLM-as-Judge (Gemini 2.5 Flash / Fallback)
# ─────────────────────────────────────────────────────────────────────────────

def build_gemini_client() -> genai.Client | None:
    """Build and return an authenticated Gemini Gen AI client if API key is present."""
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


def _heuristic_judge_score(
    source_text: str,
    summary: str,
    expected_facts: list[str] | None,
    lexical_hallucinations: list[str] | None,
    reason_prefix: str,
) -> dict[str, Any]:
    """Deterministic fallback judge when Gemini API is offline or quota is exceeded."""
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
    judge_model: str,
    expected_facts: list[str] | None = None,
    lexical_hallucinations: list[str] | None = None,
) -> dict[str, Any]:
    """
    Use Gemini as an LLM-as-judge to evaluate summary accuracy & semantic hallucinations.
    If Gemini is unavailable or quota is exceeded, falls back to deterministic heuristic validation.
    """
    if not summary:
        return {
            "score": 1,
            "verdict": "FAIL",
            "conceptual_hallucinations": [],
            "reasoning": "Empty summary generated.",
            "api_error": False,
        }

    if gemini_client is None:
        return _heuristic_judge_score(source_text, summary, expected_facts, lexical_hallucinations, "Heuristic Fallback")

    prompt = _JUDGE_PROMPT_TEMPLATE.format(source_text=source_text, summary=summary)
    try:
        response = gemini_client.models.generate_content(
            model=judge_model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )
        raw = response.text.strip()
        result = json.loads(raw)
        return {
            "score": int(result.get("score", 1)),
            "verdict": str(result.get("verdict", "FAIL")).upper(),
            "conceptual_hallucinations": result.get("conceptual_hallucinations", []),
            "reasoning": str(result.get("reasoning", "")),
            "api_error": False,
        }
    except Exception as e:
        # Avoid penalizing candidate model for Gemini API quota or network issues
        err_msg = str(e)
        if "402" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "credits are depleted" in err_msg:
            prefix = "API Quota Depleted"
        elif "429" in err_msg or "RATE_LIMIT" in err_msg:
            prefix = "API Rate Limit"
        else:
            prefix = f"API Error ({type(e).__name__})"

        return _heuristic_judge_score(
            source_text=source_text,
            summary=summary,
            expected_facts=expected_facts,
            lexical_hallucinations=lexical_hallucinations,
            reason_prefix=prefix,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Per-Model Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_model(
    model: str,
    dataset: list[dict[str, Any]],
    config: dict[str, Any],
    gemini_client: genai.Client | None,
) -> dict[str, Any]:
    """
    Run all evaluation cases for a single model.
    Returns a structured result dict with per-case details and aggregate stats.
    """
    ollama_cfg = config["ollama"]
    ollama_url = ollama_cfg["url"].rstrip("/")
    temperature = ollama_cfg["temperature"]
    num_ctx = ollama_cfg["num_ctx"]
    timeout = ollama_cfg["timeout_seconds"]
    prompt_template = config["summarization"]["prompt_template"]
    judge_model = config["judge"]["model"]
    eval_cfg = config["evaluation"]
    min_overlap = eval_cfg["min_keyword_overlap"]
    min_rouge = eval_cfg.get("min_rouge_l", 0.45)
    stream_mode = ollama_cfg.get("stream", True)
    eval_runs = max(1, int(eval_cfg.get("eval_runs", 1)))
    case_results = []

    console.print(f"\n[bold cyan]━━━ Evaluating model: [yellow]{model}[/yellow] ({eval_runs} pass(es) per case) ━━━[/bold cyan]")

    total_eval_steps = len(dataset) * eval_runs
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"  Running {total_eval_steps} evaluations...", total=total_eval_steps)

        for case in dataset:
            case_id = case["id"]
            source_text = case["source_text"]
            expected_facts = case.get("expected_facts", [])

            for run_idx in range(1, eval_runs + 1):
                run_suffix = f" (Pass {run_idx}/{eval_runs})" if eval_runs > 1 else ""
                progress.update(task, description=f"  [dim]Case:[/dim] [bold]{case_id}{run_suffix}[/bold]")

                # ── 1. Generate summary + measure latency, speed, and RAM ──────────────────────
                console.print(f"\n  [dim]▶ [{case_id}{run_suffix}] Generating summary with {model}...[/dim]")
                mem_info = get_system_and_ollama_memory_gb(ollama_url)

                try:
                    summary, latency, ttft, tok_per_sec, input_toks, output_toks = generate_summary_ollama(
                        source_text=source_text,
                        model=model,
                        prompt_template=prompt_template,
                        ollama_url=ollama_url,
                        temperature=temperature,
                        num_ctx=num_ctx,
                        timeout=timeout,
                        stream=stream_mode,
                    )
                    gen_error = None
                except Exception as e:
                    summary, latency, ttft, tok_per_sec, input_toks, output_toks = "", 0.0, 0.0, 0.0, 0, 0
                    gen_error = str(e)
                    console.print(f"  [red]  ERROR generating summary for {case_id}: {e}[/red]")

                # ── 2. Compute lexical metrics ─────────────────────────────────────────
                rouge_l = compute_rouge_l(source_text, summary)
                keyword_overlap = compute_keyword_overlap(source_text, summary, expected_facts)
                lexical_hallucinations = detect_hallucinations(source_text, summary)
                length = compute_length_metrics(summary)

                # Positional Recall check (if case contains middle_buried_facts)
                buried_facts = case.get("middle_buried_facts", [])
                positional_recall_passed = True
                if buried_facts:
                    found_buried = sum(1 for bf in buried_facts if bf.lower() in summary.lower())
                    positional_recall_passed = (found_buried == len(buried_facts))

                # ── 3. LLM-as-judge (Semantic Accuracy, Tone & Conceptual Hallucinations) ──────
                judge_tag = f"Gemini ({judge_model})" if gemini_client else "Heuristic Judge"
                console.print(f"  [dim]▶ [{case_id}{run_suffix}] Running {judge_tag}...[/dim]")
                judge = llm_judge_score(
                    source_text=source_text,
                    summary=summary,
                    gemini_client=gemini_client,
                    judge_model=judge_model,
                    expected_facts=expected_facts,
                    lexical_hallucinations=lexical_hallucinations,
                )

                # Combine lexical (regex token) + conceptual (LLM reasoning) hallucinations
                conceptual_hallucinations = judge.get("conceptual_hallucinations", [])
                all_hallucinations = list(set(lexical_hallucinations + conceptual_hallucinations))

                # ── 4. Determine pass/fail ────────────────────────────────────
                passed = (
                    rouge_l >= min_rouge
                    and keyword_overlap >= min_overlap
                    and len(all_hallucinations) == 0
                    and judge["verdict"] == "PASS"
                    and positional_recall_passed
                )

                status_icon = "✅" if passed else "❌"
                console.print(
                    f"  {status_icon} [dim][{case_id}{run_suffix}][/dim] "
                    f"ROUGE-L: [cyan]{rouge_l:.3f}[/cyan]  "
                    f"Overlap: [cyan]{keyword_overlap:.2f}[/cyan]  "
                    f"Hallucinations: [{'red' if all_hallucinations else 'green'}]{len(all_hallucinations)}[/{'red' if all_hallucinations else 'green'}]  "
                    f"Judge: [{'green' if judge['verdict'] == 'PASS' else 'red'}]{judge['score']}/5[/{'green' if judge['verdict'] == 'PASS' else 'red'}]  "
                    f"TTFT: [yellow]{ttft:.2f}s[/yellow]  "
                    f"Ollama RAM: [cyan]{mem_info['ollama_process_rss_gb']:.2f}GB[/cyan]"
                )

                case_results.append({
                    "case_id": case_id,
                    "run_idx": run_idx,
                    "summary": summary,
                    "latency_seconds": round(latency, 3),
                    "ttft_seconds": round(ttft, 3),
                    "tokens_per_second": round(tok_per_sec, 2),
                    "input_tokens": input_toks,
                    "output_tokens": output_toks,
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
                })
                progress.advance(task)

    # ── Aggregate stats ──────────────────────────────────────────────────────
    n = len(case_results)
    if n == 0:
        return {"model": model, "cases": [], "aggregate": {}}

    first_half_lat = [r["latency_seconds"] for r in case_results[: max(1, n // 2)]]
    second_half_lat = [r["latency_seconds"] for r in case_results[max(1, n // 2):]]
    avg_first = sum(first_half_lat) / len(first_half_lat) if first_half_lat else 0.001
    avg_second = sum(second_half_lat) / len(second_half_lat) if second_half_lat else 0.001
    thermal_drift_pct = round(((avg_second - avg_first) / max(avg_first, 0.001)) * 100, 1)

    agg = {
        "total_cases": n,
        "passed_cases": sum(1 for r in case_results if r["passed"]),
        "pass_rate": round(sum(1 for r in case_results if r["passed"]) / n, 4),
        "mean_rouge_l": round(sum(r["rouge_l"] for r in case_results) / n, 4),
        "mean_keyword_overlap": round(sum(r["keyword_overlap"] for r in case_results) / n, 4),
        "mean_judge_score": round(sum(r["judge_score"] for r in case_results) / n, 2),
        "total_hallucinations": sum(len(r["all_hallucinations"]) for r in case_results),
        "mean_latency_seconds": round(sum(r["latency_seconds"] for r in case_results) / n, 2),
        "mean_ttft_seconds": round(sum(r["ttft_seconds"] for r in case_results) / n, 2),
        "mean_tokens_per_second": round(sum(r["tokens_per_second"] for r in case_results) / n, 1),
        "mean_input_tokens": round(sum(r["input_tokens"] for r in case_results) / n, 1),
        "mean_output_tokens": round(sum(r["output_tokens"] for r in case_results) / n, 1),
        "peak_ollama_ram_gb": round(max((r["ollama_ram_gb"] for r in case_results), default=0.0), 2),
        "peak_system_ram_gb": round(max((r["system_used_ram_gb"] for r in case_results), default=0.0), 2),
        "thermal_drift_pct": thermal_drift_pct,
        "positional_recall_rate": round(sum(1 for r in case_results if r["positional_recall_passed"]) / n, 4),
        "mean_word_count": round(sum(r["word_count"] for r in case_results) / n, 1),
    }

    console.print(
        f"\n  [bold green]Done.[/bold green] "
        f"Pass rate: [bold]{agg['pass_rate']:.0%}[/bold] ({agg['passed_cases']}/{n})  "
        f"Ollama RAM: [bold]{agg['peak_ollama_ram_gb']}GB[/bold]  "
        f"System RAM: [bold]{agg['peak_system_ram_gb']}GB[/bold]"
    )

    return {"model": model, "cases": case_results, "aggregate": agg}


# ─────────────────────────────────────────────────────────────────────────────
# Rich Terminal Report
# ─────────────────────────────────────────────────────────────────────────────

def print_comparison_table(all_results: list[dict[str, Any]]) -> None:
    """Print a rich side-by-side model comparison table to the terminal."""
    table = Table(
        title="📊 LLM Summarization Model Comparison Checklist",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )

    table.add_column("Category / Metric", style="bold", min_width=24)
    for r in all_results:
        table.add_column(r["model"], justify="center", min_width=16)

    def fmt_pct(val: float) -> str:
        pct = val * 100
        color = "green" if pct >= 80 else ("yellow" if pct >= 50 else "red")
        return f"[{color}]{pct:.1f}%[/{color}]"

    def fmt_score(val: float) -> str:
        color = "green" if val >= 4 else ("yellow" if val >= 3 else "red")
        return f"[{color}]{val:.2f}/5[/{color}]"

    def fmt_rouge(val: float) -> str:
        color = "green" if val >= 0.45 else ("yellow" if val >= 0.20 else "red")
        return f"[{color}]{val:.4f}[/{color}]"

    def fmt_overlap(val: float) -> str:
        color = "green" if val >= 0.60 else ("yellow" if val >= 0.35 else "red")
        return f"[{color}]{val:.2f}[/{color}]"

    def fmt_hallucinations(val: int) -> str:
        return f"[green]{val}[/green]" if val == 0 else f"[red]{val}[/red]"

    def fmt_latency(val: float) -> str:
        color = "green" if val <= 3.0 else ("yellow" if val <= 10.0 else "red")
        return f"[{color}]{val:.2f}s[/{color}]"

    def fmt_ttft(val: float) -> str:
        color = "green" if val <= 0.60 else ("yellow" if val <= 2.0 else "red")
        return f"[{color}]{val:.2f}s[/{color}]"

    def fmt_ram(val: float) -> str:
        color = "green" if val <= 5.0 else "red"
        return f"[{color}]{val:.2f} GB[/{color}]"

    def fmt_drift(val: float) -> str:
        color = "green" if val <= 15.0 else "red"
        return f"[{color}]{val:+.1f}%[/{color}]"

    rows = [
        ("Pass Rate", lambda r: fmt_pct(r["aggregate"]["pass_rate"])),
        ("Memory: Ollama RAM (< 5.0GB)", lambda r: fmt_ram(r["aggregate"].get("peak_ollama_ram_gb", 0.0))),
        ("Memory: System Total Used RAM", lambda r: fmt_ram(r["aggregate"].get("peak_system_ram_gb", 0.0))),
        ("Latency TTFT (< 600ms target)", lambda r: fmt_ttft(r["aggregate"]["mean_ttft_seconds"])),
        ("Total Latency (< 3.0s target)", lambda r: fmt_latency(r["aggregate"]["mean_latency_seconds"])),
        ("Lexical Overlap (ROUGE-L >= 0.45)", lambda r: fmt_rouge(r["aggregate"]["mean_rouge_l"])),
        ("Keyword Overlap Score", lambda r: fmt_overlap(r["aggregate"]["mean_keyword_overlap"])),
        ("Semantic Judge Score (1-5)", lambda r: fmt_score(r["aggregate"]["mean_judge_score"])),
        ("Hallucination Count (Lexical + Semantic)", lambda r: fmt_hallucinations(r["aggregate"]["total_hallucinations"])),
        ("Positional Recall Rate", lambda r: fmt_pct(r["aggregate"]["positional_recall_rate"])),
        ("Thermal Stability Drift (< 15%)", lambda r: fmt_drift(r["aggregate"]["thermal_drift_pct"])),
        ("Mean Speed (tok/s)", lambda r: f"{r['aggregate']['mean_tokens_per_second']:.1f} tok/s"),
        ("Mean Tokens (Prompt / Summary)", lambda r: f"{round(r['aggregate']['mean_input_tokens'])} / {round(r['aggregate']['mean_output_tokens'])}"),
    ]

    for label, extractor in rows:
        table.add_row(label, *[extractor(r) for r in all_results])

    console.print()
    console.print(table)
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Markdown Report
# ─────────────────────────────────────────────────────────────────────────────

def save_markdown_report(all_results: list[dict[str, Any]], config: dict[str, Any]) -> Path:
    """Generate and save a detailed markdown report."""
    report_dir = PROJECT_ROOT / config["output"]["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"model_comparison_{timestamp}.md"

    models = [r["model"] for r in all_results]
    n_cases = all_results[0]["aggregate"]["total_cases"] if all_results else 0

    lines: list[str] = []
    lines.append("# LLM Summarization Model Comparison Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Models compared:** {', '.join(f'`{m}`' for m in models)}  ")
    lines.append(f"**Evaluation cases:** {n_cases}  ")
    lines.append(f"**Judge model:** `{config['judge']['model']}`\n")

    # ── Aggregate summary table ─────────────────────────────────────────────
    lines.append("## Aggregate Results\n")
    header = "| Metric | " + " | ".join(models) + " |"
    sep = "| :--- | " + " | ".join(["---:"] * len(models)) + " |"
    lines.append(header)
    lines.append(sep)

    agg_rows = [
        ("Pass Rate", lambda a: f"{a['pass_rate']:.0%}"),
        ("Mean ROUGE-L F1", lambda a: f"{a['mean_rouge_l']:.4f}"),
        ("Mean Keyword Overlap", lambda a: f"{a['mean_keyword_overlap']:.2f}"),
        ("Mean Judge Score (1-5)", lambda a: f"{a['mean_judge_score']:.2f}"),
        ("Total Hallucinations", lambda a: str(a["total_hallucinations"])),
        ("Peak Ollama RAM", lambda a: f"{a.get('peak_ollama_ram_gb', 0.0):.2f} GB"),
        ("Peak System Used RAM", lambda a: f"{a.get('peak_system_ram_gb', 0.0):.2f} GB"),
        ("Mean Input Tokens (Prompt)", lambda a: str(round(a["mean_input_tokens"]))),
        ("Mean Output Tokens (Summary)", lambda a: str(round(a["mean_output_tokens"]))),
        ("Mean TTFT (s)", lambda a: f"{a['mean_ttft_seconds']:.2f}s"),
        ("Mean Speed (tok/s)", lambda a: f"{a['mean_tokens_per_second']:.1f}"),
        ("Mean Total Latency (s)", lambda a: f"{a['mean_latency_seconds']:.2f}s"),
        ("Thermal Drift (%)", lambda a: f"{a.get('thermal_drift_pct', 0.0):+.1f}%"),
        ("Positional Recall Rate", lambda a: f"{a.get('positional_recall_rate', 0.0):.0%}"),
        ("Mean Word Count", lambda a: str(round(a["mean_word_count"]))),
        ("Cases Passed / Total", lambda a: f"{a['passed_cases']}/{a['total_cases']}"),
    ]

    for label, extractor in agg_rows:
        row = f"| {label} | " + " | ".join(extractor(r["aggregate"]) for r in all_results) + " |"
        lines.append(row)

    # ── Per-case detail sections ────────────────────────────────────────────
    lines.append("\n---\n")
    lines.append("## Per-Case Results\n")

    case_ids = [c["case_id"] for c in all_results[0]["cases"]]
    for case_id in case_ids:
        lines.append(f"### Case: `{case_id}`\n")

        case_rows_per_model = {
            r["model"]: next((c for c in r["cases"] if c["case_id"] == case_id), None)
            for r in all_results
        }

        lines.append("| Metric | " + " | ".join(models) + " |")
        lines.append("| :--- | " + " | ".join(["---:"] * len(models)) + " |")

        case_metrics = [
            ("Pass", lambda c: "YES" if c["passed"] else "NO"),
            ("ROUGE-L", lambda c: f"{c['rouge_l']:.4f}"),
            ("Keyword Overlap", lambda c: f"{c['keyword_overlap']:.2f}"),
            ("Judge Score", lambda c: f"{c['judge_score']}/5 ({c['judge_verdict']})"),
            ("Hallucinations (Lexical + Semantic)", lambda c: str(len(c.get("all_hallucinations", c.get("hallucinations", []))))),
            ("Ollama RAM", lambda c: f"{c.get('ollama_ram_gb', 0.0):.2f} GB"),
            ("System Used RAM", lambda c: f"{c.get('system_used_ram_gb', 0.0):.2f} GB"),
            ("Input Tokens (Prompt)", lambda c: str(c["input_tokens"])),
            ("Output Tokens (Summary)", lambda c: str(c["output_tokens"])),
            ("TTFT (s)", lambda c: f"{c['ttft_seconds']:.2f}s"),
            ("Speed (tok/s)", lambda c: f"{c['tokens_per_second']:.1f}"),
            ("Total Latency (s)", lambda c: f"{c['latency_seconds']:.2f}s"),
            ("Word Count", lambda c: str(c["word_count"])),
        ]

        for label, extractor in case_metrics:
            vals = []
            for m in models:
                c = case_rows_per_model.get(m)
                vals.append(extractor(c) if c else "-")
            lines.append(f"| {label} | " + " | ".join(vals) + " |")

        # Generated summaries per model
        lines.append("\n**Generated Summaries:**\n")
        for m in models:
            c = case_rows_per_model.get(m)
            summary = c["summary"] if c else "_(error)_"
            judge_reasoning = c["judge_reasoning"] if c else ""
            lines.append(f"**`{m}`**")
            lines.append(f"> {summary}\n")
            if judge_reasoning:
                lines.append(f"*Judge: {judge_reasoning}*\n")

    # ── Raw JSON appendix ───────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## Raw JSON Results\n")
    lines.append("```json")
    lines.append(json.dumps(all_results, indent=2, default=str))
    lines.append("```\n")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


# ─────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]LLM Summarization Model Comparator[/bold cyan]\n"
            "[dim]Evaluate multiple Ollama models on summarization quality[/dim]",
            border_style="cyan",
        )
    )

    # ── Load config + dataset ────────────────────────────────────────────────
    config = load_config()
    dataset = load_golden_dataset(config)
    ollama_url = config["ollama"]["url"].rstrip("/")

    # ── Model selection ──────────────────────────────────────────────────────
    console.print("\n[bold]Step 1:[/bold] Querying Ollama for available models...")
    available_models = get_ollama_models(ollama_url)
    if not available_models:
        console.print("[red]ERROR:[/red] No models found in Ollama. Pull a model first with `ollama pull <model>`.")
        sys.exit(1)
    selected_models = select_models_interactively(available_models)

    # ── Gemini judge setup ───────────────────────────────────────────────────
    console.print("\n[bold]Step 2:[/bold] Initializing Gemini judge...")
    gemini_client = build_gemini_client()
    console.print(f"  [green]OK[/green] Judge ready: [cyan]{config['judge']['model']}[/cyan]")

    # ── Sequential model evaluation ──────────────────────────────────────────
    console.print(f"\n[bold]Step 3:[/bold] Running evaluation across {len(selected_models)} model(s)...\n")
    all_results: list[dict[str, Any]] = []

    for model in selected_models:
        result = evaluate_model(model, dataset, config, gemini_client)
        all_results.append(result)

        # Unload model from VRAM after evaluation to free memory
        console.print(f"\n  [dim]Unloading [cyan]{model}[/cyan] from memory...[/dim]")
        unload_model_from_ollama(model, ollama_url)

    # ── Terminal comparison table ─────────────────────────────────────────────
    console.print("\n[bold]Step 4:[/bold] Results summary\n")
    print_comparison_table(all_results)

    # ── Markdown report ───────────────────────────────────────────────────────
    console.print("[bold]Step 5:[/bold] Saving reports...")
    report_path = save_markdown_report(all_results, config)
    console.print(f"  [green]OK[/green] Markdown report: [link file://{report_path}]{report_path}[/link file://{report_path}]")

    # ── HTML interactive dashboard ────────────────────────────────────────────
    html_path = save_html_dashboard(all_results, config)
    console.print(f"  [green]OK[/green] HTML dashboard: [link file://{html_path}]{html_path}[/link file://{html_path}]")

    console.print("\n[bold green]Evaluation complete![/bold green]\n")


if __name__ == "__main__":
    main()
