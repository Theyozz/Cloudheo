"""CloudWatch metrics — used to feed the (future) FinOps rightsizing rules."""

from datetime import UTC, datetime, timedelta

import boto3


def get_cpu_utilization(
    session: boto3.Session,
    region: str,
    namespace: str,
    dimension_name: str,
    dimension_value: str,
    days: int = 14,
) -> dict | None:
    """Average/max CPU utilization over the window, or None if no data points
    (e.g. the resource was stopped the whole period, or is too new)."""
    client = session.client("cloudwatch", region_name=region)
    end = datetime.now(UTC)
    start = end - timedelta(days=days)

    response = client.get_metric_statistics(
        Namespace=namespace,
        MetricName="CPUUtilization",
        Dimensions=[{"Name": dimension_name, "Value": dimension_value}],
        StartTime=start,
        EndTime=end,
        Period=3600,
        Statistics=["Average", "Maximum"],
    )

    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return None

    return {
        "average_cpu": round(sum(d["Average"] for d in datapoints) / len(datapoints), 2),
        "max_cpu": round(max(d["Maximum"] for d in datapoints), 2),
    }


def get_ec2_cpu_utilization(session: boto3.Session, region: str, instance_id: str, days: int = 14) -> dict | None:
    return get_cpu_utilization(session, region, "AWS/EC2", "InstanceId", instance_id, days)


def get_rds_cpu_utilization(session: boto3.Session, region: str, db_instance_id: str, days: int = 14) -> dict | None:
    return get_cpu_utilization(session, region, "AWS/RDS", "DBInstanceIdentifier", db_instance_id, days)
