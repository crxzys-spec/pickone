from __future__ import annotations

from sqlalchemy import select

from app.models.organization import Organization
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class OrganizationRepo(BaseRepo):
    def list(self) -> list[Organization]:
        stmt = select(Organization).order_by(Organization.sort_order, Organization.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Organization], int]:
        stmt = select(Organization)
        stmt = apply_keyword(stmt, keyword, [Organization.name, Organization.code])
        sort_map = {
            "id": Organization.id,
            "name": Organization.name,
            "code": Organization.code,
            "sort_order": Organization.sort_order,
            "is_active": Organization.is_active,
        }
        effective_sort = sort_by or "sort_order"
        stmt = apply_sort(
            stmt, effective_sort, sort_order, sort_map, Organization.id
        )
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, organization_id: int) -> Organization | None:
        stmt = select(Organization).where(Organization.id == organization_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Organization | None:
        stmt = select(Organization).where(Organization.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Organization | None:
        stmt = select(Organization).where(Organization.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
