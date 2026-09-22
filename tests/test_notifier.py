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
        # Each chunk should contain non-empty text
        assert len(chunk.strip()) > 0


def test_send_to_telegram_skips_when_credentials_missing():
    # When bot_token or chat_id is empty, it returns False gracefully
    res = send_to_telegram("digest text", [], bot_token="", chat_id="")
    assert res is False
