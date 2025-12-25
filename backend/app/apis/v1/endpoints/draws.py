from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.draw import DrawApply, DrawOut, DrawReplace, DrawResultOut, DrawUpdate
from app.services import draws as draw_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["draw:read"]))],
    response_model=list[DrawOut],
)
def list_draws(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.list_draws(db)


@router.post(
    "/apply",
    dependencies=[Depends(require_scopes(["draw:apply"]))],
    response_model=DrawOut,
    status_code=status.HTTP_201_CREATED,
)
def apply_draw(
    payload: DrawApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.create_draw(db, payload, current_user.id)


@router.get(
    "/{draw_id}",
    dependencies=[Depends(require_scopes(["draw:read"]))],
    response_model=DrawOut,
)
def get_draw(
    draw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.get_draw(db, draw_id)


@router.put(
    "/{draw_id}",
    dependencies=[Depends(require_scopes(["draw:apply"]))],
    response_model=DrawOut,
)
def update_draw(
    draw_id: int,
    payload: DrawUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.update_draw(db, draw_id, payload)


@router.delete(
    "/{draw_id}",
    dependencies=[Depends(require_scopes(["draw:apply"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_draw(
    draw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draw_service.delete_draw(db, draw_id)
    return None


@router.post(
    "/{draw_id}/execute",
    dependencies=[Depends(require_scopes(["draw:execute"]))],
    response_model=list[DrawResultOut],
)
def execute_draw(
    draw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.execute_draw(db, draw_id)


@router.get(
    "/{draw_id}/results",
    dependencies=[Depends(require_scopes(["draw:read"]))],
    response_model=list[DrawResultOut],
)
def list_draw_results(
    draw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.list_results(db, draw_id)


@router.post(
    "/{draw_id}/replace",
    dependencies=[Depends(require_scopes(["draw:execute"]))],
    response_model=list[DrawResultOut],
)
def replace_draw_result(
    draw_id: int,
    payload: DrawReplace,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return draw_service.replace_draw_result(db, draw_id, payload.result_id)
