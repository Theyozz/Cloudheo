"""FastAPI dependency for the explanation provider. Tests override this via
``app.dependency_overrides`` to inject the stub instead of calling Claude.
"""

from app.services.ai.base import ExplanationProvider
from app.services.ai.claude_provider import ClaudeExplanationProvider


def get_ai_provider() -> ExplanationProvider:
    return ClaudeExplanationProvider()
