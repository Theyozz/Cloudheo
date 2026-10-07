"""EBS volume inventory."""

import boto3


def list_volumes(session: boto3.Session, region: str) -> list[dict]:
    client = session.client("ec2", region_name=region)
    paginator = client.get_paginator("describe_volumes")

    volumes = []
    for page in paginator.paginate():
        for volume in page["Volumes"]:
            tags = {t["Key"]: t["Value"] for t in volume.get("Tags", [])}
            attachments = volume.get("Attachments", [])
            volumes.append(
                {
                    "volume_id": volume["VolumeId"],
                    "size_gb": volume["Size"],
                    "state": volume["State"],
                    "attached": len(attachments) > 0,
                    # A volume normally has at most one attachment (Multi-Attach
                    # is a rare opt-in feature); take the first one.
                    "attached_instance_id": attachments[0]["InstanceId"] if attachments else None,
                    "region": region,
                    "tags": tags,
                }
            )
    return volumes
