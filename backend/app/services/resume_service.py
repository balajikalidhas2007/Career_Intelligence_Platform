"""Resume processing service: upload, extract text, extract skills, create evidence."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini import get_skill_extractor
from app.ai.provider import ExtractedSkill
from app.models.evidence import Evidence
from app.models.evidence_skill import EvidenceSkill
from app.models.skill import Skill
from app.services.text_extraction import extract_text
from app.storage.local import save_file

logger = logging.getLogger(__name__)


async def process_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
    filename: str,
    content_type: str,
    content: bytes,
) -> Evidence:
    """Full resume processing pipeline.

    1. Store the file
    2. Extract text
    3. Extract skills via AI
    4. Create Evidence + Skill + EvidenceSkill records

    Returns the created Evidence with skill_links loaded.
    """
    # 1. Store file
    storage_key = await save_file(user_id, filename, content)

    # 2. Extract text
    resume_text = extract_text(content, content_type)

    # 3. Extract skills via AI
    extractor = get_skill_extractor()
    extracted_skills = await extractor.extract_skills(resume_text)

    # 4. Create Evidence record
    evidence = Evidence(
        user_id=user_id,
        source_type="resume",
        source_reference=storage_key,
        title=f"Resume: {filename}",
        description=f"Uploaded resume ({len(resume_text)} chars extracted)",
        metadata_={
            "original_filename": filename,
            "content_type": content_type,
            "text_length": len(resume_text),
            "skills_extracted": len(extracted_skills),
        },
    )
    db.add(evidence)
    await db.flush()

    # 5. Upsert skills and create links
    await _link_extracted_skills(db, evidence, extracted_skills)

    await db.flush()
    return evidence


async def _link_extracted_skills(
    db: AsyncSession,
    evidence: Evidence,
    extracted_skills: list[ExtractedSkill],
) -> None:
    """Upsert skills by canonical_name and link to evidence."""
    seen_canonical: set[str] = set()

    for es in extracted_skills:
        canonical = es.name.strip().lower()
        if not canonical or canonical in seen_canonical:
            continue
        seen_canonical.add(canonical)

        # Find or create skill
        result = await db.execute(
            select(Skill).where(Skill.canonical_name == canonical)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            skill = Skill(
                name=es.name.strip(),
                canonical_name=canonical,
                category=es.category,
            )
            db.add(skill)
            await db.flush()

        # Create evidence-skill link
        link = EvidenceSkill(
            evidence_id=evidence.id,
            skill_id=skill.id,
            confidence=es.confidence,
            extraction_method="gemini_resume",
        )
        db.add(link)
