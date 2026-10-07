from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException

from app.schemas.recommendations import Recommendation
from app.schemas.resources import ResourceInventoryRequest
from app.services.aws import ec2
from app.services.aws.inventory import fetch_inventory
from app.services.aws.sts import AssumeRoleError, assume_role, session_from_assumed_credentials
from app.services.finops.rules import evaluate_all

router = APIRouter(prefix="/finops", tags=["finops"])


@router.post("/recommendations", response_model=list[Recommendation])
def get_recommendations(payload: ResourceInventoryRequest):
    """Scan a customer account and run the deterministic FinOps rules over it."""
    try:
        creds = assume_role(role_arn=payload.role_arn, external_id=payload.external_id)
        session = session_from_assumed_credentials(creds)
        regions = [payload.region] if payload.region else ec2.list_regions(session)
        inventory = fetch_inventory(session, regions)
    except AssumeRoleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return evaluate_all(inventory["ec2_instances"], inventory["ebs_volumes"])
