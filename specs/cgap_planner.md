# Capability-Grounded Agentic Planning Specifications (`CGAP`)

Formal specifications defining atomic predicate compilation, symbolic execution plans, Dual-Grounding prompt synthesis, and deterministic pre-gating.

---

## CGAP-001: Atomic Capability Predicate Compilation

The system shall deterministically compile each verified story into an atomic StoryFactPredicate capturing allowed key entities, metrics, extractive quotes, and Core Takeaways.

Acceptance Criteria:
- AC-CGAP-001.1: Extracts numerical metrics and capitalized entities from verified summaries into the story predicate catalog.
- AC-CGAP-001.2: Incorporates clean Level 1 article body excerpts into allowed predicate vocabulary for Dual-Grounding.

---

## CGAP-002: Symbolic Monologue Execution Planning

When preparing spoken monologue synthesis, the system shall compile an explicit, step-by-step symbolic plan mapping introduction, story coverage, and sign-off in strict sequential order.

Acceptance Criteria:
- AC-CGAP-002.1: Generates monotonic step identifiers Step 0 through Step N strictly preserving chronological story sequence.
- AC-CGAP-002.2: Guarantees 100% inclusion of all verified stories in the symbolic execution plan without omissions.

---

## CGAP-003: Dual-Grounding Monologue Architecture

The system shall structure the presenter prompt using Dual-Grounding, binding Level 2 Core Takeaways as immutable factual anchors and Level 1 Article Context as conversational canvas.

Acceptance Criteria:
- AC-CGAP-003.1: Formats each story block with Core Takeaway anchor and Article Context canvas in the presenter LLM prompt.
- AC-CGAP-003.2: Directs the presenter model to preserve Core Takeaways without contradiction while using Article Context for technical depth.

---

## CGAP-004: Deterministic Grounding Pre-Gate

Before executing audio synthesis or neural fact audits, the system shall execute deterministic pre-gate verification of coverage, ordering, entities, and metrics in under 2ms on CPU.

Acceptance Criteria:
- AC-CGAP-004.1: Deterministically verifies 100% story coverage and strictly monotonic sequential order in the candidate monologue.
- AC-CGAP-004.2: Flags any metric or named entity in a script segment that is absent from the story's predicate catalog.
