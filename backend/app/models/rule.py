from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Rule(Base, TimestampMixin):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    subcategory_id: Mapped[int | None] = mapped_column(Integer, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(80))
    title_required: Mapped[str | None] = mapped_column(String(100))
    avoid_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    draw_method: Mapped[str] = mapped_column(
        String(50), default="random", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
