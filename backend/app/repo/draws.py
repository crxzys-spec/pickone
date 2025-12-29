from __future__ import annotations

from sqlalchemy import select

from app.models.draw import DrawApplication
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class DrawRepo(BaseRepo):
    def list(self) -> list[DrawApplication]:
        stmt = select(DrawApplication).order_by(DrawApplication.id.desc())
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[DrawApplication], int]:
        stmt = select(DrawApplication)
        stmt = apply_keyword(
            stmt,
            keyword,
            [
                DrawApplication.category,
                DrawApplication.subcategory,
                DrawApplication.specialty,
                DrawApplication.project_name,
                DrawApplication.project_code,
                DrawApplication.review_location,
                DrawApplication.status,
            ],
        )
        sort_map = {
            "id": DrawApplication.id,
            "category": DrawApplication.category,
            "subcategory": DrawApplication.subcategory,
            "specialty": DrawApplication.specialty,
            "project_name": DrawApplication.project_name,
            "project_code": DrawApplication.project_code,
            "expert_count": DrawApplication.expert_count,
            "backup_count": DrawApplication.backup_count,
            "draw_method": DrawApplication.draw_method,
            "review_time": DrawApplication.review_time,
            "review_location": DrawApplication.review_location,
            "status": DrawApplication.status,
            "rule_id": DrawApplication.rule_id,
        }
        effective_sort = sort_by or "id"
        effective_order = sort_order if sort_by else "desc"
        stmt = apply_sort(
            stmt, effective_sort, effective_order, sort_map, DrawApplication.id
        )
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, draw_id: int) -> DrawApplication | None:
        stmt = select(DrawApplication).where(DrawApplication.id == draw_id)
        return self.db.execute(stmt).scalar_one_or_none()
