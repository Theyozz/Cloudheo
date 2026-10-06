"""SQLAlchemy models.

Empty for now — models will be added sprint by sprint (User, Organization,
AwsAccount, Resource, Cost, Recommendation, ...). Each new model module
should be imported here so Alembic's autogenerate can discover it via
``Base.metadata``.
"""

from app.core.db import Base

__all__ = ["Base"]
