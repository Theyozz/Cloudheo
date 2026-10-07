import anthropic
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.schemas.ai import ExplainRequest, ExplainResponse
from app.services.ai import get_ai_provider
from app.services.ai.base import ExplanationProvider

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(get_current_user)])


@router.post("/explain", response_model=ExplainResponse)
def explain_recommendation(
    payload: ExplainRequest,
    provider: ExplanationProvider = Depends(get_ai_provider),
):
    """Turn one recommendation's already-computed numbers into plain language.
    Called on demand, per recommendation — not automatically for a whole
    list, to keep dashboard loads fast and avoid unnecessary LLM spend."""
    try:
        explanation = provider.explain(payload.recommendation)
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ExplainResponse(explanation=explanation)
