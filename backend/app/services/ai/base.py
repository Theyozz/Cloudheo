"""The explanation provider interface.

Cloudheo must never be locked into one LLM vendor — this is the only contract
the rest of the app depends on. Swapping providers (or using a stub in tests)
means writing a new class here, nothing else changes.
"""

from abc import ABC, abstractmethod

from app.schemas.recommendations import Recommendation


class ExplanationProvider(ABC):
    @abstractmethod
    def explain(self, recommendation: Recommendation) -> str:
        """Return a natural-language explanation of a recommendation.

        The provider only narrates numbers it is given — it never computes
        or invents a cost, saving, or confidence figure itself.
        """
