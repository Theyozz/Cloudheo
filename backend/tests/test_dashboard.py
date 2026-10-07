from moto import mock_aws

from tests.conftest import create_customer_role


@mock_aws
def test_dashboard_summary_without_connection(client):
    resp = client.get("/dashboard/summary")

    assert resp.status_code == 200
    body = resp.json()
    assert body["connected"] is False
    assert body["monthly_spend"] == 0.0
    assert body["top_recommendations"] == []


@mock_aws
def test_dashboard_summary_after_connecting(client):
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
