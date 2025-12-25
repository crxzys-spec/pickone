from __future__ import annotations

from sqlalchemy import select

from app.models.expert import Expert
from app.repo.base import BaseRepo


class ExpertRepo(BaseRepo):
    def list(self) -> list[Expert]:
        stmt = select(Expert).order_by(Expert.id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, expert_id: int) -> Expert | None:
        stmt = select(Expert).where(Expert.id == expert_id)
        return self.db.execute(stmt).scalar_one_or_none()
