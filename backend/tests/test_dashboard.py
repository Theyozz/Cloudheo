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
    assert body["recommendations_count"] == 0
    assert body["savings_by_category"] == []
