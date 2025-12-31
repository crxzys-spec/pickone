from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.region import Region
from app.models.rule import Rule
from app.models.specialty import Specialty
from app.models.title import Title
from app.repo.rules import RuleRepo
from app.repo.specialties import SpecialtyRepo
from app.repo.titles import TitleRepo
from app.schemas.pagination import PageParams
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


def _load_specialty_names(db: Session, specialty_ids: list[int]) -> list[str]:
    if not specialty_ids:
        return []
    stmt = select(Specialty).where(Specialty.id.in_(specialty_ids))
    rows = db.execute(stmt).scalars().all()
    if len(rows) != len(set(specialty_ids)):
        existing = {spec.id for spec in rows}
        missing = [str(item) for item in specialty_ids if item not in existing]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialty not found: {', '.join(missing)}",
        )
    specialty_map = {spec.id: spec for spec in rows}
    return [specialty_map[item].name for item in specialty_ids if item in specialty_map]


def _derive_root_label(db: Session, specialty_ids: list[int]) -> str:
    if not specialty_ids:
        return "不限"
    items = SpecialtyRepo(db).list()
    name_map = {item.id: item.name for item in items}
    parent_map = {item.id: item.parent_id for item in items}

    def root_name(node_id: int) -> str | None:
        current = node_id
        while parent_map.get(current) is not None:
            current = parent_map[current]
        return name_map.get(current)

    roots = {root_name(item) for item in specialty_ids}
    roots.discard(None)
    if len(roots) == 1:
        return next(iter(roots))
    if roots:
        return "多专业"
    return "不限"


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


def _apply_specialty(rule: Rule, db: Session, specialty_ids: list[int]) -> None:
    names = _load_specialty_names(db, specialty_ids)
    rule.specialty_ids = specialty_ids
    rule.specialty_id = specialty_ids[0] if len(specialty_ids) == 1 else None
    rule.specialty = _join_names(names)
    rule.category_id = None
    rule.category = _derive_root_label(db, specialty_ids)
    rule.subcategory_id = None
    rule.subcategory = None


def create_rule(db: Session, payload: RuleCreate) -> Rule:
    data = payload.model_dump()
    specialty_ids = _normalize_ids(data.get("specialty_ids"))
    title_required_ids = _normalize_ids(data.get("title_required_ids"))
    region_required_ids = _normalize_ids(data.get("region_required_ids"))
    if not region_required_ids and data.get("region_required_id") is not None:
        region_required_ids = _normalize_ids([data.get("region_required_id")])

    rule = Rule(**data)
    _apply_specialty(rule, db, specialty_ids)

    title_names = _load_titles(db, title_required_ids)
    rule.title_required_ids = title_required_ids
    rule.title_required = _join_names(title_names)

    region_names = _load_regions(db, region_required_ids)
    rule.region_required_ids = region_required_ids
    rule.region_required_id = (
        region_required_ids[0] if len(region_required_ids) == 1 else None
    )
    rule.region_required = _join_names(region_names)

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: int, payload: RuleUpdate) -> Rule:
    rule = get_rule(db, rule_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "specialty_ids" in update_data:
        specialty_ids = _normalize_ids(update_data.get("specialty_ids"))
        _apply_specialty(rule, db, specialty_ids)

    if "title_required_ids" in update_data:
        title_required_ids = _normalize_ids(update_data.get("title_required_ids"))
        title_names = _load_titles(db, title_required_ids)
        rule.title_required_ids = title_required_ids
        rule.title_required = _join_names(title_names)

    if "region_required_ids" in update_data or "region_required_id" in update_data:
        region_required_ids = _normalize_ids(update_data.get("region_required_ids"))
        if not region_required_ids and update_data.get("region_required_id") is not None:
            region_required_ids = _normalize_ids([update_data.get("region_required_id")])
        region_names = _load_regions(db, region_required_ids)
        rule.region_required_ids = region_required_ids
        rule.region_required_id = (
            region_required_ids[0] if len(region_required_ids) == 1 else None
        )
        rule.region_required = _join_names(region_names)

    for key, value in update_data.items():
        if key in {
            "specialty_ids",
            "title_required_ids",
            "region_required_id",
            "region_required_ids",
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

