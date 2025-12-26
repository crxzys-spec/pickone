from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.user import User
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class UserRepo(BaseRepo):
    def list(self) -> list[User]:
        stmt = select(User).options(selectinload(User.roles)).order_by(User.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        stmt = select(User).options(selectinload(User.roles))
        stmt = apply_keyword(stmt, keyword, [User.username, User.full_name, User.email])
        sort_map = {
            "id": User.id,
            "username": User.username,
            "full_name": User.full_name,
            "email": User.email,
            "is_active": User.is_active,
            "is_superuser": User.is_superuser,
        }
        stmt = apply_sort(stmt, sort_by, sort_order, sort_map, User.id)
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return self.db.execute(stmt).scalar_one_or_none()
