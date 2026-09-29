"""AI provider abstraction for skill extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ExtractedSkill:
    """A skill extracted by AI from text."""

    name: str
    category: str | None = None
    confidence: float = 0.5
    context: str | None = None  # brief snippet explaining why this skill was identified


class SkillExtractor(Protocol):
    """Protocol for AI skill extraction providers."""

    async def extract_skills(self, text: str) -> list[ExtractedSkill]:
        """Extract skills from text and return structured results."""
        ...
