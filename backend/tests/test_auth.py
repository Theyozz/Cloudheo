ORG_NAME = "Acme Inc"
EMAIL = "admin@cloudheo.dev"
PASSWORD = "supersecret123"


def test_register_returns_usable_token(unauthenticated_client):
    resp = unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]

    me = unauthenticated_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == EMAIL
    assert me.json()["organization_id"]
    assert me.json()["organization_name"] == ORG_NAME


def test_second_organization_can_register(unauthenticated_client):
    """Registration stays open after the first signup — a second customer
    must be able to create their own organization."""
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )

    resp = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Other Co", "email": "other@cloudheo.dev", "password": PASSWORD},
    )
    assert resp.status_code == 201


def test_duplicate_email_is_rejected(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )

    resp = unauthenticated_client.post(
        "/auth/register", json={"organization_name": "Other Co", "email": EMAIL, "password": PASSWORD}
    )
    assert resp.status_code == 409


def test_login_with_correct_password_succeeds(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )

    resp = unauthenticated_client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_is_rejected(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )

    resp = unauthenticated_client.post("/auth/login", json={"email": EMAIL, "password": "wrongpassword"})
    assert resp.status_code == 401


def test_login_with_unknown_email_is_rejected(unauthenticated_client):
    resp = unauthenticated_client.post("/auth/login", json={"email": "nobody@cloudheo.dev", "password": PASSWORD})
    assert resp.status_code == 401


def test_protected_route_without_token_is_rejected(unauthenticated_client):
    resp = unauthenticated_client.get("/aws/connect")
    assert resp.status_code == 401


def test_protected_route_with_invalid_token_is_rejected(unauthenticated_client):
    resp = unauthenticated_client.get("/aws/connect", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_protected_route_with_valid_token_succeeds(client):
    # The `client` fixture is already authenticated.
    resp = client.get("/aws/connect")
    assert resp.status_code == 200


def test_short_password_is_rejected(unauthenticated_client):
    resp = unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": "short"}
    )
    assert resp.status_code == 422
