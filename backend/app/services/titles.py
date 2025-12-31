from __future__ import annotations

from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.expert import Expert
from app.models.rule import Rule
from app.models.title import Title
from app.repo.titles import TitleRepo
from app.schemas.pagination import PageParams
from app.schemas.title import TitleCreate, TitleUpdate


def _generate_unique_code(repo: TitleRepo) -> str:
    code = generate_code(prefix="title")
    while repo.get_by_code(code):
        code = generate_code(prefix="title")
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


def _sort_key(item: Title) -> tuple[int, str, str, int]:
    code = (item.code or "").strip()
    name = item.name.strip()
    return (item.sort_order, code, name, item.id)


def _build_tree(items: list[Title]) -> list[dict[str, object]]:
    nodes: dict[int, dict[str, object]] = {}
    children_map: dict[int | None, list[Title]] = defaultdict(list)
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


def list_titles(db: Session, params: PageParams) -> tuple[list[Title], int]:
    return TitleRepo(db).list_page(
        None,
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def list_titles_all(db: Session) -> list[Title]:
    return TitleRepo(db).list()


def list_title_tree(db: Session) -> list[TitleTreeOut]:
    items = TitleRepo(db).list()
    return _build_tree(items)


def get_title(db: Session, title_id: int) -> Title:
    title = TitleRepo(db).get_by_id(title_id)
    if title is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Title not found"
        )
    return title


def _ensure_unique_code(
    db: Session, code: str | None, exclude_id: int | None = None
) -> None:
    if not code:
        return
    repo = TitleRepo(db)
    existing = repo.get_by_code(code)
    if existing and existing.id != exclude_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title code already exists",
        )


def _validate_parent(db: Session, parent_id: int | None, node_id: int | None = None) -> None:
    if parent_id is None:
        return
    parent = TitleRepo(db).get_by_id(parent_id)
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent title not found"
        )
    if node_id is None:
        return
    parents = {item.id: item.parent_id for item in TitleRepo(db).list()}
    current = parent_id
    while current is not None:
        if current == node_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set parent to descendant",
            )
        current = parents.get(current)


def create_title(db: Session, payload: TitleCreate) -> Title:
    data = payload.model_dump()
    code = data.get("code")
    if code:
        code = code.strip()
    if not code:
        code = _generate_unique_code(TitleRepo(db))
    data["code"] = code
    _ensure_unique_code(db, code)
    _validate_parent(db, data.get("parent_id"))

    title = Title(**data)
    db.add(title)
    db.commit()
    db.refresh(title)
    return title


def update_title(db: Session, title_id: int, payload: TitleUpdate) -> Title:
    title = get_title(db, title_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = update_data["code"].strip() if update_data.get("code") else None
    if "code" in update_data and not update_data.get("code"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title code is required",
        )
    _ensure_unique_code(db, update_data.get("code"), exclude_id=title_id)
    if "parent_id" in update_data:
        _validate_parent(db, update_data.get("parent_id"), node_id=title_id)

    old_name = title.name
    name_changed = "name" in update_data and update_data["name"] != title.name
    for key, value in update_data.items():
        setattr(title, key, value)

    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.title_id == title_id)
            .values(title=title.name)
        )
        db.execute(
            Expert.__table__.update()
            .where(Expert.title_id.is_(None), Expert.title == old_name)
            .values(title=title.name)
        )

    db.commit()
    db.refresh(title)
    return title


def _collect_descendant_ids(items: list[Title], target_ids: list[int]) -> list[int]:
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


def _cleanup_rules_for_titles(db: Session, title_ids: set[int]) -> None:
    if not title_ids:
        return
    rules = db.execute(select(Rule)).scalars().all()
    if not rules:
        return
    titles = {item.id: item for item in TitleRepo(db).list()}
    for rule in rules:
        current = _normalize_ids(rule.title_required_ids)
        if not current:
            continue
        if not title_ids.intersection(current):
            continue
        remaining = [item for item in current if item not in title_ids]
        rule.title_required_ids = remaining
        names = [titles[item].name for item in remaining if item in titles]
        rule.title_required = ";".join(names) if names else None


def delete_title(db: Session, title_id: int) -> None:
    items = TitleRepo(db).list()
    existing = {item.id for item in items}
    if title_id not in existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")
    to_delete = _collect_descendant_ids(items, [title_id])
    delete_ids = set(to_delete)

    db.execute(
        Expert.__table__.update()
        .where(Expert.title_id.in_(delete_ids))
        .values(title_id=None, title=None)
    )
    _cleanup_rules_for_titles(db, delete_ids)
    db.execute(delete(Title).where(Title.id.in_(delete_ids)))
    db.commit()


def delete_titles(db: Session, title_ids: list[int]) -> dict[str, int]:
    unique_ids = _normalize_ids(title_ids)
    if not unique_ids:
        return {"deleted": 0, "skipped": 0}

    deleted = 0
    skipped = 0
    for title_id in set(unique_ids):
        try:
            delete_title(db, title_id)
            deleted += 1
        except HTTPException:
            db.rollback()
            skipped += 1
        except Exception:
            db.rollback()
            raise
    return {"deleted": deleted, "skipped": skipped}


def batch_titles(
    db: Session, action: str, title_ids: list[int]
) -> dict[str, int | list[dict[str, object]]]:
    items = TitleRepo(db).list()
    existing = {item.id for item in items}
    unique_ids = [item for item in _normalize_ids(title_ids) if item in existing]
    if not unique_ids:
        return {"updated": 0, "deleted": 0, "skipped": len(set(title_ids)), "errors": []}

    if action in {"enable", "disable"}:
        is_active = action == "enable"
        target_ids = set(_collect_descendant_ids(items, unique_ids))
        db.execute(
            Title.__table__.update()
            .where(Title.id.in_(target_ids))
            .values(is_active=is_active)
        )
        db.commit()
        return {"updated": len(target_ids), "deleted": 0, "skipped": 0, "errors": []}

    if action == "delete":
        target_ids = set(_collect_descendant_ids(items, unique_ids))
        db.execute(
            Expert.__table__.update()
            .where(Expert.title_id.in_(target_ids))
            .values(title_id=None, title=None)
        )
        _cleanup_rules_for_titles(db, target_ids)
        db.execute(delete(Title).where(Title.id.in_(target_ids)))
        db.commit()
        return {"updated": 0, "deleted": len(target_ids), "skipped": 0, "errors": []}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")


def resolve_title(
    db: Session,
    title_id: int | None,
    title_name: str | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Title | None:
    repo = TitleRepo(db)
    title = None
    if title_id is not None:
        title = repo.get_by_id(title_id)
        if title is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found",
            )
    elif title_name:
        title = repo.get_by_name(title_name)
        if title is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found",
            )
        if title is None and create_if_missing:
            title = Title(
                name=title_name,
                code=_generate_unique_code(repo),
                is_active=True,
                sort_order=0,
            )
            db.add(title)
            db.flush()
    return title


def expand_to_leaf_ids(db: Session, selected_ids: list[int]) -> list[int]:
    normalized = _normalize_ids(selected_ids)
    if not normalized:
        return []
    items = TitleRepo(db).list()
    existing = {item.id for item in items}
    missing = [str(item) for item in normalized if item not in existing]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title not found: {', '.join(missing)}",
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


def ensure_leaf_ids(db: Session, title_ids: list[int]) -> None:
    normalized = _normalize_ids(title_ids)
    if not normalized:
        return
    items = TitleRepo(db).list()
    existing = {item.id for item in items}
    missing = [str(item) for item in normalized if item not in existing]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title not found: {', '.join(missing)}",
        )
    children_map: dict[int | None, list[int]] = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item.id)
    non_leaf = [item for item in normalized if children_map.get(item)]
    if non_leaf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be a leaf",
        )
