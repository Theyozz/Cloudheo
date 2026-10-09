from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogEntry

router = APIRouter(prefix="/audit-logs", tags=["audit"])

MAX_ENTRIES = 200


@router.get("", response_model=list[AuditLogEntry])
def list_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Most recent audit log entries for the current organization, newest first."""
    entries = (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == current_user.organization_id)
        .order_by(AuditLog.created_at.desc())
        .limit(MAX_ENTRIES)
        .all()
    )
    return [
        AuditLogEntry(
            id=e.id,
            user_id=e.user_id,
            action=e.action,
            details=e.details,
            created_at=e.created_at.isoformat(),
        )
        for e in entries
    ]
