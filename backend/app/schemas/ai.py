from pydantic import BaseModel

from app.schemas.recommendations import Recommendation


class ExplainRequest(BaseModel):
    recommendation: Recommendation


class ExplainResponse(BaseModel):
    explanation: str
