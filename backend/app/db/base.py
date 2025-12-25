from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Load model modules so Alembic can detect them.
from app import models  # noqa: F401,E402
