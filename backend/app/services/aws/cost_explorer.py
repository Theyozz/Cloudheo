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


def get_savings_plans_coverage(session: boto3.Session, start_date: str, end_date: str) -> dict:
    """Aggregate Savings Plans coverage for the given period: how much of
    compute spend is already covered by a Savings Plan vs. still paying
    full on-demand price. Used by the coverage-gap FinOps rule."""
    client = session.client("ce", region_name=COST_EXPLORER_REGION)
    response = client.get_savings_plans_coverage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
    )

    on_demand_cost = 0.0
    covered_cost = 0.0
    total_cost = 0.0
    for period in response["SavingsPlansCoverages"]:
        coverage = period["Coverage"]
        on_demand_cost += float(coverage["OnDemandCost"])
        covered_cost += float(coverage["SpendCoveredBySavingsPlans"])
        total_cost += float(coverage["TotalCost"])

    coverage_percentage = round((covered_cost / total_cost) * 100, 1) if total_cost else 0.0

    return {
        "on_demand_cost": round(on_demand_cost, 2),
        "covered_cost": round(covered_cost, 2),
        "total_cost": round(total_cost, 2),
        "coverage_percentage": coverage_percentage,
    }
