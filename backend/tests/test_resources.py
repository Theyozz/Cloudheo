import os

import boto3
from moto import mock_aws

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from app.services.aws import ebs, ec2, rds  # noqa: E402
from app.services.aws.cloudwatch import get_ec2_cpu_utilization  # noqa: E402

REGION = "eu-west-1"


@mock_aws
def test_list_instances_returns_launched_instance():
    client = boto3.client("ec2", region_name=REGION)
    image_id = client.describe_images()["Images"][0]["ImageId"]
    client.run_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.micro",
        TagSpecifications=[{"ResourceType": "instance", "Tags": [{"Key": "env", "Value": "dev"}]}],
    )

    session = boto3.Session(region_name=REGION)
    instances = ec2.list_instances(session, REGION)

    assert len(instances) == 1
    assert instances[0]["instance_type"] == "t3.micro"
    assert instances[0]["tags"] == {"env": "dev"}


@mock_aws
def test_list_volumes_detects_unattached():
    client = boto3.client("ec2", region_name=REGION)
    client.create_volume(Size=20, AvailabilityZone=f"{REGION}a")

    session = boto3.Session(region_name=REGION)
    volumes = ebs.list_volumes(session, REGION)

    assert len(volumes) == 1
    assert volumes[0]["size_gb"] == 20
    assert volumes[0]["attached"] is False


@mock_aws
def test_list_rds_instances():
    client = boto3.client("rds", region_name=REGION)
    client.create_db_instance(
        DBInstanceIdentifier="test-db",
        DBInstanceClass="db.t3.micro",
        Engine="postgres",
        MasterUsername="admin",
        MasterUserPassword="password123",
        AllocatedStorage=20,
    )

    session = boto3.Session(region_name=REGION)
    instances = rds.list_instances(session, REGION)

    assert len(instances) == 1
    assert instances[0]["db_instance_id"] == "test-db"
    assert instances[0]["engine"] == "postgres"


@mock_aws
def test_cpu_utilization_returns_none_without_data():
    session = boto3.Session(region_name=REGION)
    result = get_ec2_cpu_utilization(session, REGION, "i-doesnotexist")

    assert result is None
