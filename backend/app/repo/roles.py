from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class RoleRepo(BaseRepo):
    def list(self) -> list[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Role], int]:
        stmt = select(Role).options(selectinload(Role.permissions))
        stmt = apply_keyword(stmt, keyword, [Role.name, Role.description])
        sort_map = {
            "id": Role.id,
            "name": Role.name,
            "description": Role.description,
        }
        stmt = apply_sort(stmt, sort_by, sort_order, sort_map, Role.id)
        return paginate(self.db, stmt, page, page_size)

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
