from __future__ import annotations

from sqlalchemy import select

from app.models.title import Title
from app.repo.base import BaseRepo
from app.repo.utils import apply_keyword, apply_sort, paginate


class TitleRepo(BaseRepo):
    def list(self) -> list[Title]:
        stmt = select(Title).order_by(Title.sort_order, Title.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_page(
        self,
        keyword: str | None,
        sort_by: str | None,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Title], int]:
        stmt = select(Title)
        stmt = apply_keyword(stmt, keyword, [Title.name, Title.code])
        sort_map = {
            "id": Title.id,
            "name": Title.name,
            "code": Title.code,
            "sort_order": Title.sort_order,
            "is_active": Title.is_active,
        }
        effective_sort = sort_by or "sort_order"
        stmt = apply_sort(stmt, effective_sort, sort_order, sort_map, Title.id)
        return paginate(self.db, stmt, page, page_size)

    def get_by_id(self, title_id: int) -> Title | None:
        stmt = select(Title).where(Title.id == title_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Title | None:
        stmt = select(Title).where(Title.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, code: str) -> Title | None:
        stmt = select(Title).where(Title.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
