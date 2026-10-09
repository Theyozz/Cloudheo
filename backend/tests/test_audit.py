from moto import mock_aws

from tests.conftest import create_customer_role


def test_register_and_login_are_logged(unauthenticated_client):
    register_resp = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Acme Inc", "email": "a@cloudheo.dev", "password": "supersecret123"},
    )
    token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    unauthenticated_client.post("/auth/login", json={"email": "a@cloudheo.dev", "password": "supersecret123"})

    logs = unauthenticated_client.get("/audit-logs", headers=headers).json()
    actions = [entry["action"] for entry in logs]
    assert "auth.register" in actions
    assert "auth.login" in actions


@mock_aws
def test_aws_connect_and_disconnect_are_logged(client):
    role_arn = create_customer_role()
    client.post("/aws/connect", json={"role_arn": role_arn})
    client.delete("/aws/connect")

    logs = client.get("/audit-logs").json()
    actions = [entry["action"] for entry in logs]
    assert "aws.connect" in actions
    assert "aws.disconnect" in actions

    connect_entry = next(entry for entry in logs if entry["action"] == "aws.connect")
    assert connect_entry["details"]["role_arn"] == role_arn


def test_disconnect_without_a_connected_account_is_not_logged(client):
    client.delete("/aws/connect")

    logs = client.get("/audit-logs").json()
    assert "aws.disconnect" not in [entry["action"] for entry in logs]


def test_audit_logs_are_not_visible_to_another_organization(unauthenticated_client):
    org_a = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Org A", "email": "a@cloudheo.dev", "password": "supersecret123"},
    ).json()
    org_b = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Org B", "email": "b@cloudheo.dev", "password": "supersecret123"},
    ).json()

    logs_b = unauthenticated_client.get(
        "/audit-logs", headers={"Authorization": f"Bearer {org_b['access_token']}"}
    ).json()
    assert all(entry["details"].get("email") != "a@cloudheo.dev" for entry in logs_b if entry["details"])


def test_audit_logs_requires_auth(unauthenticated_client):
    resp = unauthenticated_client.get("/audit-logs")
    assert resp.status_code == 401
