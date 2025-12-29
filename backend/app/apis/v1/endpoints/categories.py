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
from app.schemas.subcategory import SubcategoryCreate, SubcategoryOut, SubcategoryUpdate
from app.schemas.specialty import SpecialtyCreate, SpecialtyOut, SpecialtyUpdate
from app.services import categories as category_service
from app.services import specialties as specialty_service

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
    dependencies=[
        Depends(require_scopes(["category:write", "subcategory:write", "specialty:write"]))
    ],
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


@router.get(
    "/subcategories/{subcategory_id}/specialties",
    dependencies=[Depends(require_scopes(["specialty:read"]))],
    response_model=Page[SpecialtyOut],
)
def list_specialties(
    subcategory_id: int,
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = specialty_service.list_specialties(db, subcategory_id, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.post(
    "/subcategories/{subcategory_id}/specialties",
    dependencies=[Depends(require_scopes(["specialty:write"]))],
    response_model=SpecialtyOut,
    status_code=status.HTTP_201_CREATED,
)
def create_specialty(
    subcategory_id: int,
    payload: SpecialtyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return specialty_service.create_specialty(db, subcategory_id, payload)


@router.put(
    "/specialties/{specialty_id}",
    dependencies=[Depends(require_scopes(["specialty:write"]))],
    response_model=SpecialtyOut,
)
def update_specialty(
    specialty_id: int,
    payload: SpecialtyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return specialty_service.update_specialty(db, specialty_id, payload)


@router.delete(
    "/specialties/{specialty_id}",
    dependencies=[Depends(require_scopes(["specialty:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_specialty(
    specialty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    specialty_service.delete_specialty(db, specialty_id)
    return None
