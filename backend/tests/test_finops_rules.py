from app.services.finops.rules import evaluate_all, evaluate_ebs_unattached, evaluate_ec2_rightsizing


def test_underutilized_running_instance_is_flagged():
    instances = [
        {
            "instance_id": "i-underused",
            "instance_type": "t3.large",
            "state": "running",
            "average_cpu": 8.2,
            "max_cpu": 27.0,
        }
    ]

    recs = evaluate_ec2_rightsizing(instances)

    assert len(recs) == 1
    rec = recs[0]
    assert rec.resource_id == "i-underused"
    assert rec.category == "RIGHTSIZING"
    assert rec.estimated_savings > 0
    assert rec.estimated_optimized_cost < rec.current_cost
    assert 0.5 <= rec.confidence <= 0.98


def test_busy_instance_is_not_flagged():
    instances = [
        {
            "instance_id": "i-busy",
            "instance_type": "t3.large",
            "state": "running",
            "average_cpu": 65.0,
            "max_cpu": 90.0,
        }
    ]

    assert evaluate_ec2_rightsizing(instances) == []


def test_stopped_instance_is_ignored():
    instances = [
        {
            "instance_id": "i-stopped",
            "instance_type": "t3.large",
            "state": "stopped",
            "average_cpu": 2.0,
            "max_cpu": 5.0,
        }
    ]

    assert evaluate_ec2_rightsizing(instances) == []


def test_instance_without_cpu_data_is_ignored():
    instances = [
        {
            "instance_id": "i-nodata",
            "instance_type": "t3.large",
            "state": "running",
            "average_cpu": None,
            "max_cpu": None,
        }
    ]

    assert evaluate_ec2_rightsizing(instances) == []


def test_unknown_instance_type_is_skipped_not_crashed():
    instances = [
        {
            "instance_id": "i-exotic",
            "instance_type": "x9.impossible",
            "state": "running",
            "average_cpu": 1.0,
            "max_cpu": 2.0,
        }
    ]

    assert evaluate_ec2_rightsizing(instances) == []


def test_unattached_volume_is_flagged():
    volumes = [{"volume_id": "vol-unused", "size_gb": 200, "attached": False}]

    recs = evaluate_ebs_unattached(volumes)

    assert len(recs) == 1
    assert recs[0].category == "UNATTACHED_VOLUME"
    assert recs[0].estimated_savings > 0
    assert recs[0].estimated_optimized_cost == 0.0


def test_attached_volume_is_not_flagged():
    volumes = [{"volume_id": "vol-used", "size_gb": 200, "attached": True}]

    assert evaluate_ebs_unattached(volumes) == []


def test_evaluate_all_sorts_by_savings_descending():
    instances = [
        {
            "instance_id": "i-small-waste",
            "instance_type": "t3.small",
            "state": "running",
            "average_cpu": 3.0,
            "max_cpu": 10.0,
        }
    ]
    volumes = [{"volume_id": "vol-big-waste", "size_gb": 1000, "attached": False}]

    recs = evaluate_all(instances, volumes)

    assert len(recs) == 2
    assert recs[0].estimated_savings >= recs[1].estimated_savings
