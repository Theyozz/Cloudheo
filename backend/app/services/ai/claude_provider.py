"""Claude-backed explanation provider.

Uses Haiku — this is short, factual narration of numbers the FinOps engine
already computed, not a task that needs a larger model.
"""

import anthropic

from app.core.config import get_settings
from app.schemas.recommendations import Recommendation
from app.services.ai.base import ExplanationProvider

MODEL = "claude-haiku-5-5"

SYSTEM_PROMPT = (
    "You are Cloudheo's FinOps assistant. You turn a cloud cost optimization "
    "recommendation into a short, clear explanation for a non-technical "
    "business owner. Use only the numbers given to you — never invent or "
    "recalculate a figure. Two to three sentences, plain language, no "
    "markdown, no bullet points."
)


class ClaudeExplanationProvider(ExplanationProvider):
    def __init__(self):
        settings = get_settings()
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def explain(self, recommendation: Recommendation) -> str:
        prompt = (
            f"Resource: {recommendation.resource_type} {recommendation.resource_id}\n"
            f"Category: {recommendation.category}\n"
            f"Current cost: ${recommendation.current_cost}/month\n"
            f"Estimated savings: ${recommendation.estimated_savings}/month\n"
            f"Risk level: {recommendation.risk}\n"
            f"Confidence: {round(recommendation.confidence * 100)}%\n"
            f"Technical detail: {recommendation.description}\n\n"
            "Explain this recommendation to the business owner."
        )

        response = self._client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        return next((block.text for block in response.content if block.type == "text"), "")
