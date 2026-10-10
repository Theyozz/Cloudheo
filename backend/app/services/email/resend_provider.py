"""Resend-backed email provider."""

import html

import resend

from app.core.config import get_settings
from app.services.email.base import EmailProvider


class ResendEmailProvider(EmailProvider):
    def __init__(self):
        settings = get_settings()
        resend.api_key = settings.RESEND_API_KEY
        self._from = settings.EMAIL_FROM

    def send_password_reset(self, to_email: str, reset_url: str) -> None:
        resend.Emails.send(
            {
                "from": self._from,
                "to": [to_email],
                "subject": "Reset your Cloudheo password",
                "html": (
                    "<p>Someone asked to reset the password for this Cloudheo account.</p>"
                    f'<p><a href="{reset_url}">Reset your password</a></p>'
                    "<p>This link expires in 1 hour. If you didn't request this, you can ignore this email.</p>"
                ),
            }
        )

    def send_audit_lead_notification(
        self,
        to_email: str,
        name: str,
        company_name: str,
        work_email: str,
        monthly_spend_range: str,
        message: str | None,
    ) -> None:
        # User-submitted values from a public, unauthenticated form — escape
        # before interpolating into HTML.
        safe_name = html.escape(name)
        safe_company = html.escape(company_name)
        safe_email = html.escape(work_email)
        safe_message = html.escape(message) if message else None

        resend.Emails.send(
            {
                "from": self._from,
                "to": [to_email],
                "reply_to": work_email,
                "subject": f"New free AWS audit request — {company_name}",
                "html": (
                    f"<p><strong>{safe_name}</strong> at <strong>{safe_company}</strong> requested a free AWS audit.</p>"
                    f"<p>Work email: {safe_email}</p>"
                    f"<p>Approximate monthly AWS spend: {monthly_spend_range}</p>"
                    + (f"<p>Message: {safe_message}</p>" if safe_message else "")
                ),
            }
        )
