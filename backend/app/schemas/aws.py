from pydantic import BaseModel, Field


class TestConnectionRequest(BaseModel):
    role_arn: str = Field(..., examples=["arn:aws:iam::123456789012:role/CloudheoReadOnlyRole"])
    external_id: str | None = None


class TestConnectionResponse(BaseModel):
    success: bool
    account_id: str
    assumed_role_arn: str
    expiration: str
