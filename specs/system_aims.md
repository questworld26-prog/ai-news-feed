# System Mission & Architectural Invariants (`AIM`)

Formal specifications defining the overall mission, hardware budget, and non-negotiable architectural invariants of the AI News Voice Feed pipeline.

---

## AIM-001: 100% Local Execution with Zero Paid API Footprint

The system shall execute the entire daily production news briefing pipeline locally on Apple Silicon Metal with zero paid cloud API dependencies.

Acceptance Criteria:
- AC-AIM-001.1: Production inference executes exclusively via local Ollama SLMs and local PyTorch LAYA models without paid API keys.
- AC-AIM-001.2: Cloud LLM provider SDKs (such as google-genai) are strictly quarantined to offline benchmark evaluation and golden judging.

---

## AIM-002: Hierarchy of Truth Anti-Hallucination Invariant

The system shall enforce a strict three-tier Hierarchy of Truth where Level 2 summaries derive exclusively from Level 1 source text, and Level 3 spoken monologues derive exclusively from Level 2 validated facts.

Acceptance Criteria:
- AC-AIM-002.1: Level 2 story summary claims must be fully grounded in and entailed by extracted verbatim source quotes.
- AC-AIM-002.2: Level 3 spoken monologue segments cannot introduce outside entities, facts, or numerical metrics not present in validated Level 2 predicates.

---

## AIM-003: Operational Memory Headroom on 8GB Apple Silicon

While executing on 8GB unified memory hardware, the system shall manage memory headroom by enforcing serial model execution and purging PyTorch CPU tensors and Ollama VRAM prior to multi-chunk Metal TTS synthesis.

Acceptance Criteria:
- AC-AIM-003.1: The system enforces serial execution preventing concurrent heavy model loads in memory.
- AC-AIM-003.2: Reclaims memory via unload_laya_engine before initiating multi-chunk Kokoro-mlx TTS voice synthesis.

---

## AIM-004: Automated Multi-Modal Daily Telegram Delivery

When daily execution finishes, the system shall format a standardized Markdown digest and synthesize a natural 24kHz WAV podcast voice note, dispatching both to configured Telegram channels.

Acceptance Criteria:
- AC-AIM-004.1: Assembles briefing markdown conforming to the BriefingOutput schema with metadata and story links.
- AC-AIM-004.2: Dispatches synthesized WAV audio notes and formatted markdown to Telegram Bot API with automatic 45MB chunking.

