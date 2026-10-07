from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException

from app.schemas.resources import ResourceInventoryRequest, ResourceInventoryResponse
from app.services.aws import ec2
from app.services.aws.inventory import fetch_inventory
from app.services.aws.sts import AssumeRoleError, assume_role, session_from_assumed_credentials

router = APIRouter(prefix="/aws", tags=["aws"])


@router.post("/resources", response_model=ResourceInventoryResponse)
def get_resources(payload: ResourceInventoryRequest):
    """Inventory EC2 instances, EBS volumes, EBS snapshots and RDS instances
    for a customer account, enriched with CloudWatch CPU utilization for
    running resources.
    """
    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        session = session_from_assumed_credentials(creds)
        regions = [payload.region] if payload.region else ec2.list_regions(session)
        inventory = fetch_inventory(session, regions)
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ResourceInventoryResponse(regions_scanned=regions, **inventory)
