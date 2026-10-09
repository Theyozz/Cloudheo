from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    id: str
    user_id: str
    action: str
    details: dict | None
    created_at: str
