from pydantic import BaseModel, Field


class ResourceInventoryRequest(BaseModel):
    role_arn: str = Field(..., examples=["arn:aws:iam::123456789012:role/CloudheoReadOnlyRole"])
    external_id: str | None = None
    region: str | None = Field(None, description="Scan a single region; omit to scan every enabled region")


class Ec2Instance(BaseModel):
    instance_id: str
    instance_type: str
    state: str
    region: str
    tags: dict[str, str]
    average_cpu: float | None = None
    max_cpu: float | None = None


class EbsVolume(BaseModel):
    volume_id: str
    size_gb: int
    state: str
    attached: bool
    attached_instance_id: str | None = None
    region: str
    tags: dict[str, str]


class EbsSnapshot(BaseModel):
    snapshot_id: str
    volume_id: str
    volume_size_gb: int
    state: str
    start_time: str
    region: str
    tags: dict[str, str]


class RdsInstance(BaseModel):
    db_instance_id: str
    engine: str
    instance_class: str
    status: str
    multi_az: bool
    region: str
    tags: dict[str, str]
    average_cpu: float | None = None
    max_cpu: float | None = None


class ResourceInventoryResponse(BaseModel):
    regions_scanned: list[str]
    ec2_instances: list[Ec2Instance]
    ebs_volumes: list[EbsVolume]
    rds_instances: list[RdsInstance]
    ebs_snapshots: list[EbsSnapshot]
