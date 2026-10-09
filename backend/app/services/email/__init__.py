"""FastAPI dependency for the email provider. Tests override this via
``app.dependency_overrides`` to inject the stub instead of calling Resend.
"""

from app.services.email.base import EmailProvider
from app.services.email.resend_provider import ResendEmailProvider


def get_email_provider() -> EmailProvider:
    return ResendEmailProvider()
