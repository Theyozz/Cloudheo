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


def ec2_monthly_cost(instance_type: str) -> float | None:
    hourly = EC2_HOURLY_PRICE.get(instance_type)
    if hourly is None:
        return None
    return round(hourly * HOURS_PER_MONTH, 2)


def ebs_monthly_cost(size_gb: int) -> float:
    return round(size_gb * EBS_GP3_PRICE_PER_GB_MONTH, 2)
