from __future__ import annotations

import random

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.draw import DrawApplication, DrawResult
from app.models.expert import Expert
from app.repo.draws import DrawRepo
from app.repo.rules import RuleRepo
from app.repo.utils import apply_keyword, apply_sort, paginate
from app.services import categories as category_service
from app.schemas.pagination import PageParams
from app.schemas.draw import DrawApply, DrawUpdate

SUPPORTED_DRAW_METHODS = {"random", "lottery"}


def resolve_draw_method(draw: DrawApplication, rule) -> str:
    if draw.draw_method:
        return draw.draw_method
    if rule is not None and rule.draw_method:
        return rule.draw_method
    return "random"


def pick_experts(
    candidates: list[Expert], total_needed: int, draw_method: str
) -> list[Expert]:
    if draw_method == "random":
        return random.sample(candidates, total_needed)
    if draw_method == "lottery":
        tickets = [(random.random(), expert) for expert in candidates]
        tickets.sort(key=lambda item: item[0])
        return [expert for _, expert in tickets[:total_needed]]
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported draw method",
    )


def list_draws(db: Session, params: PageParams) -> tuple[list[DrawApplication], int]:
    return DrawRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def get_draw(db: Session, draw_id: int) -> DrawApplication:
    draw = DrawRepo(db).get_by_id(draw_id)
    if draw is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draw not found")
    return draw


def create_draw(db: Session, payload: DrawApply, created_by_id: int | None) -> DrawApplication:
    data = payload.model_dump()
    rule = None
    if payload.rule_id is not None:
        rule = RuleRepo(db).get_by_id(payload.rule_id)
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )

    if rule is not None:
        category = category_service.resolve_category(
            db, rule.category_id, rule.category
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required",
            )
        subcategory = None
        if rule.subcategory_id is not None or rule.subcategory:
            subcategory = category_service.resolve_subcategory(
                db, rule.subcategory_id, rule.subcategory, category, strict=False
            )
    else:
        category = category_service.resolve_category(
            db, data.get("category_id"), data.get("category")
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required",
            )
        subcategory = category_service.resolve_subcategory(
            db, data.get("subcategory_id"), data.get("subcategory"), category
        )
        if subcategory and category is None:
            category = category_service.resolve_category(
                db, subcategory.category_id, None
            )

    draw = DrawApplication(**data, created_by_id=created_by_id)
    if rule is not None:
        draw.rule_id = rule.id
    draw.category_id = category.id
    draw.category = category.name
    if subcategory:
        draw.subcategory_id = subcategory.id
        draw.subcategory = subcategory.name
    else:
        draw.subcategory_id = None
        draw.subcategory = None
    db.add(draw)
    db.commit()
    db.refresh(draw)
    return draw


def update_draw(db: Session, draw_id: int, payload: DrawUpdate) -> DrawApplication:
    draw = get_draw(db, draw_id)
    update_data = payload.model_dump(exclude_unset=True)

    rule = None
    if "rule_id" in update_data:
        rule_id = update_data.get("rule_id")
        if rule_id is not None:
            rule = RuleRepo(db).get_by_id(rule_id)
            if rule is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )
            draw.rule_id = rule.id
            category = category_service.resolve_category(
                db, rule.category_id, rule.category
            )
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category is required",
                )
            subcategory = None
            if rule.subcategory_id is not None or rule.subcategory:
                subcategory = category_service.resolve_subcategory(
                    db, rule.subcategory_id, rule.subcategory, category, strict=False
                )
            draw.category_id = category.id
            draw.category = category.name
            draw.subcategory_id = subcategory.id if subcategory else None
            draw.subcategory = subcategory.name if subcategory else None
        else:
            draw.rule_id = None

    category_input = "category_id" in update_data or "category" in update_data
    subcategory_input = "subcategory_id" in update_data or "subcategory" in update_data
    if rule is None and (category_input or subcategory_input):
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

        subcategory = None
        subcategory_value = update_data.get("subcategory")
        subcategory_id_value = update_data.get("subcategory_id")
        if subcategory_input and (subcategory_id_value is not None or subcategory_value):
            subcategory = category_service.resolve_subcategory(
                db,
                subcategory_id_value,
                subcategory_value,
                category,
            )
            if subcategory and category is None:
                category = category_service.resolve_category(
                    db, subcategory.category_id, None
                )

        if category_input or (subcategory and not category_input):
            draw.category_id = category.id if category else None
            draw.category = category.name if category else update_data.get("category")
        if subcategory_input:
            draw.subcategory_id = subcategory.id if subcategory else None
            draw.subcategory = (
                subcategory.name if subcategory else update_data.get("subcategory")
            )

    for key, value in update_data.items():
        if key in {
            "category_id",
            "category",
            "subcategory_id",
            "subcategory",
            "rule_id",
        }:
            continue
        setattr(draw, key, value)

    db.commit()
    db.refresh(draw)
    return draw


def delete_draw(db: Session, draw_id: int) -> None:
    draw = get_draw(db, draw_id)
    db.delete(draw)
    db.commit()


def list_results(db: Session, draw_id: int) -> list[DrawResult]:
    _ = get_draw(db, draw_id)
    stmt = (
        select(DrawResult)
        .where(DrawResult.draw_id == draw_id)
        .options(selectinload(DrawResult.expert))
        .order_by(DrawResult.is_backup, DrawResult.ordinal)
    )
    return list(db.execute(stmt).scalars().all())


def list_results_page(
    db: Session, draw_id: int, params: PageParams
) -> tuple[list[DrawResult], int]:
    _ = get_draw(db, draw_id)
    stmt = (
        select(DrawResult)
        .where(DrawResult.draw_id == draw_id)
        .options(selectinload(DrawResult.expert))
    )
    if params.keyword:
        stmt = stmt.join(Expert, Expert.id == DrawResult.expert_id, isouter=True)
        stmt = apply_keyword(
            stmt,
            params.keyword,
            [Expert.name, Expert.company, Expert.phone, Expert.email],
        )
    sort_map = {
        "id": DrawResult.id,
        "ordinal": DrawResult.ordinal,
        "is_backup": DrawResult.is_backup,
        "is_replacement": DrawResult.is_replacement,
    }
    if params.sort_by:
        stmt = apply_sort(
            stmt, params.sort_by, params.sort_order, sort_map, DrawResult.id
        )
    else:
        stmt = stmt.order_by(DrawResult.is_backup, DrawResult.ordinal, DrawResult.id)
    return paginate(db, stmt, params.page, params.page_size)


def execute_draw(db: Session, draw_id: int) -> list[DrawResult]:
    draw = get_draw(db, draw_id)
    if draw.status == "completed":
        return list_results(db, draw.id)
    if draw.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Draw already completed or cancelled",
        )

    existing = db.execute(
        select(DrawResult.id).where(DrawResult.draw_id == draw.id)
    ).first()
    if existing:
        if draw.status != "completed":
            draw.status = "completed"
            db.commit()
        return list_results(db, draw.id)

    rule = None
    if draw.rule_id is not None:
        rule = RuleRepo(db).get_by_id(draw.rule_id)
    if rule is None:
        if draw.category_id is not None:
            if draw.subcategory_id is not None:
                rule = RuleRepo(db).get_active_by_category_and_subcategory_id(
                    draw.category_id, draw.subcategory_id
                )
            if rule is None:
                rule = RuleRepo(db).get_active_by_category_id(draw.category_id)
        elif draw.category:
            if draw.subcategory:
                rule = RuleRepo(db).get_active_by_category_and_subcategory(
                    draw.category, draw.subcategory
                )
            if rule is None:
                rule = RuleRepo(db).get_active_by_category(draw.category)
        if rule is not None:
            draw.rule_id = rule.id

    stmt = select(Expert).where(Expert.is_active.is_(True))
    if draw.category_id is not None:
        stmt = stmt.where(Expert.category_id == draw.category_id)
    elif draw.category:
        stmt = stmt.where(Expert.category == draw.category)
    if draw.subcategory_id is not None:
        stmt = stmt.where(Expert.subcategory_id == draw.subcategory_id)
    elif draw.subcategory:
        stmt = stmt.where(Expert.subcategory == draw.subcategory)
    if rule is not None and rule.title_required:
        stmt = stmt.where(Expert.title == rule.title_required)
    if rule is not None and rule.avoid_enabled and draw.review_location:
        stmt = stmt.where(
            or_(
                Expert.avoid_units.is_(None),
                ~Expert.avoid_units.contains(draw.review_location),
            )
        )

    candidates = list(db.execute(stmt).scalars().all())
    backup_count = draw.backup_count or 0
    total_needed = draw.expert_count + backup_count
    if len(candidates) < total_needed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough qualified experts",
        )

    method = resolve_draw_method(draw, rule)
    if method not in SUPPORTED_DRAW_METHODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported draw method",
        )
    chosen = pick_experts(candidates, total_needed, method)
    for index, expert in enumerate(chosen, start=1):
        is_backup = index > draw.expert_count
        result = DrawResult(
            draw_id=draw.id,
            expert_id=expert.id,
            is_backup=is_backup,
            ordinal=index,
        )
        db.add(result)

    draw.draw_method = method
    draw.status = "completed"
    db.commit()

    return list_results(db, draw.id)


def replace_draw_result(db: Session, draw_id: int, result_id: int) -> list[DrawResult]:
    draw = get_draw(db, draw_id)
    if draw.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Draw is not completed",
        )

    target = db.execute(
        select(DrawResult).where(
            DrawResult.draw_id == draw.id, DrawResult.id == result_id
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Result not found"
        )
    if target.is_backup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot replace a backup expert",
        )

    backup = (
        db.execute(
            select(DrawResult)
            .where(DrawResult.draw_id == draw.id, DrawResult.is_backup.is_(True))
            .order_by(DrawResult.ordinal, DrawResult.id)
        )
        .scalars()
        .first()
    )
    if backup is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backup experts available",
        )

    target_ordinal = target.ordinal
    db.delete(target)
    backup.is_backup = False
    backup.is_replacement = True
    if target_ordinal is not None:
        backup.ordinal = target_ordinal
    db.commit()

    return list_results(db, draw.id)
