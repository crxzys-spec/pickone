from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ExpertSpecialty(Base, TimestampMixin):
    __tablename__ = "expert_specialties"
    __table_args__ = (
        UniqueConstraint("expert_id", "specialty_id", name="uq_expert_specialty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    expert_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    specialty_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
