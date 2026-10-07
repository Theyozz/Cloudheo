"""Static, approximate pricing used by the FinOps rules engine.

AWS pricing varies by region and changes over time. Querying the real-time
AWS Pricing API for every recommendation would add latency and complexity
that isn't justified yet. This table uses representative on-demand Linux
hourly rates (EU regions, as of late 2025) — good enough to produce directly
comparable, consistent savings estimates. Swap this for the AWS Pricing API
once accuracy at the cent level actually matters.
"""

HOURS_PER_MONTH = 730

# On-demand hourly price (USD) — Linux, EU region average.
EC2_HOURLY_PRICE: dict[str, float] = {
    "t3.nano": 0.0052,
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "t3.xlarge": 0.1664,
    "t3.2xlarge": 0.3328,
    "m5.large": 0.096,
    "m5.xlarge": 0.192,
    "m5.2xlarge": 0.384,
    "m5.4xlarge": 0.768,
    "r5.large": 0.126,
    "r5.xlarge": 0.252,
    "c5.large": 0.085,
    "c5.xlarge": 0.17,
}

# When an instance looks oversized, suggest stepping down to this type.
EC2_DOWNSIZE: dict[str, str] = {
    "t3.2xlarge": "t3.xlarge",
    "t3.xlarge": "t3.large",
    "t3.large": "t3.medium",
    "t3.medium": "t3.small",
    "t3.small": "t3.micro",
    "m5.4xlarge": "m5.2xlarge",
    "m5.2xlarge": "m5.xlarge",
    "m5.xlarge": "m5.large",
    "r5.xlarge": "r5.large",
    "c5.xlarge": "c5.large",
}

EBS_GP3_PRICE_PER_GB_MONTH = 0.088

# AWS bills EBS snapshots on the actual unique data stored, which the
# DescribeSnapshots API does not expose — only the source volume's full size
# is available. Using that size is therefore an UPPER BOUND, not an exact
# figure: a mostly-empty volume's snapshot is billed far below this estimate.
EBS_SNAPSHOT_PRICE_PER_GB_MONTH = 0.05

RDS_HOURLY_PRICE: dict[str, float] = {
    "db.t3.micro": 0.018,
    "db.t3.small": 0.036,
    "db.t3.medium": 0.072,
    "db.t3.large": 0.144,
    "db.t3.xlarge": 0.288,
    "db.m5.large": 0.19,
    "db.m5.xlarge": 0.38,
    "db.m5.2xlarge": 0.76,
    "db.r5.large": 0.24,
    "db.r5.xlarge": 0.48,
}

RDS_DOWNSIZE: dict[str, str] = {
    "db.t3.xlarge": "db.t3.large",
    "db.t3.large": "db.t3.medium",
    "db.t3.medium": "db.t3.small",
    "db.t3.small": "db.t3.micro",
    "db.m5.2xlarge": "db.m5.xlarge",
    "db.m5.xlarge": "db.m5.large",
    "db.r5.xlarge": "db.r5.large",
}

# A non-production resource running 24/7 could instead run on a business-hours
# schedule. Used by the non-prod scheduling rule.
NON_PROD_SCHEDULE_HOURS_PER_DAY = 12
NON_PROD_SCHEDULE_DAYS_PER_WEEK = 5


def ec2_monthly_cost(instance_type: str) -> float | None:
    hourly = EC2_HOURLY_PRICE.get(instance_type)
    if hourly is None:
        return None
    return round(hourly * HOURS_PER_MONTH, 2)


def rds_monthly_cost(instance_class: str) -> float | None:
    hourly = RDS_HOURLY_PRICE.get(instance_class)
    if hourly is None:
        return None
    return round(hourly * HOURS_PER_MONTH, 2)


def ebs_monthly_cost(size_gb: int) -> float:
    return round(size_gb * EBS_GP3_PRICE_PER_GB_MONTH, 2)


def ebs_snapshot_monthly_cost_upper_bound(volume_size_gb: int) -> float:
    return round(volume_size_gb * EBS_SNAPSHOT_PRICE_PER_GB_MONTH, 2)


def non_prod_scheduled_monthly_hours() -> float:
    weeks_per_month = HOURS_PER_MONTH / (24 * 7)
    return round(NON_PROD_SCHEDULE_HOURS_PER_DAY * NON_PROD_SCHEDULE_DAYS_PER_WEEK * weeks_per_month, 1)
