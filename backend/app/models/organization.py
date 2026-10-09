"""A customer tenant.

Each Organization has its own users and AWS connection — this is the
isolation boundary between Cloudheo customers.
"""

import uuid
from datetime import datetime, UTC

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
