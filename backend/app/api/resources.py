from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException

from app.schemas.resources import (
    Ec2Instance,
    EbsVolume,
    RdsInstance,
    ResourceInventoryRequest,
    ResourceInventoryResponse,
)
from app.services.aws import ebs, ec2, rds
from app.services.aws.cloudwatch import get_ec2_cpu_utilization, get_rds_cpu_utilization
from app.services.aws.sts import AssumeRoleError, assume_role, session_from_assumed_credentials

router = APIRouter(prefix="/aws", tags=["aws"])


@router.post("/resources", response_model=ResourceInventoryResponse)
def get_resources(payload: ResourceInventoryRequest):
    """Inventory EC2 instances, EBS volumes and RDS instances for a customer
    account, enriched with CloudWatch CPU utilization for running resources.
    """
    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        session = session_from_assumed_credentials(creds)

        regions = [payload.region] if payload.region else ec2.list_regions(session)

        ec2_instances: list[Ec2Instance] = []
        ebs_volumes: list[EbsVolume] = []
        rds_instances: list[RdsInstance] = []

        for region in regions:
            for instance in ec2.list_instances(session, region):
                cpu = None
                if instance["state"] == "running":
                    cpu = get_ec2_cpu_utilization(session, region, instance["instance_id"])
                ec2_instances.append(
                    Ec2Instance(
                        **instance,
                        average_cpu=cpu["average_cpu"] if cpu else None,
                        max_cpu=cpu["max_cpu"] if cpu else None,
                    )
                )

            for volume in ebs.list_volumes(session, region):
                ebs_volumes.append(EbsVolume(**volume))

            for db in rds.list_instances(session, region):
                cpu = None
                if db["status"] == "available":
                    cpu = get_rds_cpu_utilization(session, region, db["db_instance_id"])
                rds_instances.append(
                    RdsInstance(
                        **db,
                        average_cpu=cpu["average_cpu"] if cpu else None,
                        max_cpu=cpu["max_cpu"] if cpu else None,
                    )
                )
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ResourceInventoryResponse(
        regions_scanned=regions,
        ec2_instances=ec2_instances,
        ebs_volumes=ebs_volumes,
        rds_instances=rds_instances,
    )
