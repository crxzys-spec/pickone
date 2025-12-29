from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.expert import (
    ExpertBatchDelete,
    ExpertCreate,
    ExpertOut,
    ExpertUpdate,
)
from app.schemas.pagination import Page, PageParams
from app.services import experts as expert_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["expert:read"]))],
    response_model=Page[ExpertOut],
)
def list_experts(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = expert_service.list_experts(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.get(
    "/all",
    dependencies=[Depends(require_scopes(["expert:read"]))],
    response_model=list[ExpertOut],
)
def list_experts_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expert_service.list_experts_all(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["expert:write"]))],
    response_model=ExpertOut,
    status_code=status.HTTP_201_CREATED,
)
def create_expert(
    payload: ExpertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expert_service.create_expert(db, payload)


@router.post(
    "/import",
    dependencies=[Depends(require_scopes(["expert:write"]))],
)
def import_experts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expert_service.import_experts(db, file)


@router.get(
    "/export",
    dependencies=[Depends(require_scopes(["expert:read"]))],
)
def export_experts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    output = expert_service.export_experts(db)
    filename = f"experts_{datetime.utcnow().date().isoformat()}.xlsx"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get(
    "/{expert_id}",
    dependencies=[Depends(require_scopes(["expert:read"]))],
    response_model=ExpertOut,
)
def get_expert(
    expert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expert_service.get_expert(db, expert_id)


@router.put(
    "/{expert_id}",
    dependencies=[Depends(require_scopes(["expert:write"]))],
    response_model=ExpertOut,
)
def update_expert(
    expert_id: int,
    payload: ExpertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expert_service.update_expert(db, expert_id, payload)


@router.delete(
    "/{expert_id}",
    dependencies=[Depends(require_scopes(["expert:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expert(
    expert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expert_service.delete_expert(db, expert_id)
    return None


@router.post(
    "/batch-delete",
    dependencies=[Depends(require_scopes(["expert:write"]))],
)
def batch_delete_experts(
    payload: ExpertBatchDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expert_service.delete_experts(db, payload.ids)
