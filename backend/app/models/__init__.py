"""SQLAlchemy models.

Models are added sprint by sprint (User, Organization, Resource, Cost,
Recommendation, ...). Each new model module is imported here so Alembic's
autogenerate can discover it via ``Base.metadata``.
"""

from app.core.db import Base
from app.models.aws_account import AwsAccount

__all__ = ["Base", "AwsAccount"]
