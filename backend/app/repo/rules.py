from __future__ import annotations

from sqlalchemy import select

from app.models.rule import Rule
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class RuleRepo(BaseRepo):
    def list(self) -> list[Rule]:
        stmt = select(Rule).order_by(Rule.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Rule], int]:
        stmt = select(Rule)
        stmt = apply_keyword(
            stmt,
            keyword,
            [
                Rule.name,
                Rule.category,
                Rule.subcategory,
                Rule.specialty,
                Rule.region_required,
            ],
        )
        sort_map = {
            "id": Rule.id,
            "name": Rule.name,
            "category": Rule.category,
            "subcategory": Rule.subcategory,
            "specialty": Rule.specialty,
            "title_required": Rule.title_required,
            "region_required": Rule.region_required,
            "draw_method": Rule.draw_method,
            "is_active": Rule.is_active,
        }
        stmt = apply_sort(stmt, sort_by, sort_order, sort_map, Rule.id)
        return paginate(self.db, stmt, page, page_size)

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

    def get_active_by_specialty_id(self, specialty_id: int) -> Rule | None:
        stmt = (
            select(Rule)
            .where(Rule.specialty_id == specialty_id, Rule.is_active.is_(True))
            .order_by(Rule.id.desc())
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_by_specialty(self, specialty: str) -> Rule | None:
        stmt = (
            select(Rule)
            .where(Rule.specialty == specialty, Rule.is_active.is_(True))
            .order_by(Rule.id.desc())
        )
        return self.db.execute(stmt).scalar_one_or_none()
