"""Deterministic FinOps rules.

Each rule is a pure function: structured AWS data in, Recommendation objects
out. No AI, no randomness — every number here must be reproducible and
traceable back to the input data. Turning these into natural-language
explanations is a separate, later concern (the AI service).
"""

from app.schemas.recommendations import Recommendation
from app.services.finops.environment import is_non_production
from app.services.finops.pricing import (
    EC2_DOWNSIZE,
    HOURS_PER_MONTH,
    MIN_ON_DEMAND_COST_FOR_SAVINGS_PLAN,
    NON_PROD_SCHEDULE_DAYS_PER_WEEK,
    NON_PROD_SCHEDULE_HOURS_PER_DAY,
    RDS_DOWNSIZE,
    SAVINGS_PLAN_COVERAGE_FLAG_THRESHOLD,
    SAVINGS_PLAN_ESTIMATED_DISCOUNT,
    ebs_gp2_monthly_cost,
    ebs_monthly_cost,
    ebs_snapshot_monthly_cost_upper_bound,
    ec2_monthly_cost,
    elastic_ip_idle_monthly_cost,
    non_prod_scheduled_monthly_hours,
    rds_monthly_cost,
    savings_plan_optimized_cost,
)

EC2_AVG_CPU_THRESHOLD = 10.0
EC2_MAX_CPU_THRESHOLD = 40.0
RDS_AVG_CPU_THRESHOLD = 10.0
RDS_MAX_CPU_THRESHOLD = 40.0


def _rightsizing_confidence(average_cpu: float, max_cpu: float) -> float:
    """Lower CPU usage -> higher confidence the resource is oversized."""
    score = 1 - (average_cpu / 100) * 0.6 - (max_cpu / 100) * 0.4
    return round(max(0.5, min(0.98, score)), 2)


def evaluate_ec2_rightsizing(instances: list[dict]) -> list[Recommendation]:
    recommendations = []

    for instance in instances:
        if instance.get("state") != "running":
            continue
        average_cpu = instance.get("average_cpu")
        max_cpu = instance.get("max_cpu")
        if average_cpu is None or max_cpu is None:
            continue
        if average_cpu >= EC2_AVG_CPU_THRESHOLD or max_cpu >= EC2_MAX_CPU_THRESHOLD:
            continue

        instance_type = instance["instance_type"]
        downsize_to = EC2_DOWNSIZE.get(instance_type)
        current_cost = ec2_monthly_cost(instance_type)
        optimized_cost = ec2_monthly_cost(downsize_to) if downsize_to else None
        if downsize_to is None or current_cost is None or optimized_cost is None:
            continue

        recommendations.append(
            Recommendation(
                resource_id=instance["instance_id"],
                resource_type="EC2",
                category="RIGHTSIZING",
                current_cost=current_cost,
                estimated_optimized_cost=optimized_cost,
                estimated_savings=round(current_cost - optimized_cost, 2),
                risk="LOW",
                confidence=_rightsizing_confidence(average_cpu, max_cpu),
                title=f"Downsize {instance['instance_id']} from {instance_type} to {downsize_to}",
                description=(
                    f"Average CPU is {average_cpu}% and max CPU is {max_cpu}% over "
                    f"the observed period. {downsize_to} should comfortably cover "
                    f"this instance's current load."
                ),
            )
        )

    return recommendations


def evaluate_rds_rightsizing(instances: list[dict]) -> list[Recommendation]:
    recommendations = []

    for db in instances:
        if db.get("status") != "available":
            continue
        average_cpu = db.get("average_cpu")
        max_cpu = db.get("max_cpu")
        if average_cpu is None or max_cpu is None:
            continue
        if average_cpu >= RDS_AVG_CPU_THRESHOLD or max_cpu >= RDS_MAX_CPU_THRESHOLD:
            continue

        instance_class = db["instance_class"]
        downsize_to = RDS_DOWNSIZE.get(instance_class)
        current_cost = rds_monthly_cost(instance_class)
        optimized_cost = rds_monthly_cost(downsize_to) if downsize_to else None
        if downsize_to is None or current_cost is None or optimized_cost is None:
            continue

        recommendations.append(
            Recommendation(
                resource_id=db["db_instance_id"],
                resource_type="RDS",
                category="RIGHTSIZING",
                current_cost=current_cost,
                estimated_optimized_cost=optimized_cost,
                estimated_savings=round(current_cost - optimized_cost, 2),
                risk="LOW",
                confidence=_rightsizing_confidence(average_cpu, max_cpu),
                title=f"Downsize {db['db_instance_id']} from {instance_class} to {downsize_to}",
                description=(
                    f"Average CPU is {average_cpu}% and max CPU is {max_cpu}% over "
                    f"the observed period. {downsize_to} should comfortably cover "
                    f"this database's current load."
                ),
            )
        )

    return recommendations


def evaluate_ebs_unattached(volumes: list[dict]) -> list[Recommendation]:
    recommendations = []

    for volume in volumes:
        if volume.get("attached"):
            continue

        monthly_cost = ebs_monthly_cost(volume["size_gb"])
        recommendations.append(
            Recommendation(
                resource_id=volume["volume_id"],
                resource_type="EBS",
                category="UNATTACHED_VOLUME",
                current_cost=monthly_cost,
                estimated_optimized_cost=0.0,
                estimated_savings=monthly_cost,
                risk="LOW",
                confidence=0.97,
                title=f"Delete unattached volume {volume['volume_id']}",
                description=(
                    f"This {volume['size_gb']} GB volume is not attached to any "
                    f"instance. If it isn't needed, deleting it removes its "
                    f"monthly storage cost entirely."
                ),
            )
        )

    return recommendations


def evaluate_stopped_instance_storage(ec2_instances: list[dict], ebs_volumes: list[dict]) -> list[Recommendation]:
    """A stopped EC2 instance pays no compute charges, but its attached
    volumes keep incurring storage cost regardless of instance state. This
    only reports the (certain) fact that storage is still billed — it makes
    no claim about how long the instance has been stopped, since that isn't
    available from the EC2 API without parsing a free-text field."""
    recommendations = []

    for instance in ec2_instances:
        if instance.get("state") != "stopped":
            continue

        attached = [v for v in ebs_volumes if v.get("attached_instance_id") == instance["instance_id"]]
        if not attached:
            continue

        monthly_cost = round(sum(ebs_monthly_cost(v["size_gb"]) for v in attached), 2)
        if monthly_cost <= 0:
            continue

        recommendations.append(
            Recommendation(
                resource_id=instance["instance_id"],
                resource_type="EC2",
                category="STOPPED_INSTANCE_STORAGE",
                current_cost=monthly_cost,
                estimated_optimized_cost=0.0,
                estimated_savings=monthly_cost,
                risk="HIGH",
                confidence=0.9,
                title=f"Review stopped instance {instance['instance_id']}",
                description=(
                    f"This instance is stopped, but its {len(attached)} attached "
                    f"volume(s) still cost {monthly_cost:.2f} USD/month in storage, "
                    f"regardless of the instance being off. If you don't plan to "
                    f"restart it, consider terminating it (which can also delete "
                    f"its volumes) after taking a final snapshot if needed."
                ),
            )
        )

    return recommendations


def evaluate_orphaned_snapshots(ebs_volumes: list[dict], snapshots: list[dict]) -> list[Recommendation]:
    """An EBS snapshot whose source volume no longer exists is unambiguously
    orphaned — the safest, most precise definition of an 'unused snapshot'.
    Its cost is an upper bound: AWS bills snapshots on the unique data they
    store, which the API does not expose, only the source volume's full size."""
    existing_volume_ids = {v["volume_id"] for v in ebs_volumes}
    recommendations = []

    for snapshot in snapshots:
        if snapshot["volume_id"] in existing_volume_ids:
            continue

        monthly_cost = ebs_snapshot_monthly_cost_upper_bound(snapshot["volume_size_gb"])
        if monthly_cost <= 0:
            continue

        recommendations.append(
            Recommendation(
                resource_id=snapshot["snapshot_id"],
                resource_type="EBS",
                category="ORPHANED_SNAPSHOT",
                current_cost=monthly_cost,
                estimated_optimized_cost=0.0,
                estimated_savings=monthly_cost,
                risk="LOW",
                confidence=0.95,
                title=f"Delete orphaned snapshot {snapshot['snapshot_id']}",
                description=(
                    f"The source volume for this snapshot ({snapshot['volume_id']}) "
                    f"no longer exists. Estimated cost is an upper bound of "
                    f"{monthly_cost:.2f} USD/month, based on the original "
                    f"{snapshot['volume_size_gb']} GB volume size."
                ),
            )
        )

    return recommendations


def evaluate_unused_elastic_ips(elastic_ips: list[dict]) -> list[Recommendation]:
    recommendations = []
    monthly_cost = elastic_ip_idle_monthly_cost()

    for eip in elastic_ips:
        if eip.get("associated"):
            continue

        recommendations.append(
            Recommendation(
                resource_id=eip["allocation_id"],
                resource_type="ELASTIC_IP",
                category="UNUSED_ELASTIC_IP",
                current_cost=monthly_cost,
                estimated_optimized_cost=0.0,
                estimated_savings=monthly_cost,
                risk="LOW",
                confidence=0.95,
                title=f"Release unused Elastic IP {eip['public_ip']}",
                description=(
                    f"This Elastic IP ({eip['public_ip']}) isn't associated with any "
                    f"running resource. AWS bills idle Elastic IPs hourly; releasing it "
                    f"removes this cost entirely."
                ),
            )
        )

    return recommendations


def evaluate_gp2_to_gp3(ebs_volumes: list[dict]) -> list[Recommendation]:
    """Attached gp2 volumes only — an unattached gp2 volume is already
    covered by the (strictly better) delete recommendation above, so
    suggesting a type migration on it too would just be noise."""
    recommendations = []

    for volume in ebs_volumes:
        if volume.get("volume_type") != "gp2" or not volume.get("attached"):
            continue

        current_cost = ebs_gp2_monthly_cost(volume["size_gb"])
        optimized_cost = ebs_monthly_cost(volume["size_gb"])
        savings = round(current_cost - optimized_cost, 2)
        if savings <= 0:
            continue

        recommendations.append(
            Recommendation(
                resource_id=volume["volume_id"],
                resource_type="EBS",
                category="GP3_MIGRATION",
                current_cost=current_cost,
                estimated_optimized_cost=optimized_cost,
                estimated_savings=savings,
                risk="LOW",
                confidence=0.95,
                title=f"Migrate {volume['volume_id']} from gp2 to gp3",
                description=(
                    f"This {volume['size_gb']} GB volume still uses the older gp2 type. "
                    f"gp3 offers the same baseline performance at a lower price per GB, "
                    f"and the migration can be done live with no downtime."
                ),
            )
        )

    return recommendations


def evaluate_savings_plan_coverage_gap(coverage: dict) -> list[Recommendation]:
    """Unlike the other rules, this isn't a single misconfigured resource —
    it's a financial-commitment opportunity across the whole account, so
    there's at most one recommendation here, not one per resource. Risk is
    MEDIUM rather than LOW because, unlike deleting or resizing a resource,
    a Savings Plan commits spend for a fixed term and can't be undone."""
    on_demand_cost = coverage["on_demand_cost"]
    coverage_percentage = coverage["coverage_percentage"]

    if on_demand_cost < MIN_ON_DEMAND_COST_FOR_SAVINGS_PLAN:
        return []
    if coverage_percentage >= SAVINGS_PLAN_COVERAGE_FLAG_THRESHOLD:
        return []

    optimized_cost = savings_plan_optimized_cost(on_demand_cost)
    savings = round(on_demand_cost - optimized_cost, 2)

    return [
        Recommendation(
            resource_id="compute-savings-plan",
            resource_type="SAVINGS_PLAN",
            category="SAVINGS_PLAN_COVERAGE_GAP",
            current_cost=on_demand_cost,
            estimated_optimized_cost=optimized_cost,
            estimated_savings=savings,
            risk="MEDIUM",
            confidence=0.7,
            title=f"Cover {on_demand_cost:.2f} USD/month of on-demand spend with a Savings Plan",
            description=(
                f"Only {coverage_percentage}% of your compute spend is covered by a "
                f"Savings Plan over the observed period, leaving {on_demand_cost:.2f} "
                f"USD/month on full on-demand pricing. A 1-year, no-upfront Compute "
                f"Savings Plan typically cuts this by at least "
                f"{int(SAVINGS_PLAN_ESTIMATED_DISCOUNT * 100)}% — but it's a committed "
                f"spend for the term, so size it to your baseline usage, not your peak."
            ),
        )
    ]


def _non_prod_schedule_savings(current_cost: float) -> float:
    scheduled_fraction = non_prod_scheduled_monthly_hours() / HOURS_PER_MONTH
    return round(current_cost * (1 - scheduled_fraction), 2)


def _non_prod_schedule_description(label: str) -> str:
    return (
        f"This looks like a non-production {label} running 24/7. Scheduling it to "
        f"stop outside business hours ({NON_PROD_SCHEDULE_HOURS_PER_DAY}h/day, "
        f"{NON_PROD_SCHEDULE_DAYS_PER_WEEK} days/week) would cut its cost significantly."
    )


def evaluate_non_prod_scheduling(ec2_instances: list[dict], rds_instances: list[dict]) -> list[Recommendation]:
    recommendations = []

    for instance in ec2_instances:
        if instance.get("state") != "running":
            continue
        non_prod, confidence = is_non_production(instance["instance_id"], instance.get("tags", {}))
        if not non_prod:
            continue
        current_cost = ec2_monthly_cost(instance["instance_type"])
        if current_cost is None:
            continue
        savings = _non_prod_schedule_savings(current_cost)
        if savings <= 0:
            continue

        recommendations.append(
            Recommendation(
                resource_id=instance["instance_id"],
                resource_type="EC2",
                category="NON_PROD_SCHEDULING",
                current_cost=current_cost,
                estimated_optimized_cost=round(current_cost - savings, 2),
                estimated_savings=savings,
                risk="MEDIUM",
                confidence=confidence,
                title=f"Schedule {instance['instance_id']} to business hours only",
                description=_non_prod_schedule_description("instance"),
            )
        )

    for db in rds_instances:
        if db.get("status") != "available":
            continue
        non_prod, confidence = is_non_production(db["db_instance_id"], db.get("tags", {}))
        if not non_prod:
            continue
        current_cost = rds_monthly_cost(db["instance_class"])
        if current_cost is None:
            continue
        savings = _non_prod_schedule_savings(current_cost)
        if savings <= 0:
            continue

        recommendations.append(
            Recommendation(
                resource_id=db["db_instance_id"],
                resource_type="RDS",
                category="NON_PROD_SCHEDULING",
                current_cost=current_cost,
                estimated_optimized_cost=round(current_cost - savings, 2),
                estimated_savings=savings,
                risk="MEDIUM",
                confidence=confidence,
                title=f"Schedule {db['db_instance_id']} to business hours only",
                description=_non_prod_schedule_description("database"),
            )
        )

    return recommendations


def evaluate_all(
    ec2_instances: list[dict],
    ebs_volumes: list[dict],
    rds_instances: list[dict],
    ebs_snapshots: list[dict],
    elastic_ips: list[dict],
    savings_plans_coverage: dict,
) -> list[Recommendation]:
    recommendations = (
        evaluate_ec2_rightsizing(ec2_instances)
        + evaluate_rds_rightsizing(rds_instances)
        + evaluate_ebs_unattached(ebs_volumes)
        + evaluate_stopped_instance_storage(ec2_instances, ebs_volumes)
        + evaluate_orphaned_snapshots(ebs_volumes, ebs_snapshots)
        + evaluate_non_prod_scheduling(ec2_instances, rds_instances)
        + evaluate_unused_elastic_ips(elastic_ips)
        + evaluate_gp2_to_gp3(ebs_volumes)
        + evaluate_savings_plan_coverage_gap(savings_plans_coverage)
    )
    return sorted(recommendations, key=lambda r: r.estimated_savings, reverse=True)
