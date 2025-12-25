from sqlalchemy.orm import Session


class BaseRepo:
    def __init__(self, db: Session) -> None:
        self.db = db
