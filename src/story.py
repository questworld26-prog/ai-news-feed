"""
Story Data Class Module
Provides a structured dataclass for RSS feed entries with helpers for LLM prompt context creation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# [spec: INGEST-003]
# [spec: AIM-002]
@dataclass
class Story:
    """
    Represents a structured feed entry story throughout the briefing pipeline.
    """

    source: str
    title: str
    link: str
    summary: str
    pub_dt: datetime | None = None
    points: int = 0
    score: float = 0.0
    validated_summary: str | None = None
    extra_metadata: dict[str, Any] = field(default_factory=dict)
    is_update: bool = False
    original_briefed_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert Story instance to dictionary representation."""
        return {
            "source": self.source,
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "pub_dt": self.pub_dt,
            "points": self.points,
            "score": self.score,
            "validated_summary": self.validated_summary,
            "extra_metadata": self.extra_metadata,
            "is_update": self.is_update,
            "original_briefed_date": self.original_briefed_date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Story:
        """Construct a Story instance from a dictionary."""
        return cls(
            source=data.get("source", "Unknown"),
            title=data.get("title", "Untitled"),
            link=data.get("link", ""),
            summary=data.get("summary", ""),
            pub_dt=data.get("pub_dt"),
            points=data.get("points", 0),
            score=data.get("score", 0.0),
            validated_summary=data.get("validated_summary"),
            extra_metadata=data.get("extra_metadata", {}),
            is_update=data.get("is_update", False),
            original_briefed_date=data.get("original_briefed_date"),
        )

    def to_prompt_context(self, idx: int | None = None, max_summary_chars: int = 400) -> str:
        """Format story for inclusion in LLM prompts."""
        prefix = f"{idx}. " if idx is not None else ""
        update_tag = (
            f" [UPDATE - Previously briefed on {self.original_briefed_date}]"
            if self.is_update and self.original_briefed_date
            else (" [UPDATE]" if self.is_update else "")
        )
        s_text = self.summary[:max_summary_chars] if self.summary else "No summary available."
        return (
            f"{prefix}[{self.source}]{update_tag} {self.title}\n"
            f"   Link: {self.link}\n"
            f"   Points: {self.points}\n"
            f"   Summary: {s_text}"
        )

    def to_structured_prompt_dict(self) -> dict[str, Any]:
        """Return structured dict formatted for schema-constrained LLM outputs."""
        d = {
            "source": self.source,
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "points": self.points,
        }
        if self.is_update:
            d["is_update"] = True
            d["original_briefed_date"] = self.original_briefed_date
        return d


# [spec: AIM-004]
@dataclass
class BriefingOutput:
    """
    Structured output representing a complete daily briefing digest.
    Guarantees strict, standardized markdown layout structure across all generated .md files.
    """

    theme_name: str
    theme_emoji: str
    theme_description: str
    stories: list[Story]
    text_digest: str
    audio_script: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """
        Render the strict, standardized markdown content for .md storage.
        Ensures consistent headers, structured story blocks, and optional spoken script section.
        """
        content = [self.text_digest.strip()]
        if self.audio_script.strip():
            content.append("\n\n## Spoken Audio Script\n\n" + self.audio_script.strip())
        return "\n".join(content)

    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like get method for backwards compatibility."""
        if key == "text_digest":
            return self.text_digest
        if key == "audio_script":
            return self.audio_script
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like indexing for backwards compatibility."""
        if key == "text_digest":
            return self.text_digest
        if key == "audio_script":
            return self.audio_script
        raise KeyError(key)
