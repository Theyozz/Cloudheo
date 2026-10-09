"""The AWS account an Organization is currently connected to.

MVP simplification: one connected account per Organization at a time.
Connecting a new account replaces the previous one for that Organization.
"""

import uuid
from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AwsAccount(Base):
    __tablename__ = "aws_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id"), nullable=False, index=True
    )
    aws_account_id: Mapped[str] = mapped_column(String, nullable=False)
    role_arn: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    # Restrict scans to a single region — useful for sandboxed/guardrailed
    # AWS accounts; leave null to scan every enabled region (normal case).
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
