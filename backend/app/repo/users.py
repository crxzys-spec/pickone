from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.user import User
from app.repo.base import BaseRepo


class UserRepo(BaseRepo):
    def list(self) -> list[User]:
        stmt = select(User).options(selectinload(User.roles)).order_by(User.id)
        return list(self.db.execute(stmt).scalars().all())

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
