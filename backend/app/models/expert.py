from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Expert(Base, TimestampMixin):
    __tablename__ = "experts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    id_card_no: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    gender: Mapped[str | None] = mapped_column(String(10))
    phone: Mapped[str | None] = mapped_column(String(30))
    company: Mapped[str | None] = mapped_column(String(255))
    organization_id: Mapped[int | None] = mapped_column(Integer, index=True)
    region_id: Mapped[int | None] = mapped_column(Integer, index=True)
    region: Mapped[str | None] = mapped_column(String(80), index=True)
    title: Mapped[str | None] = mapped_column(String(100))
    title_id: Mapped[int | None] = mapped_column(Integer, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
