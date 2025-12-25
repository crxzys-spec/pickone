from __future__ import annotations

from sqlalchemy import select

from app.models.subcategory import Subcategory
from app.repo.base import BaseRepo


class SubcategoryRepo(BaseRepo):
    def list(self) -> list[Subcategory]:
        stmt = select(Subcategory).order_by(
            Subcategory.sort_order, Subcategory.id
        )
        return list(self.db.execute(stmt).scalars().all())

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
