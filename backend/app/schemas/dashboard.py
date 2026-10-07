from pydantic import BaseModel, Field

from app.schemas.recommendations import Recommendation


class ConnectAwsAccountRequest(BaseModel):
    role_arn: str = Field(..., examples=["arn:aws:iam::123456789012:role/CloudheoReadOnlyRole"])
    external_id: str | None = None
    region: str | None = Field(
        None, description="Restrict scans to a single region instead of every enabled region"
    )


class AwsAccountStatus(BaseModel):
    connected: bool
    aws_account_id: str | None = None
    role_arn: str | None = None
    region: str | None = None
    connected_at: str | None = None


class CategorySaving(BaseModel):
    category: str
    amount: float


class DashboardSummaryResponse(BaseModel):
    connected: bool
    aws_account_id: str | None = None
    monthly_spend: float = 0.0
    potential_savings: float = 0.0
    savings_percent: float = 0.0
    recommendations_count: int = 0
    savings_by_category: list[CategorySaving] = []
    top_recommendations: list[Recommendation] = []
