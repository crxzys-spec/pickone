from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate
from app.services import permissions as permission_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=list[PermissionOut],
)
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return permission_service.list_permissions(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=PermissionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return permission_service.create_permission(db, payload)


@router.get(
    "/{permission_id}",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=PermissionOut,
)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return permission_service.get_permission(db, permission_id)


@router.put(
    "/{permission_id}",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=PermissionOut,
)
def update_permission(
    permission_id: int,
    payload: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return permission_service.update_permission(db, permission_id, payload)


@router.delete(
    "/{permission_id}",
    dependencies=[Depends(require_scopes(["role:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    permission_service.delete_permission(db, permission_id)
    return None
