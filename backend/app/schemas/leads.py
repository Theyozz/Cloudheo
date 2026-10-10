from typing import Literal

from pydantic import BaseModel, EmailStr, Field

MonthlySpendRange = Literal["under_10k", "10k_50k", "50k_200k", "over_200k"]


class AuditLeadRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    company_name: str = Field(..., min_length=1, max_length=200)
    work_email: EmailStr
    monthly_spend_range: MonthlySpendRange
    message: str | None = Field(None, max_length=2000)
