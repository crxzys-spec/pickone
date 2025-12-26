from __future__ import annotations

from sqlalchemy import select

from app.models.category import Category
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class CategoryRepo(BaseRepo):
    def list(self) -> list[Category]:
        stmt = select(Category).order_by(Category.sort_order, Category.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Category], int]:
        stmt = select(Category)
        stmt = apply_keyword(stmt, keyword, [Category.name, Category.code])
        sort_map = {
            "id": Category.id,
            "name": Category.name,
            "code": Category.code,
            "sort_order": Category.sort_order,
            "is_active": Category.is_active,
        }
        effective_sort = sort_by or "sort_order"
        stmt = apply_sort(stmt, effective_sort, sort_order, sort_map, Category.id)
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, category_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Category | None:
        stmt = select(Category).where(Category.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
