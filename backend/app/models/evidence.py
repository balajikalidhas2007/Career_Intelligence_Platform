import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Evidence(Base):
    """A piece of evidence supporting one or more skills.

    Evidence represents concrete artifacts: a resume, a GitHub repo,
    a project description, an assessment result, or a manual entry.
    Each evidence item belongs to exactly one user.
    """

    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    source_type: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    source_reference: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)
    is_stale: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    user: Mapped["User"] = relationship("User", back_populates="evidence_items")
    skill_links: Mapped[List["EvidenceSkill"]] = relationship(
        "EvidenceSkill", back_populates="evidence", cascade="all, delete-orphan"
    )
