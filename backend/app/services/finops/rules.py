"""Deterministic FinOps rules.

Each rule is a pure function: structured AWS data in, Recommendation objects
out. No AI, no randomness — every number here must be reproducible and
traceable back to the input data. Turning these into natural-language
explanations is a separate, later concern (the AI service).
"""

from app.schemas.recommendations import Recommendation
from app.services.finops.pricing import EC2_DOWNSIZE, ebs_monthly_cost, ec2_monthly_cost

EC2_AVG_CPU_THRESHOLD = 10.0
EC2_MAX_CPU_THRESHOLD = 40.0


def _ec2_confidence(average_cpu: float, max_cpu: float) -> float:
    """Lower CPU usage -> higher confidence the instance is oversized."""
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
                confidence=_ec2_confidence(average_cpu, max_cpu),
                title=f"Downsize {instance['instance_id']} from {instance_type} to {downsize_to}",
                description=(
                    f"Average CPU is {average_cpu}% and max CPU is {max_cpu}% over "
                    f"the observed period. {downsize_to} should comfortably cover "
                    f"this instance's current load."
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


def evaluate_all(ec2_instances: list[dict], ebs_volumes: list[dict]) -> list[Recommendation]:
    recommendations = evaluate_ec2_rightsizing(ec2_instances) + evaluate_ebs_unattached(ebs_volumes)
    return sorted(recommendations, key=lambda r: r.estimated_savings, reverse=True)
