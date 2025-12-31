from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.category import (
    CategoryBatchAction,
    CategoryBatchResult,
    CategoryCreate,
    CategoryOut,
    CategoryTreeOut,
    CategoryUpdate,
)
from app.schemas.pagination import Page, PageParams
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


@router.post(
    "/import",
    dependencies=[Depends(require_scopes(["category:write"]))],
)
def import_categories(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.import_categories(db, file)


@router.get(
    "/export",
    dependencies=[Depends(require_scopes(["category:read"]))],
)
def export_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    output = category_service.export_categories(db)
    filename = f"categories_{datetime.utcnow().date().isoformat()}.xlsx"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post(
    "/batch",
    dependencies=[Depends(require_scopes(["category:write"]))],
    response_model=CategoryBatchResult,
)
def batch_categories(
    payload: CategoryBatchAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.batch_categories(db, payload)


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
