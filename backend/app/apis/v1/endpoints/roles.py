from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.pagination import Page, PageParams
from app.schemas.role import RoleCreate, RoleOut, RolePermissionsUpdate, RoleUpdate
from app.services import roles as role_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=Page[RoleOut],
)
def list_roles(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = role_service.list_roles(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.get(
    "/all",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=list[RoleOut],
)
def list_roles_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return role_service.list_roles_all(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return role_service.create_role(db, payload)


@router.get(
    "/{role_id}",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=RoleOut,
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return role_service.get_role(db, role_id)


@router.put(
    "/{role_id}",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=RoleOut,
)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return role_service.update_role(db, role_id, payload)


@router.delete(
    "/{role_id}",
    dependencies=[Depends(require_scopes(["role:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_service.delete_role(db, role_id)
    return None


@router.put(
    "/{role_id}/permissions",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=RoleOut,
)
def assign_permissions(
    role_id: int,
    payload: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return role_service.assign_permissions(db, role_id, payload)
