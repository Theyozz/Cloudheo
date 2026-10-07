"""The `client` fixture overrides get_ai_provider with a stub (see
conftest.py) — these tests never call the real Claude API. That's
deliberate: LLM output isn't deterministic, a real call takes 1-3s, and the
suite must run without an Anthropic API key. The stub provider itself is
trivial (one f-string); the real ClaudeExplanationProvider is verified
manually against the live API instead of in the automated suite.
"""

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


def test_explain_requires_auth(unauthenticated_client):
    resp = unauthenticated_client.post("/ai/explain", json={"recommendation": SAMPLE_RECOMMENDATION})
    assert resp.status_code == 401


def test_explain_returns_text(client):
    resp = client.post("/ai/explain", json={"recommendation": SAMPLE_RECOMMENDATION})

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["explanation"], str)
    assert len(body["explanation"]) > 0


def test_explain_rejects_malformed_recommendation(client):
    resp = client.post("/ai/explain", json={"recommendation": {"resource_id": "i-0abc123"}})
    assert resp.status_code == 422
