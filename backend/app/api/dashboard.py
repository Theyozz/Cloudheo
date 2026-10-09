from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.models.aws_account import AwsAccount
from app.models.user import User
from app.schemas.dashboard import CategorySaving, DashboardSummaryResponse
from app.services.aws import ec2
from app.services.aws.cost_explorer import default_date_range, get_cost_by_service
from app.services.aws.inventory import fetch_inventory
from app.services.aws.sts import AssumeRoleError, assume_role, session_from_assumed_credentials
from app.services.finops.rules import evaluate_all

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

TOP_RECOMMENDATIONS_LIMIT = 10


@router.get("/summary", response_model=DashboardSummaryResponse)
@limiter.limit("30/minute")
def get_dashboard_summary(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """One-call summary for the dashboard: spend, potential savings, and
    top recommendations for the organization's currently connected AWS
    account."""
    account = db.query(AwsAccount).filter(AwsAccount.organization_id == current_user.organization_id).first()
    if account is None:
        return DashboardSummaryResponse(connected=False)

    try:
        creds = assume_role(role_arn=account.role_arn, external_id=account.external_id)
        session = session_from_assumed_credentials(creds)

        start_date, end_date = default_date_range()
        by_service = get_cost_by_service(session, start_date, end_date)
        monthly_spend = round(sum(item["amount"] for item in by_service), 2)

        regions = [account.region] if account.region else ec2.list_regions(session)
        inventory = fetch_inventory(session, regions)
        recommendations = evaluate_all(
            inventory["ec2_instances"],
            inventory["ebs_volumes"],
            inventory["rds_instances"],
            inventory["ebs_snapshots"],
        )
    except (AssumeRoleError, ClientError):
        # The account was connected successfully before; a transient AWS
        # error shouldn't take the whole dashboard down — show what we can.
        return DashboardSummaryResponse(connected=True, aws_account_id=account.aws_account_id)

    potential_savings = round(sum(r.estimated_savings for r in recommendations), 2)
    savings_percent = round((potential_savings / monthly_spend) * 100, 1) if monthly_spend else 0.0

    savings_by_type: dict[str, float] = {}
    for rec in recommendations:
        savings_by_type[rec.resource_type] = savings_by_type.get(rec.resource_type, 0.0) + rec.estimated_savings
    savings_by_category = [
        CategorySaving(category=resource_type, amount=round(amount, 2))
        for resource_type, amount in sorted(savings_by_type.items(), key=lambda kv: kv[1], reverse=True)
    ]

    return DashboardSummaryResponse(
        connected=True,
        aws_account_id=account.aws_account_id,
        monthly_spend=monthly_spend,
        potential_savings=potential_savings,
        savings_percent=savings_percent,
        recommendations_count=len(recommendations),
        savings_by_category=savings_by_category,
        top_recommendations=recommendations[:TOP_RECOMMENDATIONS_LIMIT],
    )
