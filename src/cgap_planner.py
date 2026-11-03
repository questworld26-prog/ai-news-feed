"""
Capability-Grounded Agentic Planning (CGAP) Module.
Implements the CGAP paradigm (Shrestha et al., 2026, WashU - arXiv:2610.41040)
for Level 3 spoken podcast monologue generation:
1. Deterministic compilation of validated Level 2 stories into atomic ground predicates.
2. Abstract symbolic execution plan generation (Theme Opening -> Story Coverage Sequence -> Sign-off).
3. Deterministic verification gate checking plan coverage, narrative ordering, and predicate grounding.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from story import Story
from validator import extract_key_tokens

logger = logging.getLogger("ai_briefing")

# Common spoken presentation words and theme identifiers that legitimately appear in spoken scripts
AUDIO_BENIGN_ENTITIES = {
    "welcome",
    "today",
    "yesterday",
    "tomorrow",
    "briefing",
    "story",
    "stories",
    "update",
    "updates",
    "coverage",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "next",
    "finally",
    "meanwhile",
    "here",
    "team",
    "researchers",
    "engineers",
    "that",
    "this",
    "from",
    "innovation",
    "scout",
    "radar",
    "lens",
    "digest",
    "builder",
    "practitioner",
    "executive",
    "daily",
    "ai",
    "metal",
    "news",
}


@dataclass
class StoryFactPredicate:
    """Atomic factual capability contract for a validated story."""

    story_id: int
    title: str
    source: str
    summary: str
    source_context: str = ""
    direct_quotes: list[str] = field(default_factory=list)
    key_entities: set[str] = field(default_factory=set)
    metrics: set[str] = field(default_factory=set)
    is_followup: bool = False

    def to_pddl_representation(self) -> str:
        """Render predicate in a structured, readable capability format."""
        entities_str = ", ".join(sorted(self.key_entities)[:8]) if self.key_entities else "None"
        metrics_str = ", ".join(sorted(self.metrics)) if self.metrics else "None"
        followup_str = " (UPDATE / Follow-up)" if self.is_followup else ""
        return (
            f"Story #{self.story_id}{followup_str}: '{self.title}' [Source: {self.source}]\n"
            f"  - Ground Facts: {self.summary}\n"
            f"  - Permitted Entities: {entities_str}\n"
            f"  - Permitted Metrics: {metrics_str}"
        )


@dataclass
class CGAPVerificationResult:
    """Verification results from deterministic CGAP grounding analysis."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    covered_story_ids: list[int] = field(default_factory=list)
    missing_story_ids: list[int] = field(default_factory=list)
    is_ordered: bool = True


# [spec: CGAP-001]
def compile_story_predicates(stories: list[Story | dict[str, Any]]) -> list[StoryFactPredicate]:
    """
    Deterministically compile Level 2 validated stories into atomic ground predicates.
    Extracts permitted entities, numbers, and verbatim quotes.
    """
    predicates: list[StoryFactPredicate] = []

    for idx, item in enumerate(stories, 1):
        s_obj = item if isinstance(item, Story) else Story.from_dict(item)

        validated_text = s_obj.validated_summary or s_obj.summary or ""
        source_text = s_obj.summary or ""
        # Combine title, validated summary, source text, and source attribution for grounding scope
        full_text = f"{s_obj.title} {validated_text} {source_text} {s_obj.source}"

        # Extract metrics (numbers, floats, percentages, versions)
        raw_metrics = set(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", full_text))
        # Filter standard low-value standalone ordinals
        metrics = {m for m in raw_metrics if m not in {"1", "2", "3", "4", "5"}}

        # Extract entities / proper nouns / model identifiers
        entities = extract_key_tokens(full_text)

        # Retrieve extractive direct quotes if recorded during summary generation
        quotes = s_obj.extra_metadata.get("direct_quotes", [])
        if not isinstance(quotes, list):
            quotes = []

        predicate = StoryFactPredicate(
            story_id=idx,
            title=s_obj.title,
            source=s_obj.source,
            summary=validated_text,
            source_context=source_text,
            direct_quotes=quotes,
            key_entities=entities,
            metrics=metrics,
            is_followup=s_obj.is_update,
        )
        predicates.append(predicate)

    return predicates


# [spec: CGAP-002]
# [spec: CGAP-003]
# [spec: AIM-002]
def build_cgap_script_plan(predicates: list[StoryFactPredicate], theme_name: str) -> str:
    """
    Generate an abstract symbolic plan for monologue script synthesis based on CGAP and Dual-Grounding.
    Provides Level 2 Core Takeaways as anchors and Level 1 Article Context for natural depth.
    Forces the LLM to follow a strict sequential path through verified predicates.
    """
    plan_lines: list[str] = [
        f"=== CGAP SYMBOLIC MONOLOGUE PLAN ({theme_name}) ===",
        f"Goal: Deliver a concise, factual audio briefing covering all {len(predicates)} stories without ungrounded claims.",
        "Execution Steps:",
        f"  Step 0: [Theme Opening] Direct 1-sentence introduction stating theme '{theme_name}' and the first topic.",
    ]

    for p in predicates:
        status_note = " [Follow-up Update]" if p.is_followup else ""
        source_note = f" [Source: {p.source}]" if p.source else ""
        is_failed = p.summary.startswith("⚠️")

        step_lines = [f"  Step {p.story_id}: [CoverStory #{p.story_id}]{status_note} '{p.title}'{source_note}"]
        if is_failed:
            step_lines.append(
                "          Notice: Summary unverified. Briefly state the title and headline only; do not speculate."
            )
        else:
            step_lines.append(f"          Core Takeaway: {p.summary}")
            # Dual-Grounding: provide clean, capped article context if available
            clean_context = re.sub(r"\s+", " ", p.source_context).strip()
            if clean_context and clean_context != p.summary:
                if len(clean_context) > 300:
                    clean_context = clean_context[:300].rsplit(" ", 1)[0] + "..."
                step_lines.append(f"          Article Context: {clean_context}")

        if p.metrics:
            step_lines.append(f"          Allowed Metrics: {', '.join(sorted(p.metrics))}")

        plan_lines.append("\n".join(step_lines))

    plan_lines.extend(
        [
            f"  Step {len(predicates) + 1}: [SignOff] State exactly: 'That is your briefing for today.'",
            "",
            "Strict Dual-Grounding Invariants:",
            "- Every claim, entity, and metric in Step k MUST bind to Story #k's Core Takeaway and Article Context.",
            "- Use the Article Context to explain the engineering problem and mechanics naturally; do not simply re-read the Core Takeaway.",
            "- NEVER introduce external metrics, ungrounded companies, or speculative claims.",
        ]
    )

    return "\n".join(plan_lines)


def _find_story_mention_position(script_lower: str, predicate: StoryFactPredicate) -> int:
    """
    Find earliest character offset where this story is introduced in the script.
    Checks normalized title substrings and distinctive title keywords.
    """
    # 1. Check exact or normalized title substring
    norm_title = re.sub(r"[^\w\s]", " ", predicate.title.lower()).strip()
    title_words = [w for w in norm_title.split() if len(w) > 3]

    pos = script_lower.find(norm_title)
    if pos != -1:
        return pos

    # 2. Check title prefix (e.g. first 3-4 significant words)
    if len(title_words) >= 3:
        prefix = " ".join(title_words[:3])
        pos = script_lower.find(prefix)
        if pos != -1:
            return pos

    # 3. Check distinctive multi-token overlap
    if title_words:
        first_word_positions = [m.start() for m in re.finditer(re.escape(title_words[0]), script_lower)]
        for p in first_word_positions:
            window = script_lower[p : p + 250]
            matched_words = sum(1 for w in title_words if w in window)
            if matched_words / len(title_words) >= 0.5:
                return p

    return -1


# [spec: CGAP-004]
def verify_cgap_grounding(
    script: str,
    predicates: list[StoryFactPredicate],
    config: dict[str, Any] | None = None,
) -> CGAPVerificationResult:
    """
    Deterministic verification checking:
    1. Plan Coverage: All planned stories are addressed in the script.
    2. Narrative Ordering: Stories are covered in the planned sequence.
    3. Metric Grounding: Numbers in the script are grounded in story predicates.
    4. Entity Grounding: Capitalized proper nouns in the script are grounded in source predicates.
    5. Clean Speech: Absence of theatrical flattery, boilerplate intros, and meta commentary.
    """
    if not script or not predicates:
        return CGAPVerificationResult(
            passed=False,
            violations=["Script or predicate catalog is empty."],
            missing_story_ids=[p.story_id for p in predicates],
        )

    violations: list[str] = []
    script_lower = script.lower()

    # 1. Check Story Plan Coverage and Sequential Ordering
    story_positions: list[tuple[int, int]] = []  # (story_id, char_position)
    missing_story_ids: list[int] = []

    for p in predicates:
        pos = _find_story_mention_position(script_lower, p)
        if pos == -1:
            missing_story_ids.append(p.story_id)
            violations.append(f"Story #{p.story_id} ('{p.title[:45]}...') is absent or missing from the spoken script.")
        else:
            story_positions.append((p.story_id, pos))

    covered_ids = [sp[0] for sp in story_positions]
    is_ordered = True

    # Check that positions are strictly monotonic increasing
    for i in range(len(story_positions) - 1):
        curr_id, curr_pos = story_positions[i]
        next_id, next_pos = story_positions[i + 1]
        if next_pos < curr_pos:
            is_ordered = False
            violations.append(
                f"Narrative ordering violation: Story #{next_id} appeared at offset {next_pos} before Story #{curr_id} at {curr_pos}."
            )

    # 2. Metric & Numerical Predicate Grounding
    all_permitted_metrics: set[str] = set()
    for p in predicates:
        all_permitted_metrics.update(p.metrics)
        all_permitted_metrics.update(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", p.summary))
        all_permitted_metrics.update(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", p.source_context))
        all_permitted_metrics.update(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", p.title))

    script_metrics = set(re.findall(r"\b\d+(?:\.\d+)+%?\b|\b\d+(?:\.\d+)?%?\b", script))
    for num in script_metrics:
        # Allow standard small ordinals, word counts, or story counts
        if num in {"1", "2", "3", "4", "5", str(len(predicates))}:
            continue
        if num not in all_permitted_metrics:
            violations.append(f"Ungrounded metric: Number '{num}' in script was not present in any story predicate.")

    # 3. Entity & Proper Noun Grounding
    all_source_text = "\n\n".join([f"{p.title}\n{p.summary}\n{p.source_context}\n{p.source}" for p in predicates])
    source_lower = all_source_text.lower()

    raw_entities = re.findall(
        r"\b[A-Z][a-zA-Z0-9]*(?:[&/'-][A-Z0-9][a-zA-Z0-9]*)*(?:\s+[A-Z0-9][a-zA-Z0-9]*(?:[&/'-][A-Z0-9][a-zA-Z0-9]*)*)*\b|\b[a-zA-Z]+\d+(?:-\w+)?\b",
        script,
    )

    seen_entities: set[str] = set()
    for ent in raw_entities:
        ent_clean = ent.strip()
        ent_lower = ent_clean.lower()
        if ent_lower in seen_entities:
            continue
        seen_entities.add(ent_lower)

        # Check if words in this entity are benign audio presentation or theme words
        words = [w.lower() for w in re.findall(r"\w+", ent_clean)]
        if words and all(w in AUDIO_BENIGN_ENTITIES for w in words):
            continue

        source_norm = re.sub(r"[-_]", " ", source_lower)
        ent_norm = re.sub(r"[-_]", " ", ent_lower)
        if ent_lower not in source_lower and ent_norm not in source_norm:
            violations.append(f"Ungrounded entity: Entity '{ent_clean}' is absent from verified story predicates.")

    # 4. Monologue Flattery / Preamble Check
    forbidden_phrases = [
        "intellectual voyage",
        "our journey through",
        "embark on this mission",
        "pushing the boundaries",
        "in conclusion",
        "thank you for joining",
        "until next time",
    ]
    for phrase in forbidden_phrases:
        if phrase in script_lower:
            violations.append(f"Forbidden theatrical filler detected: '{phrase}'.")

    passed = len(violations) == 0
    return CGAPVerificationResult(
        passed=passed,
        violations=violations,
        covered_story_ids=covered_ids,
        missing_story_ids=missing_story_ids,
        is_ordered=is_ordered,
    )


def format_cgap_feedback_hint(result: CGAPVerificationResult) -> str:
    """Format granular, actionable correction feedback for the LLM retry prompt."""
    if result.passed:
        return ""
    hints = []
    if result.missing_story_ids:
        hints.append(f"Include missing stories: {result.missing_story_ids}")
    if not result.is_ordered:
        hints.append("Follow the exact step-by-step narrative sequence: Story #1 then Story #2 up to the last story.")
    for v in result.violations:
        if v not in hints:
            hints.append(v)
    return "; ".join(hints[:4])
