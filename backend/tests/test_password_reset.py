"""The `client`/`unauthenticated_client` fixtures override get_email_provider
with a stub (see conftest.py) — these tests never call the real Resend API.
SENT_EMAILS lets us recover the reset token from the captured reset_url to
drive the rest of the flow without ever seeing it over the network.
"""

from urllib.parse import parse_qs, urlparse

from app.services.email.stub_provider import SENT_EMAILS

ORG_NAME = "Acme Inc"
EMAIL = "a@cloudheo.dev"
PASSWORD = "supersecret123"
NEW_PASSWORD = "newsupersecret456"


def _extract_token(reset_url: str) -> str:
    return parse_qs(urlparse(reset_url).query)["token"][0]


def test_forgot_password_sends_an_email_for_a_known_address(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )

    resp = unauthenticated_client.post("/auth/forgot-password", json={"email": EMAIL})
    assert resp.status_code == 200
    assert len(SENT_EMAILS) == 1
    assert SENT_EMAILS[0]["to"] == EMAIL
    assert "token=" in SENT_EMAILS[0]["reset_url"]


def test_forgot_password_gives_the_same_response_for_an_unknown_address(unauthenticated_client):
    known = unauthenticated_client.post(
        "/auth/forgot-password", json={"email": "unknown@cloudheo.dev"}
    )
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )
    registered = unauthenticated_client.post("/auth/forgot-password", json={"email": EMAIL})

    assert known.status_code == registered.status_code == 200
    assert known.json() == registered.json()
    # No email was actually sent for the unknown address.
    assert len(SENT_EMAILS) == 1


def test_reset_password_with_valid_token_changes_the_password(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )
    unauthenticated_client.post("/auth/forgot-password", json={"email": EMAIL})
    token = _extract_token(SENT_EMAILS[0]["reset_url"])

    resp = unauthenticated_client.post("/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD})
    assert resp.status_code == 200

    old_login = unauthenticated_client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert old_login.status_code == 401

    new_login = unauthenticated_client.post("/auth/login", json={"email": EMAIL, "password": NEW_PASSWORD})
    assert new_login.status_code == 200


def test_reset_password_rejects_an_invalid_token(unauthenticated_client):
    resp = unauthenticated_client.post(
        "/auth/reset-password", json={"token": "not-a-real-token", "new_password": NEW_PASSWORD}
    )
    assert resp.status_code == 400


def test_reset_password_token_is_single_use(unauthenticated_client):
    unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )
    unauthenticated_client.post("/auth/forgot-password", json={"email": EMAIL})
    token = _extract_token(SENT_EMAILS[0]["reset_url"])

    first = unauthenticated_client.post("/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD})
    second = unauthenticated_client.post(
        "/auth/reset-password", json={"token": token, "new_password": "yet-another-password"}
    )
    assert first.status_code == 200
    assert second.status_code == 400


def test_reset_password_invalidates_existing_sessions(unauthenticated_client):
    register_resp = unauthenticated_client.post(
        "/auth/register", json={"organization_name": ORG_NAME, "email": EMAIL, "password": PASSWORD}
    )
    old_token = register_resp.json()["access_token"]
    old_headers = {"Authorization": f"Bearer {old_token}"}

    # The token works before the reset.
    assert unauthenticated_client.get("/auth/me", headers=old_headers).status_code == 200

    unauthenticated_client.post("/auth/forgot-password", json={"email": EMAIL})
    reset_token = _extract_token(SENT_EMAILS[0]["reset_url"])
    unauthenticated_client.post("/auth/reset-password", json={"token": reset_token, "new_password": NEW_PASSWORD})

    resp = unauthenticated_client.get("/auth/me", headers=old_headers)
    assert resp.status_code == 401
