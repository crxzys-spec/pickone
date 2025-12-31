from __future__ import annotations

from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.expert_specialty import ExpertSpecialty
from app.models.rule import Rule
from app.models.specialty import Specialty
from app.repo.specialties import SpecialtyRepo
from app.schemas.pagination import PageParams
from app.schemas.specialty import SpecialtyCreate, SpecialtyUpdate


def _generate_unique_code(repo: SpecialtyRepo, prefix: str) -> str:
    code = generate_code(prefix=prefix)
    while repo.get_by_code(code):
        code = generate_code(prefix=prefix)
    return code


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


def _sort_key(item: Specialty) -> tuple[int, str, str, int]:
    code = (item.code or "").strip()
    name = item.name.strip()
    return (item.sort_order, code, name, item.id)


def _build_tree(items: list[Specialty]) -> list[dict[str, object]]:
    nodes: dict[int, dict[str, object]] = {}
    children_map: dict[int | None, list[Specialty]] = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item)

    for item in items:
        nodes[item.id] = {
            "id": item.id,
            "parent_id": item.parent_id,
            "name": item.name,
            "code": item.code,
            "is_active": item.is_active,
            "sort_order": item.sort_order,
            "children": [],
        }

    def attach_children(parent_id: int | None) -> list[dict[str, object]]:
        children = sorted(children_map.get(parent_id, []), key=_sort_key)
        result: list[dict[str, object]] = []
        for child in children:
            node = nodes[child.id]
            node["children"] = attach_children(child.id)
            result.append(node)
        return result

    return attach_children(None)


def list_specialties(db: Session, params: PageParams) -> tuple[list[Specialty], int]:
    return SpecialtyRepo(db).list_page(
        None,
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def list_specialties_all(db: Session) -> list[Specialty]:
    return SpecialtyRepo(db).list()


def list_specialty_tree(db: Session) -> list[SpecialtyTreeOut]:
    items = SpecialtyRepo(db).list()
    return _build_tree(items)


def get_specialty(db: Session, specialty_id: int) -> Specialty:
    specialty = SpecialtyRepo(db).get_by_id(specialty_id)
    if specialty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specialty not found"
        )
    return specialty


def _ensure_unique(
    db: Session, code: str | None, exclude_id: int | None = None
) -> None:
    if not code:
        return
    repo = SpecialtyRepo(db)
    existing = repo.get_by_code(code)
    if existing and existing.id != exclude_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty code already exists",
        )


def _validate_parent(db: Session, parent_id: int | None, node_id: int | None = None) -> None:
    if parent_id is None:
        return
    parent = SpecialtyRepo(db).get_by_id(parent_id)
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent specialty not found"
        )
    if node_id is None:
        return
    parents = {item.id: item.parent_id for item in SpecialtyRepo(db).list()}
    current = parent_id
    while current is not None:
        if current == node_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set parent to descendant",
            )
        current = parents.get(current)


def create_specialty(db: Session, payload: SpecialtyCreate) -> Specialty:
    data = payload.model_dump()
    code = data.get("code")
    if code:
        code = code.strip()
    if not code:
        code = _generate_unique_code(SpecialtyRepo(db), "spec")
    data["code"] = code
    _ensure_unique(db, code)
    _validate_parent(db, data.get("parent_id"))

    specialty = Specialty(**data)
    db.add(specialty)
    db.commit()
    db.refresh(specialty)
    return specialty


def update_specialty(db: Session, specialty_id: int, payload: SpecialtyUpdate) -> Specialty:
    specialty = get_specialty(db, specialty_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = update_data["code"].strip() if update_data.get("code") else None
    if "code" in update_data and not update_data.get("code"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty code is required",
        )
    _ensure_unique(db, update_data.get("code"), exclude_id=specialty_id)
    if "parent_id" in update_data:
        _validate_parent(db, update_data.get("parent_id"), node_id=specialty_id)

    for key, value in update_data.items():
        setattr(specialty, key, value)

    db.commit()
    db.refresh(specialty)
    return specialty


def _collect_descendant_ids(items: list[Specialty], target_ids: list[int]) -> list[int]:
    children_map: dict[int | None, list[int]] = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item.id)
    seen: set[int] = set()
    ordered: list[int] = []

    def walk(node_id: int) -> None:
        if node_id in seen:
            return
        seen.add(node_id)
        ordered.append(node_id)
        for child_id in children_map.get(node_id, []):
            walk(child_id)

    for node_id in target_ids:
        walk(node_id)

    return ordered


def _cleanup_rules_for_specialties(db: Session, specialty_ids: set[int]) -> None:
    if not specialty_ids:
        return
    rules = db.execute(select(Rule)).scalars().all()
    if not rules:
        return
    specialties = {item.id: item for item in SpecialtyRepo(db).list()}
    for rule in rules:
        current = _normalize_ids(rule.specialty_ids)
        if not current:
            continue
        if not specialty_ids.intersection(current):
            continue
        remaining = [item for item in current if item not in specialty_ids]
        rule.specialty_ids = remaining
        names = [specialties[item].name for item in remaining if item in specialties]
        rule.specialty = ";".join(names) if names else None
        rule.specialty_id = remaining[0] if len(remaining) == 1 else None


def delete_specialty(db: Session, specialty_id: int) -> None:
    items = SpecialtyRepo(db).list()
    existing = {item.id for item in items}
    if specialty_id not in existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialty not found")
    to_delete = _collect_descendant_ids(items, [specialty_id])
    delete_ids = set(to_delete)

    db.execute(
        delete(ExpertSpecialty).where(ExpertSpecialty.specialty_id.in_(delete_ids))
    )
    _cleanup_rules_for_specialties(db, delete_ids)
    db.execute(delete(Specialty).where(Specialty.id.in_(delete_ids)))
    db.commit()


def batch_specialties(
    db: Session, action: str, specialty_ids: list[int]
) -> dict[str, int | list[dict[str, object]]]:
    items = SpecialtyRepo(db).list()
    existing = {item.id for item in items}
    unique_ids = [item for item in _normalize_ids(specialty_ids) if item in existing]
    if not unique_ids:
        return {"updated": 0, "deleted": 0, "skipped": len(set(specialty_ids)), "errors": []}

    if action in {"enable", "disable"}:
        is_active = action == "enable"
        target_ids = set(_collect_descendant_ids(items, unique_ids))
        db.execute(
            Specialty.__table__.update()
            .where(Specialty.id.in_(target_ids))
            .values(is_active=is_active)
        )
        db.commit()
        return {"updated": len(target_ids), "deleted": 0, "skipped": 0, "errors": []}

    if action == "delete":
        target_ids = set(_collect_descendant_ids(items, unique_ids))
        db.execute(
            delete(ExpertSpecialty).where(ExpertSpecialty.specialty_id.in_(target_ids))
        )
        _cleanup_rules_for_specialties(db, target_ids)
        db.execute(delete(Specialty).where(Specialty.id.in_(target_ids)))
        db.commit()
        return {"updated": 0, "deleted": len(target_ids), "skipped": 0, "errors": []}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")


def resolve_specialty_by_code(db: Session, code: str) -> Specialty | None:
    return SpecialtyRepo(db).get_by_code(code)


def expand_to_leaf_ids(db: Session, selected_ids: list[int]) -> list[int]:
    normalized = _normalize_ids(selected_ids)
    if not normalized:
        return []
    items = SpecialtyRepo(db).list()
    existing = {item.id for item in items}
    missing = [str(item) for item in normalized if item not in existing]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialty not found: {', '.join(missing)}",
        )
    children_map: dict[int | None, list[int]] = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item.id)
    leaf_ids: set[int] = set()

    def walk(node_id: int) -> None:
        children = children_map.get(node_id, [])
        if not children:
            leaf_ids.add(node_id)
            return
        for child_id in children:
            walk(child_id)

    for node_id in normalized:
        walk(node_id)

    return list(leaf_ids)


def ensure_leaf_ids(db: Session, specialty_ids: list[int]) -> None:
    normalized = _normalize_ids(specialty_ids)
    if not normalized:
        return
    items = SpecialtyRepo(db).list()
    existing = {item.id for item in items}
    missing = [str(item) for item in normalized if item not in existing]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialty not found: {', '.join(missing)}",
        )
    children_map: dict[int | None, list[int]] = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item.id)
    non_leaf = [item for item in normalized if children_map.get(item)]
    if non_leaf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty must be a leaf",
        )
