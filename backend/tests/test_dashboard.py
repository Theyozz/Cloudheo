from unittest.mock import patch

from moto import mock_aws

from tests.conftest import create_customer_role

# moto's Cost Explorer backend doesn't implement get_savings_plans_coverage
# (see tests/test_cost_explorer.py), so it's patched directly wherever a test
# exercises the full /dashboard/summary endpoint under @mock_aws.
NO_SAVINGS_PLAN_GAP = {"on_demand_cost": 0.0, "covered_cost": 0.0, "total_cost": 0.0, "coverage_percentage": 0.0}


@mock_aws
def test_dashboard_summary_without_connection(client):
    resp = client.get("/dashboard/summary")

    assert resp.status_code == 200
    body = resp.json()
    assert body["connected"] is False
    assert body["monthly_spend"] == 0.0
    assert body["top_recommendations"] == []


@mock_aws
@patch("app.api.dashboard.get_savings_plans_coverage", return_value=NO_SAVINGS_PLAN_GAP)
def test_dashboard_summary_after_connecting(mock_coverage, client):
    role_arn = create_customer_role()
    client.post("/aws/connect", json={"role_arn": role_arn, "region": "eu-west-3"})

    resp = client.get("/dashboard/summary")

    assert resp.status_code == 200
    body = resp.json()
    assert body["connected"] is True
    assert body["monthly_spend"] == 0.0
    # Not asserting recommendations_count/savings_by_category here: moto's
    # describe_snapshots ignores the OwnerIds filter and injects ~479 fake
    # snapshots (see tests/test_resources.py), which would make this count
    # an artifact of the mock rather than a real assertion. The FinOps rules
    # themselves are covered with precise, moto-free tests in
    # tests/test_finops_rules.py.
