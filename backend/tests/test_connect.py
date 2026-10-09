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


@mock_aws
def test_connected_account_is_not_visible_to_another_organization(unauthenticated_client):
    org_a = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Org A", "email": "a@cloudheo.dev", "password": "supersecret123"},
    ).json()
    org_b = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Org B", "email": "b@cloudheo.dev", "password": "supersecret123"},
    ).json()
    headers_a = {"Authorization": f"Bearer {org_a['access_token']}"}
    headers_b = {"Authorization": f"Bearer {org_b['access_token']}"}

    role_arn = create_customer_role()
    unauthenticated_client.post("/aws/connect", json={"role_arn": role_arn}, headers=headers_a)

    status_a = unauthenticated_client.get("/aws/connect", headers=headers_a).json()
    status_b = unauthenticated_client.get("/aws/connect", headers=headers_b).json()
    assert status_a["connected"] is True
    assert status_b["connected"] is False
