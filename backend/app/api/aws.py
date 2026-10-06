from fastapi import APIRouter, HTTPException

from app.schemas.aws import TestConnectionRequest, TestConnectionResponse
from app.services.aws.sts import AssumeRoleError, assume_role, get_caller_identity

router = APIRouter(prefix="/aws", tags=["aws"])


@router.post("/test-connection", response_model=TestConnectionResponse)
def test_connection(payload: TestConnectionRequest):
    """Validate that Cloudheo can assume a customer's read-only role.

    This performs no resource scan — it only confirms the AssumeRole trust
    relationship is set up correctly, by assuming the role and calling
    ``sts:GetCallerIdentity`` with the resulting temporary credentials.
    """
    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        identity = get_caller_identity(creds)
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TestConnectionResponse(
        success=True,
        account_id=identity["Account"],
        assumed_role_arn=creds.assumed_role_arn,
        expiration=creds.expiration.isoformat(),
    )
