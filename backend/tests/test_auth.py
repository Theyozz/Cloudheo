EMAIL = "admin@cloudheo.dev"
PASSWORD = "supersecret123"


def test_status_reports_unregistered_initially(unauthenticated_client):
    resp = unauthenticated_client.get("/auth/status")
    assert resp.status_code == 200
    assert resp.json()["registered"] is False


def test_register_then_status_reports_registered(unauthenticated_client):
    unauthenticated_client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})

    resp = unauthenticated_client.get("/auth/status")
    assert resp.json()["registered"] is True


def test_register_returns_usable_token(unauthenticated_client):
    resp = unauthenticated_client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 201
    token = resp.json()["access_token"]

    me = unauthenticated_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == EMAIL


def test_second_registration_is_rejected(unauthenticated_client):
    unauthenticated_client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})

    resp = unauthenticated_client.post("/auth/register", json={"email": "other@cloudheo.dev", "password": PASSWORD})
    assert resp.status_code == 403


def test_login_with_correct_password_succeeds(unauthenticated_client):
    unauthenticated_client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})

    resp = unauthenticated_client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_is_rejected(unauthenticated_client):
    unauthenticated_client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})

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
    resp = unauthenticated_client.post("/auth/register", json={"email": EMAIL, "password": "short"})
    assert resp.status_code == 422
