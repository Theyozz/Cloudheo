"""A free-AWS-audit request submitted through the public landing page form.

Not to be confused with AuditLog (the security audit trail for actions
inside an authenticated organization) — this is a marketing lead, captured
before anyone has an account.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AuditLead(Base):
    __tablename__ = "audit_leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    work_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    monthly_spend_range: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
