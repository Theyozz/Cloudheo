"""The email provider interface.

Mirrors app/services/ai: one contract the rest of the app depends on, so
tests never send a real email and swapping providers means writing a new
class here, nothing else.
"""

from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    def send_password_reset(self, to_email: str, reset_url: str) -> None:
        """Send a password-reset email containing a link to reset_url."""

    @abstractmethod
    def send_audit_lead_notification(
        self,
        to_email: str,
        name: str,
        company_name: str,
        work_email: str,
        monthly_spend_range: str,
        message: str | None,
    ) -> None:
        """Notify Cloudheo that a new free-audit lead was submitted on the landing page."""
