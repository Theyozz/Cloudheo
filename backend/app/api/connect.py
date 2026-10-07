from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.aws_account import AwsAccount
from app.schemas.dashboard import AwsAccountStatus, ConnectAwsAccountRequest
from app.services.aws.sts import AssumeRoleError, assume_role, get_caller_identity

router = APIRouter(prefix="/aws", tags=["aws"], dependencies=[Depends(get_current_user)])


def _to_status(account: AwsAccount | None) -> AwsAccountStatus:
    if account is None:
        return AwsAccountStatus(connected=False)
    return AwsAccountStatus(
        connected=True,
        aws_account_id=account.aws_account_id,
        role_arn=account.role_arn,
        region=account.region,
        connected_at=account.connected_at.isoformat(),
    )


@router.post("/connect", response_model=AwsAccountStatus)
def connect_aws_account(payload: ConnectAwsAccountRequest, db: Session = Depends(get_db)):
    """Validate and store the customer's read-only role. MVP simplification:
    single-tenant — connecting a new account replaces the previous one."""
    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        identity = get_caller_identity(creds)
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.query(AwsAccount).delete()
    account = AwsAccount(
        aws_account_id=identity["Account"],
        role_arn=payload.role_arn,
        external_id=payload.external_id,
        region=payload.region,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return _to_status(account)


@router.get("/connect", response_model=AwsAccountStatus)
def get_connected_account(db: Session = Depends(get_db)):
    account = db.query(AwsAccount).first()
    return _to_status(account)


@router.delete("/connect", response_model=AwsAccountStatus)
def disconnect_aws_account(db: Session = Depends(get_db)):
    db.query(AwsAccount).delete()
    db.commit()
    return _to_status(None)
