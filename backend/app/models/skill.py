import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Skill(Base):
    """A normalized skill entity.

    Skills are deduplicated by canonical_name (lowercased, trimmed).
    Multiple evidence items can reference the same skill.
    """

    __tablename__ = "skill"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    canonical_name: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    category: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    evidence_links: Mapped[List["EvidenceSkill"]] = relationship(
        "EvidenceSkill", back_populates="skill", cascade="all, delete-orphan"
    )
