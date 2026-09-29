"""Resume upload and processing API."""

import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.evidence import Evidence
from app.models.evidence_skill import EvidenceSkill
from app.models.user import User
from app.schemas.resume import ResumeSkillResult, ResumeUploadResponse
from app.services.resume_service import process_resume
from app.services.text_extraction import MAX_FILE_SIZE, SUPPORTED_CONTENT_TYPES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Upload a resume (PDF or DOCX), extract text, extract skills via AI.

    Returns the created evidence record with extracted skills.
    """
    # Validate content type
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type: {file.content_type}. Supported: PDF, DOCX",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=422,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=422, detail="File is empty")

    # Process: store → extract text → extract skills → create evidence
    try:
        evidence = await process_resume(
            db=db,
            user_id=current_user.id,
            filename=file.filename or "resume",
            content_type=file.content_type,
            content=content,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Resume processing failed")
        raise HTTPException(status_code=500, detail="Resume processing failed")

    # Reload with skill relationships
    result = await db.execute(
        select(Evidence)
        .where(Evidence.id == evidence.id)
        .options(selectinload(Evidence.skill_links).selectinload(EvidenceSkill.skill))
    )
    evidence = result.scalar_one()

    # Build response
    skills = [
        ResumeSkillResult(
            skill_id=link.skill_id,
            name=link.skill.name,
            category=link.skill.category,
            confidence=link.confidence or 0.5,
            extraction_method=link.extraction_method,
        )
        for link in evidence.skill_links
    ]

    return ResumeUploadResponse(
        evidence_id=evidence.id,
        title=evidence.title,
        source_type=evidence.source_type,
        filename=file.filename or "resume",
        text_length=evidence.metadata_.get("text_length", 0) if evidence.metadata_ else 0,
        skills_extracted=len(skills),
        skills=skills,
        created_at=evidence.created_at,
    )


@router.get("/evidence", response_model=list[ResumeUploadResponse])
async def list_resume_evidence(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List all resume evidence for the current user."""
    result = await db.execute(
        select(Evidence)
        .where(Evidence.user_id == current_user.id, Evidence.source_type == "resume")
        .options(selectinload(Evidence.skill_links).selectinload(EvidenceSkill.skill))
        .order_by(Evidence.created_at.desc())
    )
    evidences = result.scalars().all()

    responses = []
    for ev in evidences:
        skills = [
            ResumeSkillResult(
                skill_id=link.skill_id,
                name=link.skill.name,
                category=link.skill.category,
                confidence=link.confidence or 0.5,
                extraction_method=link.extraction_method,
            )
            for link in ev.skill_links
        ]
        filename = "resume"
        if ev.metadata_ and "original_filename" in ev.metadata_:
            filename = ev.metadata_["original_filename"]

        responses.append(
            ResumeUploadResponse(
                evidence_id=ev.id,
                title=ev.title,
                source_type=ev.source_type,
                filename=filename,
                text_length=ev.metadata_.get("text_length", 0) if ev.metadata_ else 0,
                skills_extracted=len(skills),
                skills=skills,
                created_at=ev.created_at,
            )
        )

    return responses
