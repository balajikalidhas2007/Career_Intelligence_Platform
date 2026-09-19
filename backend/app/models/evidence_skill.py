import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EvidenceSkill(Base):
    """Many-to-many association between Evidence and Skill.

    Carries optional confidence and extraction metadata so the link
    itself can record how strongly the evidence supports the skill.
    """

    __tablename__ = "evidence_skill"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill.id", ondelete="CASCADE"),
        index=True,
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    extraction_method: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    evidence: Mapped["Evidence"] = relationship("Evidence", back_populates="skill_links")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="evidence_links")

    __table_args__ = (
        UniqueConstraint("evidence_id", "skill_id", name="uix_evidence_skill"),
    )
