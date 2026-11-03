"""
Unit tests for notifier audio sanitization, text chunking, and dispatch handling.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from briefing_generator import clean_script_for_audio
from notifier import chunk_text, send_to_telegram


def test_clean_script_for_audio_strips_urls_and_markdown():
    raw = (
        "# Story 1: [vLLM 0.7 Released](https://github.com/vllm-project/vllm)\n"
        "Check out Article URL: https://vllm.ai or www.vllm.ai for more details.\n"
        "The link to the original source is available at the website *bold* and _italic_."
    )
    cleaned = clean_script_for_audio(raw)
    assert "https://" not in cleaned
    assert "www." not in cleaned
    assert "Article URL" not in cleaned
    assert "*" not in cleaned
    assert "_" not in cleaned
    assert "vLLM 0.7 Released" in cleaned


def test_clean_script_for_audio_strips_preamble_and_outro_flattery():
    raw = (
        "Welcome back. Today we're looking through our Innovation Scout lens, diving into the latest unconventional and cross disciplinary AI breakthroughs. "
        "Our journey will take us through the realms of capability grounded planning and world modeling. "
        "Let's embark on this exploratory mission together. "
        "First up, researchers deployed a new model architecture. "
        "In conclusion, today's thematic journey through the Innovation Scout lens has taken us across diverse territories. "
        "Thank you for joining us on this intellectual voyage. Until next time, keep innovating and exploring the frontiers of technology."
    )
    cleaned = clean_script_for_audio(raw)
    assert "Welcome back" not in cleaned
    assert "Our journey will take us through the realms" not in cleaned
    assert "Let's embark on this exploratory mission" not in cleaned
    assert "In conclusion, today's thematic journey" not in cleaned
    assert "intellectual voyage" not in cleaned
    assert "First up, researchers deployed a new model architecture." in cleaned
    assert cleaned.endswith("That is your briefing for today.")


def test_clean_script_for_audio_empty_string():
    assert clean_script_for_audio("") == ""
    assert clean_script_for_audio(None) == ""


def test_chunk_text_respects_max_words():
    text = (
        "Sentence one is brief. Sentence two has a few more words in it. "
        "Sentence three continues the sequence. Sentence four finishes up the test text block."
    )
    chunks = chunk_text(text, max_words=10)
    assert len(chunks) >= 2
    for chunk in chunks:
        # High-fidelity anti-mirage assertion: assert length bound is strictly respected
        words = chunk.strip().split()
        assert len(words) > 0
        assert len(words) <= 10


def test_send_to_telegram_skips_when_credentials_missing():
    # When bot_token or chat_id is empty, it returns False gracefully
    res = send_to_telegram("digest text", [], bot_token="", chat_id="")
    assert res is False
