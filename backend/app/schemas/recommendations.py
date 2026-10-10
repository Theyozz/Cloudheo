from typing import Literal

from pydantic import BaseModel

Risk = Literal["LOW", "MEDIUM", "HIGH"]


class Recommendation(BaseModel):
    resource_id: str
    resource_type: Literal["EC2", "EBS", "RDS", "ELASTIC_IP", "SAVINGS_PLAN"]
    category: str
    current_cost: float
    estimated_optimized_cost: float
    estimated_savings: float
    risk: Risk
    confidence: float
    title: str
    description: str
