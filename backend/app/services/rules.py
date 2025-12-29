from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.region import Region
from app.models.specialty import Specialty
from app.models.subcategory import Subcategory
from app.models.title import Title
from app.models.rule import Rule
from app.repo.rules import RuleRepo
from app.schemas.pagination import PageParams
from app.services import categories as category_service
from app.services import specialties as specialty_service
from app.services import regions as region_service
from app.schemas.rule import RuleCreate, RuleUpdate


def list_rules(db: Session, params: PageParams) -> tuple[list[Rule], int]:
    return RuleRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def list_rules_all(db: Session) -> list[Rule]:
    return RuleRepo(db).list()


def get_rule(db: Session, rule_id: int) -> Rule:
    rule = RuleRepo(db).get_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


def _normalize_ids(values: list[int] | None) -> list[int]:
    unique: list[int] = []
    for item in values or []:
        try:
            value = int(item)
        except (TypeError, ValueError):
            continue
        if value not in unique:
            unique.append(value)
    return unique


def _join_names(names: list[str]) -> str | None:
    return ";".join(names) if names else None


def _load_specialty_meta(
    db: Session, specialty_ids: list[int]
) -> tuple[list[str], Category | None, Subcategory | None]:
    if not specialty_ids:
        return [], None, None

    stmt = (
        select(Specialty, Subcategory, Category)
        .join(Subcategory, Subcategory.id == Specialty.subcategory_id)
        .join(Category, Category.id == Subcategory.category_id)
        .where(Specialty.id.in_(specialty_ids))
    )
    rows = db.execute(stmt).all()
    if len(rows) != len(set(specialty_ids)):
        existing = {spec.id for spec, _sub, _cat in rows}
        missing = [str(item) for item in specialty_ids if item not in existing]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialty not found: {', '.join(missing)}",
        )
    specialty_map = {spec.id: (spec, sub, cat) for spec, sub, cat in rows}
    names = [specialty_map[item][0].name for item in specialty_ids if item in specialty_map]
    category_map = {cat.id: cat for _spec, _sub, cat in specialty_map.values()}
    subcategory_map = {sub.id: sub for _spec, sub, _cat in specialty_map.values()}
    category = next(iter(category_map.values())) if len(category_map) == 1 else None
    subcategory = (
        next(iter(subcategory_map.values())) if len(subcategory_map) == 1 else None
    )
    return names, category, subcategory


def _load_titles(db: Session, title_ids: list[int]) -> list[str]:
    if not title_ids:
        return []
    stmt = select(Title).where(Title.id.in_(title_ids))
    rows = db.execute(stmt).scalars().all()
    if len(rows) != len(set(title_ids)):
        existing = {title.id for title in rows}
        missing = [str(item) for item in title_ids if item not in existing]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title not found: {', '.join(missing)}",
        )
    title_map = {title.id: title for title in rows}
    return [title_map[item].name for item in title_ids if item in title_map]


def _load_regions(db: Session, region_ids: list[int]) -> list[str]:
    if not region_ids:
        return []
    stmt = select(Region).where(Region.id.in_(region_ids))
    rows = db.execute(stmt).scalars().all()
    if len(rows) != len(set(region_ids)):
        existing = {region.id for region in rows}
        missing = [str(item) for item in region_ids if item not in existing]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region not found: {', '.join(missing)}",
        )
    region_map = {region.id: region for region in rows}
    return [region_map[item].name for item in region_ids if item in region_map]


def create_rule(db: Session, payload: RuleCreate) -> Rule:
    data = payload.model_dump()
    category = None
    subcategory = None
    specialty = None
    specialty_ids = _normalize_ids(data.get("specialty_ids"))
    title_required_ids = _normalize_ids(data.get("title_required_ids"))
    region_required_ids = _normalize_ids(data.get("region_required_ids"))
    if not region_required_ids and data.get("region_required_id") is not None:
        region_required_ids = _normalize_ids([data.get("region_required_id")])

    specialty_id = data.get("specialty_id")
    specialty_name = data.get("specialty")
    subcategory_id = data.get("subcategory_id")
    subcategory_name = data.get("subcategory")
    category_id = data.get("category_id")
    category_name = data.get("category")
    region_required_name = data.get("region_required")

    specialty_names: list[str] = []
    if specialty_ids:
        specialty_names, category, subcategory = _load_specialty_meta(db, specialty_ids)
    else:
        if specialty_id is not None or specialty_name:
            if subcategory_id is not None or subcategory_name:
                category = category_service.resolve_category(
                    db, category_id, category_name
                )
                if category is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Category is required",
                    )
                subcategory = category_service.resolve_subcategory(
                    db, subcategory_id, subcategory_name, category
                )
            if specialty_id is not None:
                specialty = specialty_service.get_specialty(db, specialty_id)
                if subcategory and specialty.subcategory_id != subcategory.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Specialty does not belong to subcategory",
                    )
            else:
                if subcategory is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Subcategory is required for specialty",
                    )
                specialty = specialty_service.resolve_specialty(
                    db, None, specialty_name, subcategory.id
                )
            if subcategory is None and specialty is not None:
                subcategory = category_service.get_subcategory(
                    db, specialty.subcategory_id
                )
            if category is None and subcategory is not None:
                category = category_service.get_category(db, subcategory.category_id)
            if specialty:
                specialty_ids = [specialty.id]
                specialty_names = [specialty.name]
        else:
            category = category_service.resolve_category(db, category_id, category_name)
            if category is None and (category_id is not None or category_name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category is required",
                )
            if subcategory_id is not None or subcategory_name:
                subcategory = category_service.resolve_subcategory(
                    db, subcategory_id, subcategory_name, category
                )

    rule = Rule(**data)
    rule.specialty_ids = specialty_ids
    rule.specialty_id = specialty_ids[0] if len(specialty_ids) == 1 else None
    rule.specialty = _join_names(specialty_names)
    if category:
        rule.category_id = category.id
        rule.category = category.name
    else:
        rule.category_id = None
        rule.category = "多专业" if specialty_names else "不限"
    if subcategory:
        rule.subcategory_id = subcategory.id
        rule.subcategory = subcategory.name
    else:
        rule.subcategory_id = None
        rule.subcategory = None

    title_names = _load_titles(db, title_required_ids)
    if title_required_ids:
        rule.title_required_ids = title_required_ids
        rule.title_required = _join_names(title_names)
    else:
        rule.title_required_ids = []
        rule.title_required = data.get("title_required")

    region_names = _load_regions(db, region_required_ids)
    if region_required_ids:
        rule.region_required_ids = region_required_ids
        rule.region_required_id = (
            region_required_ids[0] if len(region_required_ids) == 1 else None
        )
        rule.region_required = _join_names(region_names)
    else:
        rule.region_required_ids = []
        rule.region_required_id = None
        rule.region_required = region_required_name

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
    specialty_input = "specialty_id" in update_data or "specialty" in update_data
    specialty_ids_input = "specialty_ids" in update_data
    title_ids_input = "title_required_ids" in update_data
    region_input = (
        "region_required_id" in update_data or "region_required" in update_data
    )
    region_ids_input = "region_required_ids" in update_data

    category = None
    subcategory = None
    specialty = None

    if specialty_ids_input:
        specialty_ids = _normalize_ids(update_data.get("specialty_ids"))
        specialty_names, category, subcategory = _load_specialty_meta(
            db, specialty_ids
        )
        rule.specialty_ids = specialty_ids
        rule.specialty_id = specialty_ids[0] if len(specialty_ids) == 1 else None
        rule.specialty = _join_names(specialty_names)
        if category:
            rule.category_id = category.id
            rule.category = category.name
        else:
            rule.category_id = None
            rule.category = "多专业" if specialty_names else "不限"
        if subcategory:
            rule.subcategory_id = subcategory.id
            rule.subcategory = subcategory.name
        else:
            rule.subcategory_id = None
            rule.subcategory = None

    if category_input:
        category = category_service.resolve_category(
            db, update_data.get("category_id"), update_data.get("category")
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required",
            )
    elif subcategory_input or specialty_input:
        category = category_service.resolve_category(
            db, rule.category_id, rule.category, strict=False
        )

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

    if specialty_input:
        specialty_id = update_data.get("specialty_id")
        specialty_name = update_data.get("specialty")
        if specialty_id is None and specialty_name is None:
            rule.specialty_id = None
            rule.specialty = None
        else:
            if specialty_id is not None:
                specialty = specialty_service.get_specialty(db, specialty_id)
                if subcategory and specialty.subcategory_id != subcategory.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Specialty does not belong to subcategory",
                    )
            else:
                if subcategory is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Subcategory is required for specialty",
                    )
                specialty = specialty_service.resolve_specialty(
                    db, None, specialty_name, subcategory.id
                )
            if subcategory is None and specialty is not None:
                subcategory = category_service.get_subcategory(
                    db, specialty.subcategory_id
                )
            if category is None and subcategory is not None:
                category = category_service.get_category(
                    db, subcategory.category_id
                )
        if specialty is not None:
            rule.specialty_ids = [specialty.id]
        elif specialty_input and not specialty_ids_input:
            rule.specialty_ids = []

    if title_ids_input:
        title_required_ids = _normalize_ids(update_data.get("title_required_ids"))
        title_names = _load_titles(db, title_required_ids)
        rule.title_required_ids = title_required_ids
        rule.title_required = _join_names(title_names)
    elif "title_required" in update_data:
        rule.title_required = update_data.get("title_required")
        rule.title_required_ids = []

    if region_ids_input:
        region_required_ids = _normalize_ids(update_data.get("region_required_ids"))
        region_names = _load_regions(db, region_required_ids)
        rule.region_required_ids = region_required_ids
        rule.region_required_id = (
            region_required_ids[0] if len(region_required_ids) == 1 else None
        )
        rule.region_required = _join_names(region_names)
    elif region_input:
        region_required_ids = _normalize_ids(update_data.get("region_required_ids"))
        if not region_required_ids and update_data.get("region_required_id") is not None:
            region_required_ids = _normalize_ids(
                [update_data.get("region_required_id")]
            )
        if region_required_ids:
            region_names = _load_regions(db, region_required_ids)
            rule.region_required_ids = region_required_ids
            rule.region_required_id = (
                region_required_ids[0] if len(region_required_ids) == 1 else None
            )
            rule.region_required = _join_names(region_names)
        else:
            region = region_service.resolve_region(
                db,
                update_data.get("region_required_id"),
                update_data.get("region_required"),
                strict=update_data.get("region_required_id") is not None,
            )
            if region:
                rule.region_required_ids = [region.id]
                rule.region_required_id = region.id
                rule.region_required = region.name
            else:
                rule.region_required_ids = []
                rule.region_required_id = None
                rule.region_required = update_data.get("region_required")

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
    if (category_input or subcategory_input) and not specialty_input:
        rule.specialty_id = None
        rule.specialty = None
        if not specialty_ids_input:
            rule.specialty_ids = []
    if specialty_input and specialty is not None:
        rule.specialty_id = specialty.id
        rule.specialty = specialty.name

    for key, value in update_data.items():
        if key in {
            "category_id",
            "category",
            "subcategory_id",
            "subcategory",
            "specialty_id",
            "specialty",
            "specialty_ids",
            "region_required_id",
            "region_required",
            "region_required_ids",
            "title_required_ids",
        }:
            continue
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int) -> None:
    rule = get_rule(db, rule_id)
    db.delete(rule)
    db.commit()
