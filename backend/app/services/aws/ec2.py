"""EC2 instance inventory."""

import boto3


def list_regions(session: boto3.Session) -> list[str]:
    """Regions actually enabled for this account (not every AWS region)."""
    client = session.client("ec2", region_name="us-east-1")
    response = client.describe_regions(AllRegions=False)
    return [r["RegionName"] for r in response["Regions"]]


def list_instances(session: boto3.Session, region: str) -> list[dict]:
    client = session.client("ec2", region_name=region)
    paginator = client.get_paginator("describe_instances")

    instances = []
    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
                instances.append(
                    {
                        "instance_id": instance["InstanceId"],
                        "instance_type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                        "region": region,
                        "tags": tags,
                    }
                )
    return instances


def list_elastic_ips(session: boto3.Session, region: str) -> list[dict]:
    client = session.client("ec2", region_name=region)
    response = client.describe_addresses()

    elastic_ips = []
    for address in response["Addresses"]:
        tags = {t["Key"]: t["Value"] for t in address.get("Tags", [])}
        elastic_ips.append(
            {
                "allocation_id": address.get("AllocationId", address["PublicIp"]),
                "public_ip": address["PublicIp"],
                "associated": "AssociationId" in address,
                "region": region,
                "tags": tags,
            }
        )
    return elastic_ips
