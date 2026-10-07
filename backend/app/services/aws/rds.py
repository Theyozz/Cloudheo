"""RDS instance inventory."""

import boto3


def list_instances(session: boto3.Session, region: str) -> list[dict]:
    client = session.client("rds", region_name=region)
    paginator = client.get_paginator("describe_db_instances")

    instances = []
    for page in paginator.paginate():
        for db in page["DBInstances"]:
            tags = {t["Key"]: t["Value"] for t in db.get("TagList", [])}
            instances.append(
                {
                    "db_instance_id": db["DBInstanceIdentifier"],
                    "engine": db["Engine"],
                    "instance_class": db["DBInstanceClass"],
                    "status": db["DBInstanceStatus"],
                    "multi_az": db.get("MultiAZ", False),
                    "region": region,
                    "tags": tags,
                }
            )
    return instances
