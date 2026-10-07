from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.schemas.aws import TestConnectionRequest, TestConnectionResponse
from app.schemas.costs import CostSummaryRequest, CostSummaryResponse
from app.services.aws.cost_explorer import default_date_range, get_cost_by_service
from app.services.aws.sts import (
    AssumeRoleError,
    assume_role,
    get_caller_identity,
    session_from_assumed_credentials,
)

router = APIRouter(prefix="/aws", tags=["aws"], dependencies=[Depends(get_current_user)])


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


@router.post("/costs", response_model=CostSummaryResponse)
def get_costs(payload: CostSummaryRequest):
    """Fetch total AWS spend and spend by service for a customer account."""
    default_start, default_end = default_date_range()
    start_date = payload.start_date or default_start
    end_date = payload.end_date or default_end

    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        session = session_from_assumed_credentials(creds)
        by_service = get_cost_by_service(session, start_date, end_date)
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CostSummaryResponse(
        start_date=start_date,
        end_date=end_date,
        total_cost=round(sum(item["amount"] for item in by_service), 2),
        by_service=by_service,
    )
