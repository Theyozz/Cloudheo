"""AssumeRole into a customer AWS account.

Cloudheo never stores or uses a customer's permanent credentials. Instead,
the customer creates a read-only IAM role (``CloudheoReadOnlyRole``) in
their own account that trusts Cloudheo's AWS account. Cloudheo's backend
then calls ``sts:AssumeRole`` to obtain short-lived, read-only credentials
scoped to that customer's account.
"""

from dataclasses import dataclass
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings


class AssumeRoleError(Exception):
    """Raised when Cloudheo fails to assume a customer's IAM role."""


@dataclass
class AssumedCredentials:
    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: datetime
    assumed_role_arn: str


def _sts_client():
    settings = get_settings()
    return boto3.client(
        "sts",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def assume_role(
    role_arn: str,
    external_id: str | None = None,
    session_name: str = "cloudheo-scan",
) -> AssumedCredentials:
    """Assume a customer's read-only IAM role and return temporary credentials."""
    kwargs = {
        "RoleArn": role_arn,
        "RoleSessionName": session_name,
        "DurationSeconds": 3600,
    }
    if external_id:
        kwargs["ExternalId"] = external_id

    try:
        response = _sts_client().assume_role(**kwargs)
    except ClientError as exc:
        raise AssumeRoleError(str(exc)) from exc

    creds = response["Credentials"]
    return AssumedCredentials(
        access_key_id=creds["AccessKeyId"],
        secret_access_key=creds["SecretAccessKey"],
        session_token=creds["SessionToken"],
        expiration=creds["Expiration"],
        assumed_role_arn=response["AssumedRoleUser"]["Arn"],
    )


def session_from_assumed_credentials(creds: AssumedCredentials) -> boto3.Session:
    """Build a boto3 Session scoped to the assumed (customer) credentials."""
    settings = get_settings()
    return boto3.Session(
        aws_access_key_id=creds.access_key_id,
        aws_secret_access_key=creds.secret_access_key,
        aws_session_token=creds.session_token,
        region_name=settings.AWS_REGION,
    )


def get_caller_identity(creds: AssumedCredentials) -> dict:
    """Confirm who we are once impersonating the customer role.

    Used to validate the AssumeRole flow end-to-end without touching any
    real customer data.
    """
    session = session_from_assumed_credentials(creds)
    return session.client("sts").get_caller_identity()
