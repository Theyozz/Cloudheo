from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.aws_account import AwsAccount
from app.models.user import User
from app.schemas.dashboard import AwsAccountStatus, ConnectAwsAccountRequest
from app.services.audit import AuditAction, log_action
from app.services.aws.sts import AssumeRoleError, assume_role, get_caller_identity

router = APIRouter(prefix="/aws", tags=["aws"])


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
def connect_aws_account(
    payload: ConnectAwsAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate and store the organization's read-only role. MVP
    simplification: one connected account per organization — connecting a
    new account replaces the previous one."""
    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        identity = get_caller_identity(creds)
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.query(AwsAccount).filter(AwsAccount.organization_id == current_user.organization_id).delete()
    account = AwsAccount(
        organization_id=current_user.organization_id,
        aws_account_id=identity["Account"],
        role_arn=payload.role_arn,
        external_id=payload.external_id,
        region=payload.region,
    )
    db.add(account)
    log_action(
        db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.AWS_CONNECT,
        details={"aws_account_id": account.aws_account_id, "role_arn": account.role_arn, "region": account.region},
    )
    db.commit()
    db.refresh(account)

    return _to_status(account)


@router.get("/connect", response_model=AwsAccountStatus)
def get_connected_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(AwsAccount).filter(AwsAccount.organization_id == current_user.organization_id).first()
    return _to_status(account)


@router.delete("/connect", response_model=AwsAccountStatus)
def disconnect_aws_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(AwsAccount).filter(AwsAccount.organization_id == current_user.organization_id).first()
    if account is not None:
        db.delete(account)
        log_action(
            db,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.AWS_DISCONNECT,
            details={"aws_account_id": account.aws_account_id},
        )
        db.commit()
    return _to_status(None)
