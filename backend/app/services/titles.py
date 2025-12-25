from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.expert import Expert
from app.models.title import Title
from app.repo.titles import TitleRepo
from app.schemas.title import TitleCreate, TitleUpdate


def _generate_unique_code(repo: TitleRepo) -> str:
    code = generate_code(prefix="title")
    while repo.get_by_code(code):
        code = generate_code(prefix="title")
    return code


def list_titles(db: Session) -> list[Title]:
    return TitleRepo(db).list()


def get_title(db: Session, title_id: int) -> Title:
    title = TitleRepo(db).get_by_id(title_id)
    if title is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Title not found"
        )
    return title


def _ensure_unique(
    db: Session, name: str | None, code: str | None, exclude_id: int | None = None
) -> None:
    repo = TitleRepo(db)
    if name:
        existing = repo.get_by_name(name)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title name already exists",
            )
    if code:
        existing = repo.get_by_code(code)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title code already exists",
            )


def create_title(db: Session, payload: TitleCreate) -> Title:
    _ensure_unique(db, payload.name, payload.code)
    title = Title(**payload.model_dump())
    if not title.code:
        title.code = _generate_unique_code(TitleRepo(db))
    db.add(title)
    db.commit()
    db.refresh(title)
    return title


def update_title(db: Session, title_id: int, payload: TitleUpdate) -> Title:
    title = get_title(db, title_id)
    update_data = payload.model_dump(exclude_unset=True)
    _ensure_unique(db, update_data.get("name"), update_data.get("code"), exclude_id=title_id)

    old_name = title.name
    name_changed = "name" in update_data and update_data["name"] != title.name
    for key, value in update_data.items():
        setattr(title, key, value)

    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.title_id == title_id)
            .values(title=title.name)
        )
        db.execute(
            Expert.__table__.update()
            .where(Expert.title_id.is_(None), Expert.title == old_name)
            .values(title=title.name)
        )

    db.commit()
    db.refresh(title)
    return title


def delete_title(db: Session, title_id: int) -> None:
    title = get_title(db, title_id)
    in_use = (
        db.execute(
            select(Expert.id).where(
                (Expert.title_id == title_id) | (Expert.title == title.name)
            )
        ).first()
        is not None
    )
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is in use",
        )

    db.delete(title)
    db.commit()


def resolve_title(
    db: Session,
    title_id: int | None,
    title_name: str | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Title | None:
    repo = TitleRepo(db)
    title = None
    if title_id is not None:
        title = repo.get_by_id(title_id)
        if title is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found",
            )
    elif title_name:
        title = repo.get_by_name(title_name)
        if title is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found",
            )
        if title is None and create_if_missing:
            title = Title(
                name=title_name,
                code=_generate_unique_code(repo),
                is_active=True,
                sort_order=0,
            )
            db.add(title)
            db.flush()
    return title
