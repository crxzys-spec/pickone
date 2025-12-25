from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.repo.base import BaseRepo


class RoleRepo(BaseRepo):
    def list(self) -> list[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, role_id: int) -> Role | None:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.permissions))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_ids(self, role_ids: list[int]) -> list[Role]:
        if not role_ids:
            return []
        stmt = (
            select(Role)
            .where(Role.id.in_(role_ids))
            .options(selectinload(Role.permissions))
        )
        return list(self.db.execute(stmt).scalars().all())
