"""AWS Cost Explorer integration.

Cost Explorer is a global AWS service, but its API must always be called
against the us-east-1 endpoint regardless of where the account's resources
actually live.
"""

from datetime import date, timedelta

import boto3

COST_EXPLORER_REGION = "us-east-1"


def default_date_range(days: int = 30) -> tuple[str, str]:
    """Return (start, end) as YYYY-MM-DD strings. End is exclusive, as required by Cost Explorer."""
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def get_cost_by_service(session: boto3.Session, start_date: str, end_date: str) -> list[dict]:
    """Total unblended cost per AWS service over the given period."""
    client = session.client("ce", region_name=COST_EXPLORER_REGION)
    response = client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    totals_by_service: dict[str, float] = {}
    for period in response["ResultsByTime"]:
        for group in period["Groups"]:
            service = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            totals_by_service[service] = totals_by_service.get(service, 0.0) + amount

    return [
        {"service": service, "amount": round(amount, 2)}
        for service, amount in sorted(totals_by_service.items(), key=lambda kv: kv[1], reverse=True)
        if amount > 0
    ]
