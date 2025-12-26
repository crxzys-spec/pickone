from __future__ import annotations

from typing import Iterable

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement


def apply_keyword(
    stmt: Select, keyword: str | None, columns: Iterable[ColumnElement]
) -> Select:
    if not keyword:
        return stmt
    key = keyword.strip()
    if not key:
        return stmt
    pattern = f"%{key}%"
    filters = [column.ilike(pattern) for column in columns]
    if not filters:
        return stmt
    return stmt.where(or_(*filters))


def apply_sort(
    stmt: Select,
    sort_by: str | None,
    sort_order: str,
    mapping: dict[str, ColumnElement],
    default: ColumnElement,
) -> Select:
    column = mapping.get(sort_by or "")
    if column is None:
        column = default
    is_desc = sort_order.lower() == "desc"
    if column is default:
        return stmt.order_by(column.desc() if is_desc else column.asc())
    direction = column.desc() if is_desc else column.asc()
    return stmt.order_by(direction, default.asc())


def paginate(
    db: Session, stmt: Select, page: int, page_size: int
) -> tuple[list, int]:
    total_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.execute(total_stmt).scalar_one()
    items = (
        db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return list(items), total
