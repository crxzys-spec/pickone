from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.pagination import Page, PageParams
from app.schemas.rule import RuleCreate, RuleOut, RuleUpdate
from app.services import rules as rule_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["rule:read"]))],
    response_model=Page[RuleOut],
)
def list_rules(
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = rule_service.list_rules(db, params)
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)


@router.get(
    "/all",
    dependencies=[Depends(require_scopes(["rule:read"]))],
    response_model=list[RuleOut],
)
def list_rules_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rule_service.list_rules_all(db)


@router.post(
    "",
    dependencies=[Depends(require_scopes(["rule:write"]))],
    response_model=RuleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(
    payload: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rule_service.create_rule(db, payload)


@router.get(
    "/{rule_id}",
    dependencies=[Depends(require_scopes(["rule:read"]))],
    response_model=RuleOut,
)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rule_service.get_rule(db, rule_id)


@router.put(
    "/{rule_id}",
    dependencies=[Depends(require_scopes(["rule:write"]))],
    response_model=RuleOut,
)
def update_rule(
    rule_id: int,
    payload: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rule_service.update_rule(db, rule_id, payload)


@router.delete(
    "/{rule_id}",
    dependencies=[Depends(require_scopes(["rule:write"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule_service.delete_rule(db, rule_id)
    return None
