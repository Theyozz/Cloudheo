"""No-network explanation provider — used in tests so the suite stays fast,
deterministic, and runnable without an Anthropic API key.
"""

from app.schemas.recommendations import Recommendation
from app.services.ai.base import ExplanationProvider


class StubExplanationProvider(ExplanationProvider):
    def explain(self, recommendation: Recommendation) -> str:
        return (
            f"[stub] {recommendation.title} — estimated savings "
            f"${recommendation.estimated_savings}/month ({recommendation.risk} risk)."
        )
