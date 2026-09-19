"""Pydantic schemas for Skill, Evidence, and EvidenceSkill."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------- Skill ----------

class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    description: Optional[str] = None


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    canonical_name: str
    category: Optional[str]
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Evidence ----------

VALID_SOURCE_TYPES = {"resume", "github", "project", "assessment", "interview", "manual"}


class EvidenceCreate(BaseModel):
    source_type: str = Field(..., min_length=1)
    source_reference: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    metadata: Optional[dict] = None
    skill_ids: list[uuid.UUID] = Field(default_factory=list)


class EvidenceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    source_reference: Optional[str] = None
    metadata: Optional[dict] = None
    is_stale: Optional[bool] = None


class EvidenceSkillInfo(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    confidence: Optional[float]
    extraction_method: Optional[str]

    model_config = {"from_attributes": True}


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    source_type: str
    source_reference: Optional[str]
    title: str
    description: Optional[str]
    metadata: Optional[dict] = Field(None, alias="metadata_")
    is_stale: bool
    created_at: datetime
    updated_at: datetime
    skills: list[EvidenceSkillInfo] = []

    model_config = {"from_attributes": True, "populate_by_name": True}


# ---------- EvidenceSkill link ----------

class EvidenceSkillCreate(BaseModel):
    skill_id: uuid.UUID
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    extraction_method: Optional[str] = None


class EvidenceSkillResponse(BaseModel):
    id: uuid.UUID
    evidence_id: uuid.UUID
    skill_id: uuid.UUID
    confidence: Optional[float]
    extraction_method: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
