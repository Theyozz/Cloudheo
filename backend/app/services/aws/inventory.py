"""Combined AWS resource inventory — EC2 + EBS + RDS + EBS snapshots +
Elastic IPs, enriched with CloudWatch CPU utilization. Shared by the raw
resource-listing endpoint and the FinOps rules engine, so the scan logic
exists in exactly one place.
"""

import boto3

from app.services.aws import ebs, ec2, rds, snapshots
from app.services.aws.cloudwatch import get_ec2_cpu_utilization, get_rds_cpu_utilization


def fetch_inventory(session: boto3.Session, regions: list[str]) -> dict:
    ec2_instances: list[dict] = []
    ebs_volumes: list[dict] = []
    rds_instances: list[dict] = []
    ebs_snapshots: list[dict] = []
    elastic_ips: list[dict] = []

    for region in regions:
        for instance in ec2.list_instances(session, region):
            cpu = None
            if instance["state"] == "running":
                cpu = get_ec2_cpu_utilization(session, region, instance["instance_id"])
            ec2_instances.append(
                {
                    **instance,
                    "average_cpu": cpu["average_cpu"] if cpu else None,
                    "max_cpu": cpu["max_cpu"] if cpu else None,
                }
            )

        ebs_volumes.extend(ebs.list_volumes(session, region))
        ebs_snapshots.extend(snapshots.list_snapshots(session, region))
        elastic_ips.extend(ec2.list_elastic_ips(session, region))

        for db in rds.list_instances(session, region):
            cpu = None
            if db["status"] == "available":
                cpu = get_rds_cpu_utilization(session, region, db["db_instance_id"])
            rds_instances.append(
                {
                    **db,
                    "average_cpu": cpu["average_cpu"] if cpu else None,
                    "max_cpu": cpu["max_cpu"] if cpu else None,
                }
            )

    return {
        "ec2_instances": ec2_instances,
        "ebs_volumes": ebs_volumes,
        "rds_instances": rds_instances,
        "ebs_snapshots": ebs_snapshots,
        "elastic_ips": elastic_ips,
    }
