"""
Unit tests for CGAP Planner module: capability compilation, symbolic planning,
and deterministic grounding verification.
"""

from cgap_planner import (
    StoryFactPredicate,
    build_cgap_script_plan,
    compile_story_predicates,
    format_cgap_feedback_hint,
    verify_cgap_grounding,
)
from story import Story


# [verifies: CGAP-001/AC-CGAP-001.1]
def test_compile_story_predicates_extracts_metrics_and_entities():
    stories = [
        Story(
            source="ArXiv cs.AI",
            title="Capability-Grounded Agentic Planning with PDDL",
            link="https://arxiv.org/abs/2610.41040",
            summary="Researchers introduce CGAP achieving 88.5% success on ToolSandbox benchmark with 4B models.",
            validated_summary="Researchers introduce CGAP achieving 88.5% success on ToolSandbox benchmark with 4B models.",
            extra_metadata={"direct_quotes": ["achieving 88.5% success on ToolSandbox benchmark"]},
            is_update=True,
        ),
        Story(
            source="Hacker News",
            title="vLLM 0.7 Released with Metal Support",
            link="https://example.com/vllm",
            summary="The vLLM team released version 0.7 adding Apple Silicon Metal acceleration and 3x throughput.",
            validated_summary="The vLLM team released version 0.7 adding Apple Silicon Metal acceleration and 3x throughput.",
        ),
    ]

    predicates = compile_story_predicates(stories)
    assert len(predicates) == 2

    # Check Story #1
    p1 = predicates[0]
    assert p1.story_id == 1
    assert p1.title == "Capability-Grounded Agentic Planning with PDDL"
    assert p1.is_followup is True
    assert "88.5%" in p1.metrics or "88.5" in p1.metrics
    assert "cgap" in p1.key_entities or "toolsandbox" in p1.key_entities
    assert len(p1.direct_quotes) == 1

    # Check Story #2
    p2 = predicates[1]
    assert p2.story_id == 2
    assert p2.is_followup is False
    assert "0.7" in p2.metrics


# [verifies: CGAP-001/AC-CGAP-001.2]
def test_compile_story_predicates_incorporates_article_context():
    stories = [
        Story(
            source="AWS Blog",
            title="SageMaker SeqKD Architecture",
            link="https://aws.amazon.com/sagemaker",
            summary="SageMaker AI introduces sequence-level knowledge distillation with 45 percent lower cost on Llama-3.",
            validated_summary="SageMaker AI introduces sequence-level knowledge distillation.",
        )
    ]
    predicates = compile_story_predicates(stories)
    assert len(predicates) == 1
    assert "45" in predicates[0].metrics
    assert "sequence-level knowledge distillation" in predicates[0].source_context


# [verifies: CGAP-002/AC-CGAP-002.1]
def test_build_cgap_script_plan_formats_steps():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Story Alpha",
            source="Feed A",
            summary="Summary of Alpha with 42% gain.",
            metrics={"42%"},
            key_entities={"alpha"},
            is_followup=False,
        ),
        StoryFactPredicate(
            story_id=2,
            title="Story Beta",
            source="Feed B",
            summary="Summary of Beta with 99% accuracy.",
            metrics={"99%"},
            key_entities={"beta"},
            is_followup=True,
        ),
    ]

    plan = build_cgap_script_plan(predicates, "Innovation Scout")
    assert "=== CGAP SYMBOLIC MONOLOGUE PLAN (Innovation Scout) ===" in plan
    assert "Step 0: [Theme Opening]" in plan
    assert "Step 1: [CoverStory #1] 'Story Alpha'" in plan
    assert "Step 2: [CoverStory #2] [Follow-up Update] 'Story Beta'" in plan
    assert "Step 3: [SignOff]" in plan


# [verifies: CGAP-002/AC-CGAP-002.2]
def test_build_cgap_script_plan_guarantees_all_verified_stories_included():
    predicates = [
        StoryFactPredicate(
            story_id=i,
            title=f"Verified Story {i}",
            source=f"Feed {i}",
            summary=f"Summary {i} with {i * 10}% improvement.",
            metrics={f"{i * 10}%"},
            key_entities={f"entity{i}"},
        )
        for i in range(1, 5)
    ]
    plan = build_cgap_script_plan(predicates, "Practitioner's Radar")
    for i in range(1, 5):
        assert f"[CoverStory #{i}] 'Verified Story {i}'" in plan
        assert f"Allowed Metrics: {i * 10}%" in plan


# [verifies: CGAP-004/AC-CGAP-004.1]
def test_verify_cgap_grounding_passes_valid_ordered_script():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Capability-Grounded Agentic Planning",
            source="ArXiv",
            summary="Researchers introduced CGAP combining PDDL with language models.",
            metrics=set(),
            key_entities={"cgap", "pddl"},
        ),
        StoryFactPredicate(
            story_id=2,
            title="vLLM Inference Acceleration",
            source="GitHub",
            summary="vLLM released version 0.7 with 3x throughput improvements on Metal.",
            metrics={"0.7", "3x", "3"},
            key_entities={"vllm", "metal"},
        ),
    ]

    script = (
        "Today in Innovation Scout: first up, researchers introduced Capability-Grounded Agentic Planning, "
        "combining PDDL with language models. "
        "Next, the team announced vLLM Inference Acceleration, deploying version 0.7 with 3x throughput "
        "improvements on Metal. That is your briefing for today."
    )

    result = verify_cgap_grounding(script, predicates)
    assert result.passed is True
    assert len(result.violations) == 0
    assert result.covered_story_ids == [1, 2]
    assert result.is_ordered is True


# [verifies: CGAP-004/AC-CGAP-004.1]
def test_verify_cgap_grounding_detects_missing_story():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Alpha Grounding System",
            source="ArXiv",
            summary="Summary Alpha.",
        ),
        StoryFactPredicate(
            story_id=2,
            title="Beta Quantum Modeling",
            source="Nature",
            summary="Summary Beta.",
        ),
    ]

    # Script omits Beta Quantum Modeling
    script = (
        "Today in Innovation Scout: first up, researchers deployed Alpha Grounding System. "
        "That is your briefing for today."
    )

    result = verify_cgap_grounding(script, predicates)
    assert result.passed is False
    assert 2 in result.missing_story_ids
    assert any("Beta Quantum Modeling" in v for v in result.violations)


# [verifies: CGAP-004/AC-CGAP-004.1]
def test_verify_cgap_grounding_detects_out_of_order_narration():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Alpha Grounding System",
            source="ArXiv",
            summary="Summary Alpha.",
        ),
        StoryFactPredicate(
            story_id=2,
            title="Beta Quantum Modeling",
            source="Nature",
            summary="Summary Beta.",
        ),
    ]

    # Script talks about Beta first, then Alpha
    script = (
        "Today in Innovation Scout: first up, Beta Quantum Modeling achieves new state results. "
        "Afterwards, Alpha Grounding System was introduced. That is your briefing for today."
    )

    result = verify_cgap_grounding(script, predicates)
    assert result.passed is False
    assert result.is_ordered is False
    assert any("Narrative ordering violation" in v for v in result.violations)


# [verifies: CGAP-004/AC-CGAP-004.2]
def test_verify_cgap_grounding_detects_fabricated_metrics():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Alpha Performance Optimization",
            source="Blog",
            summary="Alpha optimization achieved 15% latency reduction.",
            metrics={"15%", "15"},
        ),
    ]

    # Script hallucinates 99.4%
    script = (
        "Today in Innovation Scout: first up, Alpha Performance Optimization claimed an unverified 99.4% speedup. "
        "That is your briefing for today."
    )

    result = verify_cgap_grounding(script, predicates)
    assert result.passed is False
    assert any("99.4%" in v or "99.4" in v for v in result.violations)


# [verifies: CGAP-004/AC-CGAP-004.2]
def test_verify_cgap_grounding_detects_theatrical_flattery():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Alpha Performance Optimization",
            source="Blog",
            summary="Alpha optimization achieved 15% latency reduction.",
            metrics={"15%", "15"},
        ),
    ]

    # Script contains forbidden theatrical fluff
    script = (
        "Welcome back. Today our journey through the realms of AI begins with Alpha Performance Optimization. "
        "Thank you for joining us on this intellectual voyage. That is your briefing for today."
    )

    result = verify_cgap_grounding(script, predicates)
    assert result.passed is False
    assert any("theatrical filler" in v for v in result.violations)


# [verifies: CGAP-004/AC-CGAP-004.1]
def test_format_cgap_feedback_hint():
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="First Story",
            source="Blog",
            summary="Summary one.",
        ),
        StoryFactPredicate(
            story_id=2,
            title="Second Story",
            source="Blog",
            summary="Summary two.",
        ),
    ]
    script = "Here is an incomplete script with only First Story."
    res = verify_cgap_grounding(script, predicates)
    hint = format_cgap_feedback_hint(res)
    assert "Include missing stories: [2]" in hint


# [verifies: CGAP-003/AC-CGAP-003.1]
def test_build_cgap_script_plan_dual_grounding_formats_context():
    """Verify Dual-Grounding formats both Core Takeaway and Article Context in plan."""
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="SageMaker Knowledge Distillation",
            source="AWS Blog",
            summary="Sequence-level distillation transfers teacher behavior to low-cost student.",
            source_context="Frontier models running multi-step agent tool loops are expensive at scale. SageMaker AI introduces SeqKD.",
            metrics={"SeqKD"},
            key_entities={"sagemaker", "aws"},
        ),
    ]

    plan = build_cgap_script_plan(predicates, "Practitioner's Radar")
    assert "Core Takeaway: Sequence-level distillation transfers teacher behavior" in plan
    assert "Article Context: Frontier models running multi-step agent tool loops are expensive at scale." in plan


# [verifies: CGAP-003/AC-CGAP-003.2]
def test_build_cgap_script_plan_dual_grounding_preserves_unverified_notice():
    """Verify Dual-Grounding directs presenter to preserve core facts and guard unverified stories."""
    predicates = [
        StoryFactPredicate(
            story_id=1,
            title="Failed Story Example",
            source="Test Feed",
            summary="⚠️ Failed to generate a reliable summary. Read the original article.",
            source_context="Raw unparsed content here.",
        ),
    ]

    plan = build_cgap_script_plan(predicates, "Practitioner's Radar")
    assert "Notice: Summary unverified. Briefly state the title and headline only" in plan
