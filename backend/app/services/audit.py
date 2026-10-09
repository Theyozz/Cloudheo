"""Records audit log entries. Adds to the session only — callers commit as
part of their existing transaction, so the audit entry is atomic with the
action it describes."""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditAction:
    AUTH_REGISTER = "auth.register"
    AUTH_LOGIN = "auth.login"
    AUTH_PASSWORD_RESET_REQUESTED = "auth.password_reset_requested"
    AUTH_PASSWORD_RESET_COMPLETED = "auth.password_reset_completed"
    AWS_CONNECT = "aws.connect"
    AWS_DISCONNECT = "aws.disconnect"


def log_action(
    db: Session,
    *,
    organization_id: str,
    user_id: str,
    action: str,
    details: dict | None = None,
) -> None:
    db.add(AuditLog(organization_id=organization_id, user_id=user_id, action=action, details=details))
