"""
Unit tests for notifier audio sanitization, text chunking, and dispatch handling.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from briefing_generator import clean_script_for_audio
from notifier import chunk_text, send_to_telegram


# [verifies: AUDIO-003/AC-AUDIO-003.1]
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


# [verifies: AUDIO-003/AC-AUDIO-003.2]
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


# [verifies: AUDIO-004/AC-AUDIO-004.1]
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
        assert 1 <= len(words) <= 10


# [verifies: AIM-004/AC-AIM-004.2]
def test_send_to_telegram_skips_when_credentials_missing():
    # When bot_token or chat_id is empty, it returns False gracefully
    res = send_to_telegram("digest text", [], bot_token="", chat_id="")
    assert res is False


# [verifies: AIM-004/AC-AIM-004.1]
def test_send_to_telegram_delivers_text_and_audio(monkeypatch, tmp_path):
    """Verify successful dispatch of formatted text and audio files to Telegram."""
    audio_file = tmp_path / "briefing.wav"
    audio_file.write_bytes(b"RIFF" + b"\x00" * 50)

    posted_urls = []

    class MockResp:
        ok = True

        def raise_for_status(self):
            pass

    def mock_post(url, *args, **kwargs):
        posted_urls.append(url)
        return MockResp()

    import requests

    monkeypatch.setattr(requests, "post", mock_post)

    success = send_to_telegram(
        text_digest="Today's top AI headlines",
        audio_files=[audio_file],
        bot_token="test_bot_token",
        chat_id="test_chat_id",
    )
    assert success is True
    assert len(posted_urls) == 2
    assert any("/sendMessage" in u for u in posted_urls)
    assert any("/sendAudio" in u for u in posted_urls)
