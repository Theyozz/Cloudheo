PASSWORD = "supersecret123"


def test_login_is_rate_limited_after_too_many_attempts(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Acme", "email": "a@cloudheo.dev", "password": PASSWORD},
    )

    for _ in range(10):
        resp = unauthenticated_client.post("/auth/login", json={"email": "a@cloudheo.dev", "password": "wrong"})
        assert resp.status_code == 401

    resp = unauthenticated_client.post("/auth/login", json={"email": "a@cloudheo.dev", "password": PASSWORD})
    assert resp.status_code == 429


def test_register_is_rate_limited_after_too_many_attempts(unauthenticated_client):
    for i in range(5):
        resp = unauthenticated_client.post(
            "/auth/register",
            json={"organization_name": "Acme", "email": f"user{i}@cloudheo.dev", "password": PASSWORD},
        )
        assert resp.status_code == 201

    resp = unauthenticated_client.post(
        "/auth/register",
        json={"organization_name": "Acme", "email": "one-too-many@cloudheo.dev", "password": PASSWORD},
    )
    assert resp.status_code == 429
