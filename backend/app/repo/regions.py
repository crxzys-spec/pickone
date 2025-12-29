from __future__ import annotations

from sqlalchemy import select

from app.models.region import Region
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class RegionRepo(BaseRepo):
    def list(self) -> list[Region]:
        stmt = select(Region).order_by(Region.sort_order, Region.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Region], int]:
        stmt = select(Region)
        stmt = apply_keyword(stmt, keyword, [Region.name, Region.code])
        sort_map = {
            "id": Region.id,
            "name": Region.name,
            "code": Region.code,
            "sort_order": Region.sort_order,
            "is_active": Region.is_active,
        }
        effective_sort = sort_by or "sort_order"
        stmt = apply_sort(stmt, effective_sort, sort_order, sort_map, Region.id)
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, region_id: int) -> Region | None:
        stmt = select(Region).where(Region.id == region_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Region | None:
        stmt = select(Region).where(Region.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Region | None:
        stmt = select(Region).where(Region.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
