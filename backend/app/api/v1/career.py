"""Career data API: Skills, Evidence, and Evidence↔Skill links."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.evidence import Evidence
from app.models.evidence_skill import EvidenceSkill
from app.models.skill import Skill
from app.models.user import User
from app.schemas.career import (
    VALID_SOURCE_TYPES,
    EvidenceCreate,
    EvidenceResponse,
    EvidenceSkillCreate,
    EvidenceSkillInfo,
    EvidenceSkillResponse,
    EvidenceUpdate,
    SkillCreate,
    SkillResponse,
)

router = APIRouter(prefix="/career", tags=["career"])


# ────────────────────── Skills ──────────────────────


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    body: SkillCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new skill (or return existing one with same canonical name)."""
    canonical = body.name.strip().lower()
    result = await db.execute(
        select(Skill).where(Skill.canonical_name == canonical)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    skill = Skill(
        name=body.name.strip(),
        canonical_name=canonical,
        category=body.category,
        description=body.description,
    )
    db.add(skill)
    await db.flush()
    await db.refresh(skill)
    return skill


@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(
    q: Optional[str] = Query(None, min_length=1, description="Search skills by name"),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List skills, optionally filtered by name search or category."""
    stmt = select(Skill).order_by(Skill.name)
    if q:
        stmt = stmt.where(Skill.canonical_name.contains(q.strip().lower()))
    if category:
        stmt = stmt.where(Skill.category == category)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get a single skill by ID."""
    skill = await db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


# ────────────────────── Evidence ──────────────────────


def _build_evidence_response(evidence: Evidence) -> EvidenceResponse:
    """Convert an Evidence ORM object (with loaded skill_links) to response schema."""
    skills = [
        EvidenceSkillInfo(
            skill_id=link.skill_id,
            skill_name=link.skill.name,
            confidence=link.confidence,
            extraction_method=link.extraction_method,
        )
        for link in evidence.skill_links
    ]
    return EvidenceResponse(
        id=evidence.id,
        user_id=evidence.user_id,
        source_type=evidence.source_type,
        source_reference=evidence.source_reference,
        title=evidence.title,
        description=evidence.description,
        metadata_=evidence.metadata_,
        is_stale=evidence.is_stale,
        created_at=evidence.created_at,
        updated_at=evidence.updated_at,
        skills=skills,
    )


@router.post("/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    body: EvidenceCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new evidence item and optionally link skills."""
    if body.source_type not in VALID_SOURCE_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"source_type must be one of: {', '.join(sorted(VALID_SOURCE_TYPES))}",
        )

    evidence = Evidence(
        user_id=current_user.id,
        source_type=body.source_type,
        source_reference=body.source_reference,
        title=body.title,
        description=body.description,
        metadata_=body.metadata,
    )
    db.add(evidence)
    await db.flush()

    # Link requested skills (deduplicate to prevent duplicate links)
    unique_skill_ids = list(dict.fromkeys(body.skill_ids))
    for skill_id in unique_skill_ids:
        skill = await db.get(Skill, skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")
        link = EvidenceSkill(evidence_id=evidence.id, skill_id=skill_id)
        db.add(link)

    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(Evidence)
        .where(Evidence.id == evidence.id)
        .options(selectinload(Evidence.skill_links).selectinload(EvidenceSkill.skill))
    )
    evidence = result.scalar_one()
    return _build_evidence_response(evidence)


@router.get("/evidence", response_model=list[EvidenceResponse])
async def list_evidence(
    source_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List the current user's evidence items."""
    stmt = (
        select(Evidence)
        .where(Evidence.user_id == current_user.id)
        .options(selectinload(Evidence.skill_links).selectinload(EvidenceSkill.skill))
        .order_by(Evidence.created_at.desc())
    )
    if source_type:
        stmt = stmt.where(Evidence.source_type == source_type)
    result = await db.execute(stmt)
    return [_build_evidence_response(e) for e in result.scalars().all()]


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get a single evidence item (must belong to current user)."""
    result = await db.execute(
        select(Evidence)
        .where(Evidence.id == evidence_id, Evidence.user_id == current_user.id)
        .options(selectinload(Evidence.skill_links).selectinload(EvidenceSkill.skill))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return _build_evidence_response(evidence)


@router.patch("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: uuid.UUID,
    body: EvidenceUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Update an evidence item's mutable fields."""
    result = await db.execute(
        select(Evidence)
        .where(Evidence.id == evidence_id, Evidence.user_id == current_user.id)
        .options(selectinload(Evidence.skill_links).selectinload(EvidenceSkill.skill))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    update_data = body.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    for field, value in update_data.items():
        setattr(evidence, field, value)

    await db.flush()
    await db.refresh(evidence)
    return _build_evidence_response(evidence)


@router.delete("/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Delete an evidence item (cascades to evidence_skill links)."""
    result = await db.execute(
        select(Evidence).where(Evidence.id == evidence_id, Evidence.user_id == current_user.id)
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    await db.delete(evidence)


# ────────────────────── Evidence ↔ Skill links ──────────────────────


@router.post(
    "/evidence/{evidence_id}/skills",
    response_model=EvidenceSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_skill_to_evidence(
    evidence_id: uuid.UUID,
    body: EvidenceSkillCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Link a skill to an evidence item with optional confidence."""
    # Verify evidence ownership
    result = await db.execute(
        select(Evidence).where(Evidence.id == evidence_id, Evidence.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Verify skill exists
    skill = await db.get(Skill, body.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Check for duplicate link
    existing = await db.execute(
        select(EvidenceSkill).where(
            EvidenceSkill.evidence_id == evidence_id,
            EvidenceSkill.skill_id == body.skill_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Skill already linked to this evidence")

    link = EvidenceSkill(
        evidence_id=evidence_id,
        skill_id=body.skill_id,
        confidence=body.confidence,
        extraction_method=body.extraction_method,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


@router.delete(
    "/evidence/{evidence_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlink_skill_from_evidence(
    evidence_id: uuid.UUID,
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Remove a skill link from an evidence item."""
    # Verify evidence ownership
    ev_result = await db.execute(
        select(Evidence).where(Evidence.id == evidence_id, Evidence.user_id == current_user.id)
    )
    if not ev_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Evidence not found")

    result = await db.execute(
        select(EvidenceSkill).where(
            EvidenceSkill.evidence_id == evidence_id,
            EvidenceSkill.skill_id == skill_id,
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Skill link not found")
    await db.delete(link)
