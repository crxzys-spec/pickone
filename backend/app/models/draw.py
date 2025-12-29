from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class DrawApplication(Base, TimestampMixin):
    __tablename__ = "draw_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int | None] = mapped_column(Integer, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    subcategory_id: Mapped[int | None] = mapped_column(Integer, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(80), index=True)
    specialty_id: Mapped[int | None] = mapped_column(Integer, index=True)
    specialty: Mapped[str | None] = mapped_column(String(120), index=True)
    project_name: Mapped[str | None] = mapped_column(String(255), index=True)
    project_code: Mapped[str | None] = mapped_column(String(120), index=True)
    expert_count: Mapped[int] = mapped_column(Integer, nullable=False)
    backup_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    draw_method: Mapped[str] = mapped_column(
        String(50), default="random", nullable=False
    )
    review_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_location: Mapped[str | None] = mapped_column(String(255))
    avoid_units: Mapped[str | None] = mapped_column(String(255))
    avoid_persons: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    rule_id: Mapped[int | None] = mapped_column(ForeignKey("rules.id"))
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    rule = relationship("Rule")
    created_by = relationship("User")
    results = relationship(
        "DrawResult", back_populates="draw", cascade="all, delete-orphan"
    )


class DrawResult(Base, TimestampMixin):
    __tablename__ = "draw_results"
    __table_args__ = (UniqueConstraint("draw_id", "expert_id", name="uq_draw_expert"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    draw_id: Mapped[int] = mapped_column(
        ForeignKey("draw_applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    expert_id: Mapped[int] = mapped_column(
        ForeignKey("experts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    is_backup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_replacement: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    ordinal: Mapped[int | None] = mapped_column(Integer)

    draw = relationship("DrawApplication", back_populates="results")
    expert = relationship("Expert")
