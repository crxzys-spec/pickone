from __future__ import annotations

from sqlalchemy import select

from app.models.draw import DrawApplication
from app.repo.base import BaseRepo


class DrawRepo(BaseRepo):
    def list(self) -> list[DrawApplication]:
        stmt = select(DrawApplication).order_by(DrawApplication.id.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, draw_id: int) -> DrawApplication | None:
        stmt = select(DrawApplication).where(DrawApplication.id == draw_id)
        return self.db.execute(stmt).scalar_one_or_none()
