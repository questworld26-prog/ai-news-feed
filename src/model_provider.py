"""
Model Provider and LLM Client Factory Module.
Provides centralized LLM abstraction, Ollama client integration, and model management
across all pipeline roles (curation, summarization, scriptwriting, auditing, TTS offload).
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import requests
from pydantic import BaseModel

logger = logging.getLogger("ai_briefing")

T = TypeVar("T", bound=BaseModel)


# [spec: AIM-001]
class ModelProvider(ABC):
    """Abstract Base Class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        num_ctx: int = 4096,
        timeout: int = 120,
    ) -> str:
        """Generate text completion from prompt."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        model: str | None = None,
        temperature: float = 0.1,
        num_ctx: int = 4096,
        timeout: int = 120,
    ) -> T:
        """Generate structured completion validated against a Pydantic schema."""
        pass

    @abstractmethod
    def unload_models(self) -> None:
        """Unload active models from VRAM/unified memory."""
        pass


class OllamaProvider(ModelProvider):
    """
    Ollama implementation of ModelProvider.
    Uses a centralized base URL resolved from config.
    """

    def __init__(self, base_url: str, default_model: str = "phi4-mini:3.8b") -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        num_ctx: int = 4096,
        timeout: int = 120,
    ) -> str:
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx},
        }
        resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        model: str | None = None,
        temperature: float = 0.1,
        num_ctx: int = 4096,
        timeout: int = 120,
    ) -> T:
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "prompt": prompt,
            "format": schema.model_json_schema(),
            "stream": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx},
        }
        resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=timeout)
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        data = json.loads(raw)
        return schema.model_validate(data)

    def unload_models(self) -> None:
        """Offload any active models from Ollama memory via keep_alive=0."""
        try:
            ps_resp = requests.get(f"{self.base_url}/api/ps", timeout=5)
            if ps_resp.ok:
                models = ps_resp.json().get("models", [])
                if not models:
                    logger.debug("No active Ollama models loaded in memory.")
                    return

                for m in models:
                    m_name = m.get("name")
                    if m_name:
                        logger.info(f"🧹 Offloading LLM '{m_name}' from unified memory for TTS headroom...")
                        requests.post(
                            f"{self.base_url}/api/generate",
                            json={"model": m_name, "keep_alive": 0},
                            timeout=5,
                        )
        except Exception as e:
            logger.warning(f"Could not offload Ollama models: {e}")


class ModelProviderFactory:
    """Factory for creating and retrieving configured ModelProvider instances."""

    _instance: ModelProvider | None = None
    _cached_url: str | None = None

    @classmethod
    def get_provider(cls, config: dict[str, Any]) -> ModelProvider:
        """
        Return a singleton or cached ModelProvider instance using config settings.
        Resolves the single base URL from config['llm']['ollama_url'].
        """
        llm_cfg = config.get("llm", {})
        base_url = llm_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
        default_model = llm_cfg.get("model", "phi4-mini:3.8b")
        provider_type = llm_cfg.get("provider", "ollama").lower()

        # Return cached instance if URL and type have not changed
        if cls._instance is not None and cls._cached_url == base_url:
            return cls._instance

        if provider_type == "ollama":
            cls._instance = OllamaProvider(base_url=base_url, default_model=default_model)
            cls._cached_url = base_url
            return cls._instance
        else:
            raise ValueError(f"Unsupported model provider type: '{provider_type}'")

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for unit tests and re-configurations)."""
        cls._instance = None
        cls._cached_url = None
