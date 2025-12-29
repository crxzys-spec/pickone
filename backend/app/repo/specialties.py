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
        subcategory_id: int | None,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Specialty], int]:
        stmt = select(Specialty)
        if subcategory_id is not None:
            stmt = stmt.where(Specialty.subcategory_id == subcategory_id)
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

    def list_by_subcategory(self, subcategory_id: int) -> list[Specialty]:
        stmt = (
            select(Specialty)
            .where(Specialty.subcategory_id == subcategory_id)
            .order_by(Specialty.sort_order, Specialty.id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, specialty_id: int) -> Specialty | None:
        stmt = select(Specialty).where(Specialty.id == specialty_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Specialty | None:
        stmt = select(Specialty).where(Specialty.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_subcategory_and_name(
        self, subcategory_id: int, name: str
    ) -> Specialty | None:
        stmt = select(Specialty).where(
            Specialty.subcategory_id == subcategory_id, Specialty.name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_subcategory_and_code(
        self, subcategory_id: int, code: str
    ) -> Specialty | None:
        stmt = select(Specialty).where(
            Specialty.subcategory_id == subcategory_id, Specialty.code == code
        )
        return self.db.execute(stmt).scalar_one_or_none()
