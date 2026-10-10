"""No-network fake email provider, used in tests.

SENT_EMAILS is module-level so tests can both assert an email was "sent"
and recover the reset_url (and the raw token in it) to drive the rest of
the forgot-password flow end to end, without ever calling the real API.
"""

from app.services.email.base import EmailProvider

SENT_EMAILS: list[dict] = []


class StubEmailProvider(EmailProvider):
    def send_password_reset(self, to_email: str, reset_url: str) -> None:
        SENT_EMAILS.append({"to": to_email, "reset_url": reset_url})

    def send_audit_lead_notification(
        self,
        to_email: str,
        name: str,
        company_name: str,
        work_email: str,
        monthly_spend_range: str,
        message: str | None,
    ) -> None:
        SENT_EMAILS.append(
            {
                "to": to_email,
                "name": name,
                "company_name": company_name,
                "work_email": work_email,
                "monthly_spend_range": monthly_spend_range,
                "message": message,
            }
        )
