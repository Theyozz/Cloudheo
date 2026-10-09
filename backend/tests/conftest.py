import json
import os

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

import boto3
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.main import app
from app.services.ai import get_ai_provider
from app.services.ai.stub_provider import StubExplanationProvider

TEST_ORG_NAME = "Test Org"
TEST_USER_EMAIL = "test@cloudheo.dev"
TEST_USER_PASSWORD = "testpassword123"


def _new_test_client() -> TestClient:
    """A TestClient backed by its own isolated in-memory SQLite DB, so tests
    never touch the real Postgres database and never share state."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Never call the real Claude API from automated tests — see
    # tests/test_ai.py for the rationale (speed, determinism, no required key).
    app.dependency_overrides[get_ai_provider] = lambda: StubExplanationProvider()
    return TestClient(app)


@pytest.fixture()
def unauthenticated_client():
    """For tests of the auth flow itself (register/login/missing token)."""
    test_client = _new_test_client()
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client():
    """A pre-authenticated TestClient — the default for tests of protected
    routes, which is almost everything. Registers and logs in one test user,
    then attaches its token to every request."""
    test_client = _new_test_client()
    test_client.post(
        "/auth/register",
        json={"organization_name": TEST_ORG_NAME, "email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    login_resp = test_client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
    token = login_resp.json()["access_token"]
    test_client.headers.update({"Authorization": f"Bearer {token}"})

    yield test_client
    app.dependency_overrides.clear()


def create_customer_role(region: str = "eu-west-3", role_name: str = "CloudheoReadOnlyRole") -> str:
    """Create a mocked read-only role and return its ARN. Must run inside an
    active @mock_aws context."""
    iam = boto3.client("iam", region_name=region)
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Principal": {"AWS": "*"}, "Action": "sts:AssumeRole"}],
    }
    role = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy))
    return role["Role"]["Arn"]
