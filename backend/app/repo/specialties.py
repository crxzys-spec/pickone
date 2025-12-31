from __future__ import annotations

from sqlalchemy import select

from app.models.specialty import Specialty
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class SpecialtyRepo(BaseRepo):
    def list(self) -> list[Specialty]:
        stmt = select(Specialty).order_by(Specialty.sort_order, Specialty.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        parent_id: int | None,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Specialty], int]:
        stmt = select(Specialty)
        if parent_id is not None:
            stmt = stmt.where(Specialty.parent_id == parent_id)
        stmt = apply_keyword(stmt, keyword, [Specialty.name, Specialty.code])
        sort_map = {
            "id": Specialty.id,
            "name": Specialty.name,
            "code": Specialty.code,
            "sort_order": Specialty.sort_order,
            "is_active": Specialty.is_active,
        }
        effective_sort = sort_by or "sort_order"
        stmt = apply_sort(stmt, effective_sort, sort_order, sort_map, Specialty.id)
        return paginate(self.db, stmt, page, page_size)

    def list_by_parent(self, parent_id: int | None) -> list[Specialty]:
        stmt = select(Specialty)
        if parent_id is None:
            stmt = stmt.where(Specialty.parent_id.is_(None))
        else:
            stmt = stmt.where(Specialty.parent_id == parent_id)
        stmt = stmt.order_by(Specialty.sort_order, Specialty.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, specialty_id: int) -> Specialty | None:
        stmt = select(Specialty).where(Specialty.id == specialty_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Specialty | None:
        stmt = select(Specialty).where(Specialty.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_parent_and_name(
        self, parent_id: int | None, name: str
    ) -> Specialty | None:
        stmt = select(Specialty).where(
            Specialty.parent_id == parent_id, Specialty.name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_parent_and_code(
        self, parent_id: int | None, code: str
    ) -> Specialty | None:
        stmt = select(Specialty).where(
            Specialty.parent_id == parent_id, Specialty.code == code
        )
        return self.db.execute(stmt).scalar_one_or_none()
