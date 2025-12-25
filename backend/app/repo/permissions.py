from __future__ import annotations

from sqlalchemy import select

from app.models.permission import Permission
from app.repo.base import BaseRepo


class PermissionRepo(BaseRepo):
    def list(self) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, permission_id: int) -> Permission | None:
        stmt = select(Permission).where(Permission.id == permission_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_scope(self, scope: str) -> Permission | None:
        stmt = select(Permission).where(Permission.scope == scope)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_ids(self, permission_ids: list[int]) -> list[Permission]:
        if not permission_ids:
            return []
        stmt = select(Permission).where(Permission.id.in_(permission_ids))
        return list(self.db.execute(stmt).scalars().all())
