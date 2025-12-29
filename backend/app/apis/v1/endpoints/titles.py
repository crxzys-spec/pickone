from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.pagination import Page, PageParams
from app.schemas.title import (
    TitleBatchDelete,
    TitleCreate,
    TitleOut,
    TitleUpdate,
)
from app.services import titles as title_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["title:read"]))],
    response_model=Page[TitleOut],
)
def list_titles(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = title_service.list_titles(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.get(
    "/all",
    dependencies=[Depends(require_scopes(["title:read"]))],
    response_model=list[TitleOut],
)
def list_titles_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return title_service.list_titles_all(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["title:write"]))],
    response_model=TitleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_title(
    payload: TitleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return title_service.create_title(db, payload)


@router.get(
    "/{title_id}",
    dependencies=[Depends(require_scopes(["title:read"]))],
    response_model=TitleOut,
)
def get_title(
    title_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return title_service.get_title(db, title_id)


@router.put(
    "/{title_id}",
    dependencies=[Depends(require_scopes(["title:write"]))],
    response_model=TitleOut,
)
def update_title(
    title_id: int,
    payload: TitleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return title_service.update_title(db, title_id, payload)


@router.delete(
    "/{title_id}",
    dependencies=[Depends(require_scopes(["title:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_title(
    title_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    title_service.delete_title(db, title_id)
    return None


@router.post(
    "/batch-delete",
    dependencies=[Depends(require_scopes(["title:write"]))],
)
def batch_delete_titles(
    payload: TitleBatchDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return title_service.delete_titles(db, payload.ids)
