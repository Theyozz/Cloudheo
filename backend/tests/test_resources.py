import os

import boto3
from moto import mock_aws

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from app.services.aws import ebs, ec2, rds, snapshots  # noqa: E402
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
    client.create_volume(Size=20, AvailabilityZone=f"{REGION}a", VolumeType="gp2")

    session = boto3.Session(region_name=REGION)
    volumes = ebs.list_volumes(session, REGION)

    assert len(volumes) == 1
    assert volumes[0]["size_gb"] == 20
    assert volumes[0]["volume_type"] == "gp2"
    assert volumes[0]["attached"] is False
    assert volumes[0]["attached_instance_id"] is None


@mock_aws
def test_list_volumes_includes_attached_instance_id():
    client = boto3.client("ec2", region_name=REGION)
    image_id = client.describe_images()["Images"][0]["ImageId"]
    instance = client.run_instances(ImageId=image_id, MinCount=1, MaxCount=1, InstanceType="t3.micro")[
        "Instances"
    ][0]
    volume = client.create_volume(Size=10, AvailabilityZone=f"{REGION}a")
    client.attach_volume(VolumeId=volume["VolumeId"], InstanceId=instance["InstanceId"], Device="/dev/sdf")

    session = boto3.Session(region_name=REGION)
    volumes = ebs.list_volumes(session, REGION)

    attached = next(v for v in volumes if v["volume_id"] == volume["VolumeId"])
    assert attached["attached"] is True
    assert attached["attached_instance_id"] == instance["InstanceId"]


@mock_aws
def test_list_elastic_ips_detects_unassociated():
    client = boto3.client("ec2", region_name=REGION)
    client.allocate_address(Domain="vpc")

    session = boto3.Session(region_name=REGION)
    elastic_ips = ec2.list_elastic_ips(session, REGION)

    assert len(elastic_ips) == 1
    assert elastic_ips[0]["associated"] is False


@mock_aws
def test_list_elastic_ips_detects_associated():
    client = boto3.client("ec2", region_name=REGION)
    image_id = client.describe_images()["Images"][0]["ImageId"]
    instance = client.run_instances(ImageId=image_id, MinCount=1, MaxCount=1, InstanceType="t3.micro")[
        "Instances"
    ][0]
    address = client.allocate_address(Domain="vpc")
    client.associate_address(InstanceId=instance["InstanceId"], AllocationId=address["AllocationId"])

    session = boto3.Session(region_name=REGION)
    elastic_ips = ec2.list_elastic_ips(session, REGION)

    assert len(elastic_ips) == 1
    assert elastic_ips[0]["associated"] is True


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


@mock_aws
def test_list_snapshots_maps_fields_correctly():
    # moto's describe_snapshots ignores the OwnerIds=["self"] filter and also
    # returns ~479 fake snapshots it auto-generates for its built-in AMI
    # catalog (verified against real AWS: the real API filters correctly).
    # So this looks up our own snapshot by ID instead of asserting a count.
    client = boto3.client("ec2", region_name=REGION)
    volume = client.create_volume(Size=30, AvailabilityZone=f"{REGION}a")
    snap = client.create_snapshot(VolumeId=volume["VolumeId"], TagSpecifications=[
        {"ResourceType": "snapshot", "Tags": [{"Key": "Name", "Value": "my-snapshot"}]}
    ])

    session = boto3.Session(region_name=REGION)
    results = snapshots.list_snapshots(session, REGION)

    mine = next(s for s in results if s["snapshot_id"] == snap["SnapshotId"])
    assert mine["volume_id"] == volume["VolumeId"]
    assert mine["volume_size_gb"] == 30
    assert mine["tags"] == {"Name": "my-snapshot"}
