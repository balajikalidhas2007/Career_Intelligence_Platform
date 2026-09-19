import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuthAccount(Base):
    __tablename__ = "auth_account"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE")
    )
    provider: Mapped[str] = mapped_column(String, index=True)
    provider_account_id: Mapped[str] = mapped_column(String, index=True)
    provider_username: Mapped[Optional[str]] = mapped_column(String)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(String)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[Optional[str]] = mapped_column(String)
    raw_profile: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    user: Mapped["User"] = relationship("User", back_populates="auth_accounts")

    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uix_auth_account_provider"),
    )
