"""EBS snapshot inventory."""

import boto3


def list_snapshots(session: boto3.Session, region: str) -> list[dict]:
    client = session.client("ec2", region_name=region)
    paginator = client.get_paginator("describe_snapshots")

    snapshots = []
    for page in paginator.paginate(OwnerIds=["self"]):
        for snapshot in page["Snapshots"]:
            tags = {t["Key"]: t["Value"] for t in snapshot.get("Tags", [])}
            snapshots.append(
                {
                    "snapshot_id": snapshot["SnapshotId"],
                    # VolumeId is kept even if the source volume was since
                    # deleted — AWS does not clear it, which is exactly what
                    # lets us detect orphaned snapshots.
                    "volume_id": snapshot["VolumeId"],
                    "volume_size_gb": snapshot["VolumeSize"],
                    "state": snapshot["State"],
                    "start_time": snapshot["StartTime"].isoformat(),
                    "region": region,
                    "tags": tags,
                }
            )
    return snapshots
