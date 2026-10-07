import json
import os

import boto3
from moto import mock_aws

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from app.services.aws.cost_explorer import default_date_range, get_cost_by_service  # noqa: E402


def test_default_date_range_is_thirty_days():
    start, end = default_date_range()
    assert start < end


@mock_aws
def test_get_cost_by_service_returns_list():
    iam = boto3.client("iam", region_name="eu-west-3")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"AWS": "*"}, "Action": "sts:AssumeRole"}
        ],
    }
    iam.create_role(RoleName="CloudheoReadOnlyRole", AssumeRolePolicyDocument=json.dumps(trust_policy))

    session = boto3.Session(region_name="eu-west-3")
    start, end = default_date_range()

    result = get_cost_by_service(session, start, end)

    assert isinstance(result, list)
