"""Pydantic schemas for resume upload and processing responses."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResumeSkillResult(BaseModel):
    """A single skill extracted from a resume."""

    skill_id: uuid.UUID
    name: str
    category: Optional[str]
    confidence: float
    extraction_method: Optional[str]


class ResumeUploadResponse(BaseModel):
    """Response after resume upload and processing."""

    evidence_id: uuid.UUID
    title: str
    source_type: str
    filename: str
    text_length: int
    skills_extracted: int
    skills: list[ResumeSkillResult]
    created_at: datetime
