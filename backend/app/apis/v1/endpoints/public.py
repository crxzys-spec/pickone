from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.apis.deps import get_db
from app.core.config import settings
from app.core.ratelimit import enforce_rate_limit
from app.repo.organizations import OrganizationRepo
from app.repo.regions import RegionRepo
from app.schemas.expert import ExpertPublicCreate
from app.schemas.public import ExpertPublicMetadata, ExpertPublicSubmitOut
from app.services import categories as category_service
from app.services import experts as expert_service
from app.services import titles as title_service

router = APIRouter()


@router.get("/experts/metadata", response_model=ExpertPublicMetadata)
def get_expert_public_metadata(db: Session = Depends(get_db)):
    organizations = OrganizationRepo(db).list()
    regions = RegionRepo(db).list()
    titles = title_service.list_title_tree(db)
    specialties = category_service.list_category_tree(db)
    return ExpertPublicMetadata(
        organizations=organizations,
        regions=regions,
        titles=titles,
        specialties=specialties,
    )


@router.post(
    "/experts/register",
    response_model=ExpertPublicSubmitOut,
    status_code=status.HTTP_201_CREATED,
)
def register_expert_public(
    request: Request,
    payload: ExpertPublicCreate,
    db: Session = Depends(get_db),
):
    enforce_rate_limit(
        request,
        "public-register",
        settings.rate_limit_public_register_per_hour,
        3600,
    )
    expert = expert_service.create_expert_public(db, payload)
    return ExpertPublicSubmitOut(id=expert.id, audit_status=expert.audit_status)
