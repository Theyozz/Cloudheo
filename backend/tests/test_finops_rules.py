from app.services.finops.rules import (
    evaluate_all,
    evaluate_ebs_unattached,
    evaluate_ec2_rightsizing,
    evaluate_non_prod_scheduling,
    evaluate_orphaned_snapshots,
    evaluate_rds_rightsizing,
    evaluate_stopped_instance_storage,
)
from app.services.finops.pricing import ebs_monthly_cost


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
            "tags": {},
        }
    ]
    volumes = [{"volume_id": "vol-big-waste", "size_gb": 1000, "attached": False}]

    recs = evaluate_all(instances, volumes, [], [])

    assert len(recs) == 2
    assert recs[0].estimated_savings >= recs[1].estimated_savings


def test_underutilized_rds_instance_is_flagged():
    instances = [
        {
            "db_instance_id": "db-underused",
            "instance_class": "db.t3.large",
            "status": "available",
            "average_cpu": 5.0,
            "max_cpu": 15.0,
        }
    ]

    recs = evaluate_rds_rightsizing(instances)

    assert len(recs) == 1
    rec = recs[0]
    assert rec.resource_type == "RDS"
    assert rec.category == "RIGHTSIZING"
    assert rec.estimated_savings > 0


def test_rds_instance_not_available_is_ignored():
    instances = [
        {
            "db_instance_id": "db-creating",
            "instance_class": "db.t3.large",
            "status": "creating",
            "average_cpu": 2.0,
            "max_cpu": 5.0,
        }
    ]

    assert evaluate_rds_rightsizing(instances) == []


def test_tagged_non_prod_ec2_instance_is_flagged_for_scheduling():
    instances = [
        {
            "instance_id": "i-dev-box",
            "instance_type": "t3.medium",
            "state": "running",
            "tags": {"Environment": "dev"},
        }
    ]

    recs = evaluate_non_prod_scheduling(instances, [])

    assert len(recs) == 1
    rec = recs[0]
    assert rec.resource_type == "EC2"
    assert rec.category == "NON_PROD_SCHEDULING"
    assert rec.risk == "MEDIUM"
    assert rec.estimated_savings > 0
    assert rec.confidence == 0.9


def test_production_ec2_instance_is_not_flagged_for_scheduling():
    instances = [
        {
            "instance_id": "i-prod-box",
            "instance_type": "t3.medium",
            "state": "running",
            "tags": {"Environment": "production"},
        }
    ]

    assert evaluate_non_prod_scheduling(instances, []) == []


def test_name_matched_non_prod_rds_instance_is_flagged():
    instances = [
        {
            "db_instance_id": "staging-reporting-db",
            "instance_class": "db.t3.large",
            "status": "available",
            "tags": {},
        }
    ]

    recs = evaluate_non_prod_scheduling([], instances)

    assert len(recs) == 1
    rec = recs[0]
    assert rec.resource_type == "RDS"
    assert rec.confidence == 0.65


def test_stopped_instance_with_attached_volume_is_flagged():
    instances = [{"instance_id": "i-stopped-1", "state": "stopped"}]
    volumes = [
        {"volume_id": "vol-1", "size_gb": 100, "attached_instance_id": "i-stopped-1"},
        {"volume_id": "vol-unrelated", "size_gb": 50, "attached_instance_id": "i-other"},
    ]

    recs = evaluate_stopped_instance_storage(instances, volumes)

    assert len(recs) == 1
    rec = recs[0]
    assert rec.resource_id == "i-stopped-1"
    assert rec.category == "STOPPED_INSTANCE_STORAGE"
    assert rec.risk == "HIGH"
    # Only vol-1's cost counts, not the unrelated volume's.
    assert rec.estimated_savings == ebs_monthly_cost(100)


def test_stopped_instance_without_volumes_is_not_flagged():
    instances = [{"instance_id": "i-stopped-2", "state": "stopped"}]
    volumes = [{"volume_id": "vol-elsewhere", "size_gb": 50, "attached_instance_id": "i-other"}]

    assert evaluate_stopped_instance_storage(instances, volumes) == []


def test_running_instance_is_not_flagged_for_stopped_storage():
    instances = [{"instance_id": "i-running", "state": "running"}]
    volumes = [{"volume_id": "vol-1", "size_gb": 100, "attached_instance_id": "i-running"}]

    assert evaluate_stopped_instance_storage(instances, volumes) == []


def test_orphaned_snapshot_is_flagged():
    volumes = [{"volume_id": "vol-still-exists", "size_gb": 20}]
    snapshots = [
        {"snapshot_id": "snap-orphan", "volume_id": "vol-deleted-long-ago", "volume_size_gb": 40},
        {"snapshot_id": "snap-current", "volume_id": "vol-still-exists", "volume_size_gb": 20},
    ]

    recs = evaluate_orphaned_snapshots(volumes, snapshots)

    assert len(recs) == 1
    assert recs[0].resource_id == "snap-orphan"
    assert recs[0].category == "ORPHANED_SNAPSHOT"
    assert recs[0].risk == "LOW"


def test_snapshot_of_existing_volume_is_not_flagged():
    volumes = [{"volume_id": "vol-still-exists", "size_gb": 20}]
    snapshots = [{"snapshot_id": "snap-current", "volume_id": "vol-still-exists", "volume_size_gb": 20}]

    assert evaluate_orphaned_snapshots(volumes, snapshots) == []
