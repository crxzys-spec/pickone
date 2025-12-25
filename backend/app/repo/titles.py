from __future__ import annotations

from sqlalchemy import select

from app.models.title import Title
from app.repo.base import BaseRepo


class TitleRepo(BaseRepo):
    def list(self) -> list[Title]:
        stmt = select(Title).order_by(Title.sort_order, Title.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, title_id: int) -> Title | None:
        stmt = select(Title).where(Title.id == title_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Title | None:
        stmt = select(Title).where(Title.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Title | None:
        stmt = select(Title).where(Title.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
