PASSWORD = "supersecret123"

SAMPLE_RECOMMENDATION = {
    "resource_id": "i-0abc123",
    "resource_type": "EC2",
    "category": "RIGHTSIZING",
    "current_cost": 112.0,
    "estimated_optimized_cost": 54.0,
    "estimated_savings": 58.0,
    "risk": "LOW",
    "confidence": 0.94,
    "title": "Downsize i-0abc123 from t3.large to t3.medium",
    "description": "Average CPU is 8.2% and max CPU is 27.0% over the observed period.",
}


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


def test_ai_explain_is_rate_limited_after_too_many_calls(client):
    for _ in range(30):
        resp = client.post("/ai/explain", json={"recommendation": SAMPLE_RECOMMENDATION})
        assert resp.status_code == 200

    resp = client.post("/ai/explain", json={"recommendation": SAMPLE_RECOMMENDATION})
    assert resp.status_code == 429


def test_dashboard_summary_is_rate_limited_after_too_many_calls(client):
    for _ in range(30):
        resp = client.get("/dashboard/summary")
        assert resp.status_code == 200

    resp = client.get("/dashboard/summary")
    assert resp.status_code == 429


def test_forgot_password_is_rate_limited_after_too_many_calls(unauthenticated_client):
    for _ in range(5):
        resp = unauthenticated_client.post("/auth/forgot-password", json={"email": "nobody@cloudheo.dev"})
        assert resp.status_code == 200

    resp = unauthenticated_client.post("/auth/forgot-password", json={"email": "nobody@cloudheo.dev"})
    assert resp.status_code == 429


def test_reset_password_is_rate_limited_after_too_many_calls(unauthenticated_client):
    for _ in range(10):
        resp = unauthenticated_client.post(
            "/auth/reset-password", json={"token": "not-a-real-token", "new_password": PASSWORD}
        )
        assert resp.status_code == 400

    resp = unauthenticated_client.post(
        "/auth/reset-password", json={"token": "not-a-real-token", "new_password": PASSWORD}
    )
    assert resp.status_code == 429
