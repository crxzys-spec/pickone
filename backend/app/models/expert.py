from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Expert(Base, TimestampMixin):
    __tablename__ = "experts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    gender: Mapped[str | None] = mapped_column(String(10))
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(String(255))
    organization_id: Mapped[int | None] = mapped_column(Integer, index=True)
    title: Mapped[str | None] = mapped_column(String(100))
    title_id: Mapped[int | None] = mapped_column(Integer, index=True)
    category_id: Mapped[int | None] = mapped_column(Integer, index=True)
    category: Mapped[str | None] = mapped_column(String(50), index=True)
    subcategory_id: Mapped[int | None] = mapped_column(Integer, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(80), index=True)
    avoid_units: Mapped[str | None] = mapped_column(String(255))
    avoid_persons: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
