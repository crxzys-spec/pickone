from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.pagination import Page, PageParams
from app.schemas.region import (
    RegionBatchDelete,
    RegionCreate,
    RegionOut,
    RegionUpdate,
)
from app.services import regions as region_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["region:read"]))],
    response_model=Page[RegionOut],
)
def list_regions(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = region_service.list_regions(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.get(
    "/all",
    dependencies=[Depends(require_scopes(["region:read"]))],
    response_model=list[RegionOut],
)
def list_regions_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return region_service.list_regions_all(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["region:write"]))],
    response_model=RegionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_region(
    payload: RegionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return region_service.create_region(db, payload)


@router.get(
    "/{region_id}",
    dependencies=[Depends(require_scopes(["region:read"]))],
    response_model=RegionOut,
)
def get_region(
    region_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return region_service.get_region(db, region_id)


@router.put(
    "/{region_id}",
    dependencies=[Depends(require_scopes(["region:write"]))],
    response_model=RegionOut,
)
def update_region(
    region_id: int,
    payload: RegionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return region_service.update_region(db, region_id, payload)


@router.delete(
    "/{region_id}",
    dependencies=[Depends(require_scopes(["region:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_region(
    region_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    region_service.delete_region(db, region_id)
    return None


@router.post(
    "/batch-delete",
    dependencies=[Depends(require_scopes(["region:write"]))],
)
def batch_delete_regions(
    payload: RegionBatchDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return region_service.delete_regions(db, payload.ids)
