from __future__ import annotations

from sqlalchemy import select

from app.models.category import Category
from app.repo.base import BaseRepo


class CategoryRepo(BaseRepo):
    def list(self) -> list[Category]:
        stmt = select(Category).order_by(Category.sort_order, Category.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, category_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Category | None:
        stmt = select(Category).where(Category.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
