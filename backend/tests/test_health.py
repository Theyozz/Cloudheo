from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_responses_carry_basic_security_headers():
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_dead_ad_hoc_scan_endpoints_are_removed():
    """These used to accept an arbitrary role_arn from any authenticated user
    with no check that it belonged to their own organization — a cross-tenant
    data read via Cloudheo's own AssumeRole trust. Unused by the frontend
    (the real flow is /aws/connect + /dashboard/summary), so removed rather
    than patched."""
    assert client.post("/aws/test-connection", json={}).status_code == 404
    assert client.post("/aws/costs", json={}).status_code == 404
    assert client.post("/aws/resources", json={}).status_code == 404
    assert client.post("/finops/recommendations", json={}).status_code == 404
