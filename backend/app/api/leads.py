import logging

import resend.exceptions
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.rate_limit import limiter
from app.models.audit_lead import AuditLead
from app.schemas.auth import MessageResponse
from app.schemas.leads import AuditLeadRequest
from app.services.email import get_email_provider
from app.services.email.base import EmailProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit-leads", tags=["leads"])


@router.post("", response_model=MessageResponse, status_code=201)
@limiter.limit("5/hour")
def create_audit_lead(
    request: Request,
    payload: AuditLeadRequest,
    db: Session = Depends(get_db),
    email_provider: EmailProvider = Depends(get_email_provider),
):
    """Public, unauthenticated: a free-AWS-audit request submitted from the
    landing page form. Persisted first so the lead is never lost even if
    the notification email fails to send."""
    lead = AuditLead(
        name=payload.name,
        company_name=payload.company_name,
        work_email=payload.work_email,
        monthly_spend_range=payload.monthly_spend_range,
        message=payload.message,
    )
    db.add(lead)
    db.commit()

    settings = get_settings()
    try:
        email_provider.send_audit_lead_notification(
            to_email=settings.AUDIT_LEAD_NOTIFICATION_EMAIL,
            name=payload.name,
            company_name=payload.company_name,
            work_email=payload.work_email,
            monthly_spend_range=payload.monthly_spend_range,
            message=payload.message,
        )
    except resend.exceptions.ResendError:
        # The lead is already saved — don't fail the request over a
        # transient notification failure. Log it server-side instead.
        logger.exception("Failed to send audit-lead notification email for lead %s", lead.id)

    return MessageResponse(message="Thanks — we'll be in touch shortly.")
