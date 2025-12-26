from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryOut,
    CategoryTreeOut,
    CategoryUpdate,
)
from app.schemas.pagination import Page, PageParams
from app.schemas.subcategory import SubcategoryCreate, SubcategoryOut, SubcategoryUpdate
from app.services import categories as category_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["category:read"]))],
    response_model=Page[CategoryOut],
)
def list_categories(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = category_service.list_categories(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.get(
    "/tree",
    dependencies=[Depends(require_scopes(["category:read"]))],
    response_model=list[CategoryTreeOut],
)
def list_category_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.list_category_tree(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["category:write"]))],
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_category(db, payload)


@router.put(
    "/{category_id}",
    dependencies=[Depends(require_scopes(["category:write"]))],
    response_model=CategoryOut,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.update_category(db, category_id, payload)


@router.delete(
    "/{category_id}",
    dependencies=[Depends(require_scopes(["category:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category_service.delete_category(db, category_id)
    return None


@router.get(
    "/{category_id}/subcategories",
    dependencies=[Depends(require_scopes(["subcategory:read"]))],
    response_model=Page[SubcategoryOut],
)
def list_subcategories(
    category_id: int,
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = category_service.list_subcategories(db, category_id, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.post(
    "/{category_id}/subcategories",
    dependencies=[Depends(require_scopes(["subcategory:write"]))],
    response_model=SubcategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_subcategory(
    category_id: int,
    payload: SubcategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_subcategory(db, category_id, payload)


@router.put(
    "/subcategories/{subcategory_id}",
    dependencies=[Depends(require_scopes(["subcategory:write"]))],
    response_model=SubcategoryOut,
)
def update_subcategory(
    subcategory_id: int,
    payload: SubcategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.update_subcategory(db, subcategory_id, payload)


@router.delete(
    "/subcategories/{subcategory_id}",
    dependencies=[Depends(require_scopes(["subcategory:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category_service.delete_subcategory(db, subcategory_id)
    return None
