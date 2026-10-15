"""
Unit tests for Briefing Generator safety invariants, ADR-02 retry loop,
Hierarchy of Truth (Level 3 script validation), and TTS memory management.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from briefing_generator import (
    STORY_FALLBACK_SUMMARY,
    StorySummaryResponse,
    generate_story_summary_validated,
    validate_and_correct_audio_script,
)
from model_provider import ModelProviderFactory
from story import Story
from validator import FactCheckResponse


@pytest.fixture
def sample_theme() -> dict[str, str]:
    return {
        "name": "Practitioner's Radar",
        "description": "Production systems, MLOps, and architecture",
        "tone": "collegial, sharp, highly technical",
    }


@pytest.fixture
def sample_story() -> Story:
    return Story(
        source="ArXiv cs.AI",
        title="vLLM 0.7.0 Chunked Prefill Architecture",
        link="https://github.com/vllm-project/vllm",
        summary="vLLM 0.7.0 introduces chunked prefill by default, reducing TTFT by 3x on Llama 3 70B workloads.",
    )


@pytest.fixture
def test_config() -> dict:
    return {
        "llm": {"model": "phi4-mini:3.8b", "ollama_url": "http://localhost:11434"},
        "laya": {"enabled": False},  # Decoupled for fast-path unit testing
    }


def test_generate_story_summary_validated_success_first_attempt(sample_story, sample_theme, test_config, monkeypatch):
    """ADR-02: Validated summary passes on attempt 1 with grounded quotes."""
    mock_summary = StorySummaryResponse(
        direct_quotes=["vLLM 0.7.0 introduces chunked prefill by default, reducing TTFT by 3x on Llama 3 70B"],
        summary="vLLM 0.7.0 enables chunked prefill by default. This reduces TTFT by 3x on Llama 3 70B.",
    )

    class MockProvider:
        def generate_structured(self, **kwargs):
            schema = kwargs.get("schema")
            if schema == StorySummaryResponse:
                return mock_summary
            elif schema == FactCheckResponse:
                return FactCheckResponse(passed=True, reasoning="Grounded in source.")
            return None

    monkeypatch.setattr(ModelProviderFactory, "get_provider", lambda cfg: MockProvider())

    summary = generate_story_summary_validated(sample_story, sample_theme, test_config)
    assert summary == mock_summary.summary
    assert sample_story.validated_summary == mock_summary.summary
    assert sample_story.extra_metadata["summary_status"] == "success"
    assert sample_story.extra_metadata["retry_count"] == 1
    assert sample_story.extra_metadata["keyword_overlap"] > 0.40


def test_generate_story_summary_validated_retries_with_hint_then_passes(
    sample_story, sample_theme, test_config, monkeypatch
):
    """ADR-02: If attempt 1 fails fact-check, attempt 2 injects correction hint and succeeds."""
    prompts_received = []

    hallucinated_resp = StorySummaryResponse(
        direct_quotes=["vLLM 0.7.0 introduces chunked prefill"],
        summary="vLLM 0.7.0 partnered with OpenAI on a $100 billion quantum supercomputer cluster.",
    )
    grounded_resp = StorySummaryResponse(
        direct_quotes=["vLLM 0.7.0 introduces chunked prefill by default, reducing TTFT by 3x on Llama 3 70B"],
        summary="vLLM 0.7.0 enables chunked prefill by default. It cuts TTFT by 3x on Llama 3 70B workloads.",
    )

    summary_calls = 0

    class MockProvider:
        def generate_structured(self, **kwargs):
            nonlocal summary_calls
            schema = kwargs.get("schema")
            if schema == StorySummaryResponse:
                summary_calls += 1
                prompts_received.append(kwargs.get("prompt", ""))
                if summary_calls == 1:
                    return hallucinated_resp
                return grounded_resp
            elif schema == FactCheckResponse:
                return FactCheckResponse(passed=True, reasoning="Factual")
            return None

    monkeypatch.setattr(ModelProviderFactory, "get_provider", lambda cfg: MockProvider())

    summary = generate_story_summary_validated(sample_story, sample_theme, test_config)
    assert summary == grounded_resp.summary
    assert summary_calls == 2
    assert sample_story.extra_metadata["retry_count"] == 2
    assert sample_story.extra_metadata["summary_status"] == "success"

    # Assert that attempt 2 received correction feedback in prompt
    assert "CORRECTION REQUIRED FOR PREVIOUS ATTEMPT" in prompts_received[1]


def test_generate_story_summary_validated_fails_closed_to_fallback(
    sample_story, sample_theme, test_config, monkeypatch
):
    """ADR-02 Fail-Closed: After 3 failed attempts, safely replaces summary with STORY_FALLBACK_SUMMARY."""
    hallucinated_resp = StorySummaryResponse(
        direct_quotes=["vLLM 0.7.0 introduces chunked prefill"],
        summary="vLLM 0.7.0 partnered with OpenAI on a $100 billion quantum supercomputer cluster.",
    )

    class MockProvider:
        def generate_structured(self, **kwargs):
            schema = kwargs.get("schema")
            if schema == StorySummaryResponse:
                return hallucinated_resp
            elif schema == FactCheckResponse:
                return FactCheckResponse(passed=False, reasoning="Unanchored entity")
            return None

    monkeypatch.setattr(ModelProviderFactory, "get_provider", lambda cfg: MockProvider())

    summary = generate_story_summary_validated(sample_story, sample_theme, test_config)
    assert summary == STORY_FALLBACK_SUMMARY
    assert sample_story.validated_summary == STORY_FALLBACK_SUMMARY
    assert sample_story.extra_metadata["summary_status"] == "failed"
    assert sample_story.extra_metadata["retry_count"] == 3
    assert sample_story.extra_metadata["keyword_overlap"] == 0.0


def test_validate_and_correct_audio_script_hierarchy_of_truth_pass(sample_story, test_config, monkeypatch):
    """Hierarchy of Truth (Level 3 vs Level 2): Audio script matches verified summary."""
    sample_story.validated_summary = "vLLM 0.7.0 adds chunked prefill, improving TTFT by 3x."
    script = "Welcome to the briefing. Today, vLLM 0.7.0 adds chunked prefill, improving TTFT by 3x on Llama 3 70B."

    class MockProvider:
        def generate_structured(self, **kwargs):
            return FactCheckResponse(passed=True, reasoning="Script is grounded in verified story summary.")

    monkeypatch.setattr(ModelProviderFactory, "get_provider", lambda cfg: MockProvider())

    passed, reasoning = validate_and_correct_audio_script([sample_story], script, test_config)
    assert passed is True
    assert "grounded" in reasoning.lower()


def test_validate_and_correct_audio_script_hierarchy_of_truth_detects_unsupported_monologue(
    sample_story, test_config, monkeypatch
):
    """Hierarchy of Truth: Rejects script monologue that hallucinates claims not in Level 2 summaries."""
    sample_story.validated_summary = "vLLM 0.7.0 adds chunked prefill, improving TTFT by 3x."
    hallucinated_script = "Welcome back. In breaking news, OpenAI acquired Google for 2 trillion dollars."

    class MockProvider:
        def generate_structured(self, **kwargs):
            return FactCheckResponse(
                passed=False, reasoning="Script claims OpenAI acquired Google, which is absent from verified summaries."
            )

    monkeypatch.setattr(ModelProviderFactory, "get_provider", lambda cfg: MockProvider())

    passed, reasoning = validate_and_correct_audio_script([sample_story], hallucinated_script, test_config)
    assert passed is False
    assert "OpenAI acquired Google" in reasoning or "absent" in reasoning


def test_synthesize_audio_memory_headroom_lifecycle(tmp_path, test_config, monkeypatch):
    """M1 8GB Hardware Invariant: synthesize_audio unloads LLMs and clears Metal cache."""
    from notifier import synthesize_audio

    unload_mock = MagicMock()
    clear_mlx_mock = MagicMock()
    monkeypatch.setattr("notifier.unload_ollama_models", unload_mock)
    monkeypatch.setattr("notifier.clear_mlx_memory", clear_mlx_mock)

    # Mock KokoroTTS generate output
    class MockAudioResult:
        audio = [0.0] * 2400

    class MockKokoroTTS:
        @classmethod
        def from_pretrained(cls):
            return cls()

        def generate(self, text, voice, speed, sample_rate):
            return MockAudioResult()

    import kokoro_mlx

    monkeypatch.setattr(kokoro_mlx, "KokoroTTS", MockKokoroTTS)

    import soundfile as sf

    write_called = False

    def mock_write(path, data, samplerate, subtype=None):
        nonlocal write_called
        write_called = True
        Path(path).write_bytes(b"RIFF" + b"\x00" * 100)

    monkeypatch.setattr(sf, "write", mock_write)

    script = "This is a short test script for audio synthesis lifecycle verification."
    output_files = synthesize_audio(
        script=script,
        output_dir=tmp_path,
        config=test_config,
        date_str="2026-10-15",
    )

    # Assert unload_ollama_models was invoked before TTS initialization
    assert unload_mock.call_count >= 1
    # Assert Metal memory cleanup was called
    assert clear_mlx_mock.call_count >= 2
    # Assert output files were generated
    assert len(output_files) == 1
    assert write_called is True
