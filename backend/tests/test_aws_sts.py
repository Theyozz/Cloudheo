import json
import os

import boto3
from moto import mock_aws

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from app.services.aws.sts import assume_role, get_caller_identity  # noqa: E402


def _create_customer_role() -> str:
    iam = boto3.client("iam", region_name="eu-west-3")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"AWS": "*"}, "Action": "sts:AssumeRole"}
        ],
    }
    role = iam.create_role(
        RoleName="CloudheoReadOnlyRole",
        AssumeRolePolicyDocument=json.dumps(trust_policy),
    )
    return role["Role"]["Arn"]


@mock_aws
def test_assume_role_returns_temporary_credentials():
    role_arn = _create_customer_role()

    creds = assume_role(role_arn=role_arn, session_name="test-scan")

    assert creds.access_key_id
    assert creds.secret_access_key
    assert creds.session_token
    assert "CloudheoReadOnlyRole" in creds.assumed_role_arn


@mock_aws
def test_get_caller_identity_after_assume_role():
    role_arn = _create_customer_role()
    creds = assume_role(role_arn=role_arn, session_name="test-scan")

    identity = get_caller_identity(creds)

    assert "Account" in identity
    assert identity["Arn"] == creds.assumed_role_arn
