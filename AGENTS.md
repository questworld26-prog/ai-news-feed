# Workspace Rules — AI News Voice Feed

This repository builds a 100% local, automated daily AI news voice briefing pipeline with strict anti-hallucination guardrails and zero paid API footprint.

---

## 1. Environment & Tooling Standards

- **Package & Environment Management**:
  - Exclusively use `uv` for all environment actions, dependencies, and script invocations.
  - Run commands via `uv run` (e.g. `uv run pytest`, `uv run ruff check`, `uv run python src/generate_news_digest.py`).
  - Do **NOT** invoke `pip`, `pip3`, `virtualenv`, or `python -m venv` directly.
- **Linting & Formatting**:
  - Target Python version: `3.11+` (configured in `pyproject.toml`).
  - Linter: `uv run ruff check .`
  - Formatter: `uv run ruff format .`
  - Line length limit: 120 characters.
- **Testing**:
  - Run the test suite: `uv run pytest`
  - Unit tests live under `tests/`. Always ensure regression tests pass after altering pipeline stages.

---

## 2. Hardware Constraints & Operational Budget (Apple Silicon M1 8GB)

- **Target Machine**: Apple M1 with 8 GB unified memory.
- **Ollama Invariant**:
  - Keep model footprints bounded (`phi4-mini:3.8b` ~2.5 GB, `qwen2.5:3b` ~1.9 GB).
  - Never attempt to run concurrent heavy model loads. Enforce serial model usage or maximum 1 active model in VRAM where possible.
  - Do not introduce large models (>4B parameters) or heavy background indexing jobs.
- **TTS Synthesis Headroom**:
  - Audio synthesis uses `kokoro-mlx` on Apple Silicon Metal. Ensure memory is freed before invoking multi-chunk TTS synthesis to avoid OOM or swap thrashing.

---

## 3. Architectural Invariants (Hierarchy of Truth & ADRs)

All agent code contributions must adhere to the decisions recorded in `ADR.md` and `docs/`:

1. **Hierarchy of Truth (Strict Factuality)**:
   - Level 1: Ground truth RSS source text / article excerpts.
   - Level 2: Per-story bullet summaries (must be verified directly against source text).
   - Level 3: Script monologue (must be verified against approved summaries, never hallucinating new claims).
2. **Immediate Per-Item Validation (ADR-02)**:
   - Never rely on post-hoc batch digest validation. Summaries and script segments are validated immediately per-item with automatic retry/correction loops before progressing.
3. **Zero Paid API Invariant (ADR-04)**:
   - The production pipeline must run 100% locally with zero paid cloud API dependencies (Ollama + kokoro-mlx + LAYA entailment). Cloud APIs (e.g. Gemini via `google-genai`) are strictly restricted to offline dev evals and golden benchmark judging.
4. **Deterministic Orchestration**:
   - Keep control flow in plain Python. Small local models (3–4B) must have bounded agency with hard tool budgets; safety gates and verification loops must never depend on an LLM's non-deterministic discretion.

---

## 4. Change Protocol & Definition of Done

- **Plan First**: For changes modifying more than 2 files or changing pipeline interfaces, present a structured plan before making edits.
- **Automated Verification**: Before marking any task complete:
  1. `uv run ruff check .`
  2. `uv run pytest tests/` (or the relevant sub-suite for targeted changes).
- **Preserve Documentation**: Keep all existing docstrings, test fixtures, and architectural decision records up to date.

---

## 5. Documentation & Release Governance Standards

- **ADR Maintenance**:
  - `ADR.md` must be maintained with an up-to-date Table of Contents at the top.
  - When an architectural decision or pipeline boundary changes, record the new ADR and update the TOC.
- **Semantic Versioning & `RELEASE.md`**:
  - Adhere strictly to SemVer (`MAJOR.MINOR.PATCH`).
  - Maintain concise, user-facing release notes in `RELEASE.md`.
  - **MANDATORY HUMAN GATE**: Always explicitly ask the user for approval before proposing, generating, or bumping `MAJOR` or `MINOR` versions. Never increment them autonomously.
- **`README.md` Operational Parity**:
  - Keep `README.md` continuously synchronized with how to run the pipeline (flags, options) and how to run tests.

