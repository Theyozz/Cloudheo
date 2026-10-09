"""A record of a sensitive action taken within an Organization.

Covers authentication events and AWS account connect/disconnect — not every
read, just actions worth being able to answer "who did this, and when" for.
"""

import uuid
from datetime import datetime, UTC

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
