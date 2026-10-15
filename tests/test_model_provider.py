"""
Unit tests for ModelProvider and ModelProviderFactory.
"""

import sys
from pathlib import Path

from pydantic import BaseModel, Field

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from model_provider import ModelProviderFactory, OllamaProvider


class DummySchema(BaseModel):
    message: str = Field(description="A test message")
    score: int = Field(description="A test score")


def test_factory_returns_ollama_provider():
    ModelProviderFactory.reset()
    config = {
        "llm": {
            "ollama_url": "http://localhost:11434/",
            "model": "phi4-mini:3.8b",
        }
    }
    provider = ModelProviderFactory.get_provider(config)
    assert isinstance(provider, OllamaProvider)
    assert provider.base_url == "http://localhost:11434"
    assert provider.default_model == "phi4-mini:3.8b"


def test_factory_caches_singleton():
    ModelProviderFactory.reset()
    config = {
        "llm": {
            "ollama_url": "http://localhost:11434",
            "model": "phi4-mini:3.8b",
        }
    }
    provider1 = ModelProviderFactory.get_provider(config)
    provider2 = ModelProviderFactory.get_provider(config)
    assert provider1 is provider2


def test_factory_resets_on_url_change():
    ModelProviderFactory.reset()
    config1 = {"llm": {"ollama_url": "http://localhost:11434"}}
    config2 = {"llm": {"ollama_url": "http://remote-server:11434"}}
    provider1 = ModelProviderFactory.get_provider(config1)
    provider2 = ModelProviderFactory.get_provider(config2)
    assert provider1 is not provider2
    assert provider2.base_url == "http://remote-server:11434"


def test_ollama_provider_generate(monkeypatch):
    provider = OllamaProvider(base_url="http://localhost:11434", default_model="phi4-mini:3.8b")

    class MockResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": "Generated script text."}

    def mock_post(url, json, timeout):
        assert url == "http://localhost:11434/api/generate"
        assert json["model"] == "phi4-mini:3.8b"
        assert json["prompt"] == "Write a script."
        assert json["options"]["temperature"] == 0.7
        return MockResp()

    monkeypatch.setattr("requests.post", mock_post)
    res = provider.generate("Write a script.", temperature=0.7)
    assert res == "Generated script text."


def test_ollama_provider_generate_structured(monkeypatch):
    provider = OllamaProvider(base_url="http://localhost:11434", default_model="qwen2.5:3b")

    class MockResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": '{"message": "Hello", "score": 10}'}

    def mock_post(url, json, timeout):
        assert url == "http://localhost:11434/api/generate"
        assert json["model"] == "qwen2.5:3b"
        assert "format" in json
        return MockResp()

    monkeypatch.setattr("requests.post", mock_post)
    res = provider.generate_structured(
        prompt="Return test JSON",
        schema=DummySchema,
        model="qwen2.5:3b",
    )
    assert isinstance(res, DummySchema)
    assert res.message == "Hello"
    assert res.score == 10


def test_ollama_provider_unload_models(monkeypatch):
    provider = OllamaProvider(base_url="http://localhost:11434")

    calls = []

    class MockPsResp:
        ok = True

        def json(self):
            return {"models": [{"name": "phi4-mini:3.8b"}, {"name": "qwen2.5:3b"}]}

    def mock_get(url, timeout):
        assert url == "http://localhost:11434/api/ps"
        return MockPsResp()

    def mock_post(url, json, timeout):
        assert url == "http://localhost:11434/api/generate"
        calls.append(json["model"])
        assert json["keep_alive"] == 0

    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)

    provider.unload_models()
    assert calls == ["phi4-mini:3.8b", "qwen2.5:3b"]
