from __future__ import annotations

from sqlalchemy import select

from app.models.rule import Rule
from app.repo.base import BaseRepo


class RuleRepo(BaseRepo):
    def list(self) -> list[Rule]:
        stmt = select(Rule).order_by(Rule.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, rule_id: int) -> Rule | None:
        stmt = select(Rule).where(Rule.id == rule_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_by_category(self, category: str) -> Rule | None:
        stmt = (
            select(Rule)
            .where(Rule.category == category, Rule.is_active.is_(True))
            .order_by(Rule.id.desc())
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_by_category_id(self, category_id: int) -> Rule | None:
        stmt = (
            select(Rule)
            .where(Rule.category_id == category_id, Rule.is_active.is_(True))
            .order_by(Rule.id.desc())
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_by_category_and_subcategory_id(
        self, category_id: int, subcategory_id: int
    ) -> Rule | None:
        stmt = (
            select(Rule)
            .where(
                Rule.category_id == category_id,
                Rule.subcategory_id == subcategory_id,
                Rule.is_active.is_(True),
            )
            .order_by(Rule.id.desc())
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_by_category_and_subcategory(
        self, category: str, subcategory: str
    ) -> Rule | None:
        stmt = (
            select(Rule)
            .where(
                Rule.category == category,
                Rule.subcategory == subcategory,
                Rule.is_active.is_(True),
            )
            .order_by(Rule.id.desc())
        )
        return self.db.execute(stmt).scalar_one_or_none()
