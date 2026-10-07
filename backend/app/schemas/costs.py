from pydantic import BaseModel, Field


class CostSummaryRequest(BaseModel):
    role_arn: str = Field(..., examples=["arn:aws:iam::123456789012:role/CloudheoReadOnlyRole"])
    external_id: str | None = None
    start_date: str | None = Field(None, description="YYYY-MM-DD, defaults to 30 days ago")
    end_date: str | None = Field(None, description="YYYY-MM-DD, defaults to today")


class CostByService(BaseModel):
    service: str
    amount: float


class CostSummaryResponse(BaseModel):
    start_date: str
    end_date: str
    currency: str = "USD"
    total_cost: float
    by_service: list[CostByService]
