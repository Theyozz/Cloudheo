from app.services.email.stub_provider import SENT_EMAILS

VALID_PAYLOAD = {
    "name": "Jane Doe",
    "company_name": "Acme Inc",
    "work_email": "jane@acme.com",
    "monthly_spend_range": "10k_50k",
    "message": "We're mostly interested in RDS savings.",
}


def test_valid_lead_is_persisted_and_notified(unauthenticated_client):
    resp = unauthenticated_client.post("/audit-leads", json=VALID_PAYLOAD)

    assert resp.status_code == 201
    assert len(SENT_EMAILS) == 1
    assert SENT_EMAILS[0]["work_email"] == "jane@acme.com"
    assert SENT_EMAILS[0]["company_name"] == "Acme Inc"


def test_lead_without_optional_message_is_accepted(unauthenticated_client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "message"}
    resp = unauthenticated_client.post("/audit-leads", json=payload)

    assert resp.status_code == 201
    assert len(SENT_EMAILS) == 1
    assert SENT_EMAILS[0]["message"] is None


def test_invalid_email_is_rejected(unauthenticated_client):
    payload = {**VALID_PAYLOAD, "work_email": "not-an-email"}
    resp = unauthenticated_client.post("/audit-leads", json=payload)

    assert resp.status_code == 422
    assert SENT_EMAILS == []


def test_invalid_spend_range_is_rejected(unauthenticated_client):
    payload = {**VALID_PAYLOAD, "monthly_spend_range": "a_million_dollars"}
    resp = unauthenticated_client.post("/audit-leads", json=payload)

    assert resp.status_code == 422


def test_missing_required_field_is_rejected(unauthenticated_client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "company_name"}
    resp = unauthenticated_client.post("/audit-leads", json=payload)

    assert resp.status_code == 422


def test_lead_rate_limit_is_enforced(unauthenticated_client):
    for _ in range(5):
        resp = unauthenticated_client.post("/audit-leads", json=VALID_PAYLOAD)
        assert resp.status_code == 201

    resp = unauthenticated_client.post("/audit-leads", json=VALID_PAYLOAD)
    assert resp.status_code == 429
