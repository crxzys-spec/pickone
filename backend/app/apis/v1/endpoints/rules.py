from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.apis.deps import get_current_user, get_db, require_scopes
from app.models.user import User
from app.schemas.rule import RuleCreate, RuleOut, RuleUpdate
from app.services import rules as rule_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(require_scopes(["rule:read"]))],
    response_model=list[RuleOut],
)
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rule_service.list_rules(db)


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
