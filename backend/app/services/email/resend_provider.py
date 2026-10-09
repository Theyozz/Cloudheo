"""Resend-backed email provider."""

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
