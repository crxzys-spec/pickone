from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
)
from app.services import organizations as organization_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["organization:read"]))],
    response_model=list[OrganizationOut],
)
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return organization_service.list_organizations(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["organization:write"]))],
    response_model=OrganizationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return organization_service.create_organization(db, payload)


@router.get(
    "/{organization_id}",
    dependencies=[Depends(require_scopes(["organization:read"]))],
    response_model=OrganizationOut,
)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return organization_service.get_organization(db, organization_id)


@router.put(
    "/{organization_id}",
    dependencies=[Depends(require_scopes(["organization:write"]))],
    response_model=OrganizationOut,
)
def update_organization(
    organization_id: int,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return organization_service.update_organization(db, organization_id, payload)


@router.delete(
    "/{organization_id}",
    dependencies=[Depends(require_scopes(["organization:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization_service.delete_organization(db, organization_id)
    return None
