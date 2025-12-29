from __future__ import annotations

from sqlalchemy import select

from app.models.subcategory import Subcategory
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class SubcategoryRepo(BaseRepo):
    def list(self) -> list[Subcategory]:
        stmt = select(Subcategory).order_by(
            Subcategory.sort_order, Subcategory.id
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        category_id: int | None,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Subcategory], int]:
        stmt = select(Subcategory)
        if category_id is not None:
            stmt = stmt.where(Subcategory.category_id == category_id)
        stmt = apply_keyword(stmt, keyword, [Subcategory.name, Subcategory.code])
        sort_map = {
            "id": Subcategory.id,
            "name": Subcategory.name,
            "code": Subcategory.code,
            "sort_order": Subcategory.sort_order,
            "is_active": Subcategory.is_active,
        }
        effective_sort = sort_by or "sort_order"
        stmt = apply_sort(stmt, effective_sort, sort_order, sort_map, Subcategory.id)
        return paginate(self.db, stmt, page, page_size)

    def list_by_category(self, category_id: int) -> list[Subcategory]:
        stmt = (
            select(Subcategory)
            .where(Subcategory.category_id == category_id)
            .order_by(Subcategory.sort_order, Subcategory.id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, subcategory_id: int) -> Subcategory | None:
        stmt = select(Subcategory).where(Subcategory.id == subcategory_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_category_and_name(self, category_id: int, name: str) -> Subcategory | None:
        stmt = select(Subcategory).where(
            Subcategory.category_id == category_id, Subcategory.name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_category_and_code(
        self, category_id: int, code: str
    ) -> Subcategory | None:
        stmt = select(Subcategory).where(
            Subcategory.category_id == category_id, Subcategory.code == code
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Subcategory | None:
        stmt = select(Subcategory).where(Subcategory.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
