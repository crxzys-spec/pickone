from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.pagination import Page, PageParams
from app.schemas.user import (
    UserCreate,
    UserOut,
    UserPasswordChange,
    UserRolesUpdate,
    UserSelfUpdate,
    UserUpdate,
)
from app.services import users as user_service

router = APIRouter()


@router.get(
    "/me",
    response_model=UserOut,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put(
    "/me",
    response_model=UserOut,
)
def update_me(
    payload: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.update_self(db, current_user, payload)


@router.post(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    payload: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.change_password(db, current_user, payload)
    return None


@router.get(
    "",
    dependencies=[Depends(require_scopes(["user:read"]))],
    response_model=Page[UserOut],
)
def list_users(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = user_service.list_users(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["user:write"]))],
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.create_user(db, payload)


@router.get(
    "/{user_id}",
    dependencies=[Depends(require_scopes(["user:read"]))],
    response_model=UserOut,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.get_user(db, user_id)


@router.put(
    "/{user_id}",
    dependencies=[Depends(require_scopes(["user:write"]))],
    response_model=UserOut,
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.update_user(db, user_id, payload)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_scopes(["user:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.delete_user(db, user_id)
    return None


@router.put(
    "/{user_id}/roles",
    dependencies=[Depends(require_scopes(["role:write"]))],
    response_model=UserOut,
)
def assign_roles(
    user_id: int,
    payload: UserRolesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.assign_roles(db, user_id, payload)
