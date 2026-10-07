"""The AWS account Cloudheo is currently connected to.

MVP simplification: single-tenant, one connected account at a time. No
Organization/User model yet — those arrive with auth (Sprint 6). Connecting
a new account replaces the previous one.
"""

import uuid
from datetime import datetime, UTC

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AwsAccount(Base):
    __tablename__ = "aws_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    aws_account_id: Mapped[str] = mapped_column(String, nullable=False)
    role_arn: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    # Restrict scans to a single region — useful for sandboxed/guardrailed
    # AWS accounts; leave null to scan every enabled region (normal case).
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
