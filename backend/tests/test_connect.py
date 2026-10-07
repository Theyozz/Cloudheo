from moto import mock_aws

from tests.conftest import create_customer_role


@mock_aws
def test_connect_then_status_then_disconnect(client):
    role_arn = create_customer_role()

    connect_resp = client.post("/aws/connect", json={"role_arn": role_arn})
    assert connect_resp.status_code == 200
    body = connect_resp.json()
    assert body["connected"] is True
    assert body["role_arn"] == role_arn

    status_resp = client.get("/aws/connect")
    assert status_resp.json()["connected"] is True

    disconnect_resp = client.delete("/aws/connect")
    assert disconnect_resp.json()["connected"] is False

    status_resp_after = client.get("/aws/connect")
    assert status_resp_after.json()["connected"] is False


@mock_aws
def test_connecting_twice_replaces_previous_account(client):
    first_role_arn = create_customer_role()
    client.post("/aws/connect", json={"role_arn": first_role_arn})

    second_role_arn = create_customer_role(role_name="CloudheoReadOnlyRole2")
    client.post("/aws/connect", json={"role_arn": second_role_arn})

    status = client.get("/aws/connect").json()
    assert status["role_arn"] == second_role_arn
