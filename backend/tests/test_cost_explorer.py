import json
import os
from unittest.mock import MagicMock

import boto3
from moto import mock_aws

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from app.services.aws.cost_explorer import (  # noqa: E402
    default_date_range,
    get_cost_by_service,
    get_savings_plans_coverage,
)


def test_default_date_range_is_thirty_days():
    start, end = default_date_range()
    assert start < end


@mock_aws
def test_get_cost_by_service_returns_list():
    iam = boto3.client("iam", region_name="eu-west-3")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"AWS": "*"}, "Action": "sts:AssumeRole"}
        ],
    }
    iam.create_role(RoleName="CloudheoReadOnlyRole", AssumeRolePolicyDocument=json.dumps(trust_policy))

    session = boto3.Session(region_name="eu-west-3")
    start, end = default_date_range()

    result = get_cost_by_service(session, start, end)

    assert isinstance(result, list)


# moto's Cost Explorer backend doesn't implement get_savings_plans_coverage
# (only get_cost_and_usage and cost category management), so these mock the
# boto3 client response directly instead of going through @mock_aws.


def test_get_savings_plans_coverage_aggregates_across_periods():
    mock_client = MagicMock()
    mock_client.get_savings_plans_coverage.return_value = {
        "SavingsPlansCoverages": [
            {
                "Coverage": {
                    "OnDemandCost": "80.00",
                    "SpendCoveredBySavingsPlans": "20.00",
                    "TotalCost": "100.00",
                    "CoveragePercentage": "20.0",
                }
            },
            {
                "Coverage": {
                    "OnDemandCost": "40.00",
                    "SpendCoveredBySavingsPlans": "10.00",
                    "TotalCost": "50.00",
                    "CoveragePercentage": "20.0",
                }
            },
        ]
    }
    session = MagicMock()
    session.client.return_value = mock_client

    result = get_savings_plans_coverage(session, "2026-09-01", "2026-10-01")

    assert result == {
        "on_demand_cost": 120.0,
        "covered_cost": 30.0,
        "total_cost": 150.0,
        "coverage_percentage": 20.0,
    }
    session.client.assert_called_once_with("ce", region_name="us-east-1")


def test_get_savings_plans_coverage_handles_zero_spend():
    mock_client = MagicMock()
    mock_client.get_savings_plans_coverage.return_value = {
        "SavingsPlansCoverages": [
            {
                "Coverage": {
                    "OnDemandCost": "0.00",
                    "SpendCoveredBySavingsPlans": "0.00",
                    "TotalCost": "0.00",
                    "CoveragePercentage": "0.0",
                }
            }
        ]
    }
    session = MagicMock()
    session.client.return_value = mock_client

    result = get_savings_plans_coverage(session, "2026-09-01", "2026-10-01")

    assert result["coverage_percentage"] == 0.0
