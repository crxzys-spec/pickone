from __future__ import annotations

from sqlalchemy import select

from app.models.expert import Expert
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class ExpertRepo(BaseRepo):
    def list(self) -> list[Expert]:
        stmt = select(Expert).order_by(Expert.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Expert], int]:
        stmt = select(Expert)
        stmt = apply_keyword(
            stmt,
            keyword,
            [
                Expert.name,
                Expert.company,
                Expert.phone,
                Expert.id_card_no,
                Expert.region,
            ],
        )
        sort_map = {
            "id": Expert.id,
            "name": Expert.name,
            "id_card_no": Expert.id_card_no,
            "gender": Expert.gender,
            "company": Expert.company,
            "region": Expert.region,
            "title": Expert.title,
            "phone": Expert.phone,
            "is_active": Expert.is_active,
        }
        stmt = apply_sort(stmt, sort_by, sort_order, sort_map, Expert.id)
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, expert_id: int) -> Expert | None:
        stmt = select(Expert).where(Expert.id == expert_id)
        return self.db.execute(stmt).scalar_one_or_none()
