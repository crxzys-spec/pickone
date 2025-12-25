from __future__ import annotations

from sqlalchemy import select

from app.models.organization import Organization
from app.repo.base import BaseRepo


class OrganizationRepo(BaseRepo):
    def list(self) -> list[Organization]:
        stmt = select(Organization).order_by(Organization.sort_order, Organization.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, organization_id: int) -> Organization | None:
        stmt = select(Organization).where(Organization.id == organization_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Organization | None:
        stmt = select(Organization).where(Organization.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Organization | None:
        stmt = select(Organization).where(Organization.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
