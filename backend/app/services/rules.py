from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.repo.rules import RuleRepo
from app.services import categories as category_service
from app.schemas.rule import RuleCreate, RuleUpdate


def list_rules(db: Session) -> list[Rule]:
    return RuleRepo(db).list()


def get_rule(db: Session, rule_id: int) -> Rule:
    rule = RuleRepo(db).get_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


def create_rule(db: Session, payload: RuleCreate) -> Rule:
    data = payload.model_dump()
    category = category_service.resolve_category(
        db, data.get("category_id"), data.get("category")
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is required",
        )
    subcategory = None
    subcategory_id = data.get("subcategory_id")
    subcategory_name = data.get("subcategory")
    if subcategory_id is not None or subcategory_name:
        subcategory = category_service.resolve_subcategory(
            db, subcategory_id, subcategory_name, category
        )

    rule = Rule(**data)
    rule.category_id = category.id
    rule.category = category.name
    if subcategory:
        rule.subcategory_id = subcategory.id
        rule.subcategory = subcategory.name
    else:
        rule.subcategory_id = None
        rule.subcategory = None
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: int, payload: RuleUpdate) -> Rule:
    rule = get_rule(db, rule_id)
    update_data = payload.model_dump(exclude_unset=True)
    category_input = "category_id" in update_data or "category" in update_data
    subcategory_input = (
        "subcategory_id" in update_data or "subcategory" in update_data
    )
    category = None
    if category_input:
        category = category_service.resolve_category(
            db, update_data.get("category_id"), update_data.get("category")
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required",
            )
    elif subcategory_input:
        category = category_service.resolve_category(
            db, rule.category_id, rule.category, strict=False
        )

    subcategory = None
    if subcategory_input:
        subcategory_id = update_data.get("subcategory_id")
        subcategory_name = update_data.get("subcategory")
        if subcategory_id is not None or subcategory_name:
            subcategory = category_service.resolve_subcategory(
                db, subcategory_id, subcategory_name, category
            )
            if subcategory and category is None:
                category = category_service.resolve_category(
                    db, subcategory.category_id, None
                )

    if category_input:
        rule.category_id = category.id if category else None
        rule.category = category.name if category else update_data.get("category")
        if not subcategory_input:
            rule.subcategory_id = None
            rule.subcategory = None
    if subcategory_input:
        rule.subcategory_id = subcategory.id if subcategory else None
        rule.subcategory = (
            subcategory.name if subcategory else update_data.get("subcategory")
        )

    for key, value in update_data.items():
        if key in {"category_id", "category", "subcategory_id", "subcategory"}:
            continue
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int) -> None:
    rule = get_rule(db, rule_id)
    db.delete(rule)
    db.commit()
