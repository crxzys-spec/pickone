from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.draw import DrawApplication
from app.models.expert_specialty import ExpertSpecialty
from app.models.rule import Rule
from app.models.specialty import Specialty
from app.models.subcategory import Subcategory
from app.repo.specialties import SpecialtyRepo
from app.schemas.pagination import PageParams
from app.schemas.specialty import SpecialtyCreate, SpecialtyUpdate


def _generate_unique_code(repo: SpecialtyRepo, prefix: str) -> str:
    code = generate_code(prefix=prefix)
    while repo.get_by_code(code):
        code = generate_code(prefix=prefix)
    return code


def _in_use_detail(entity: str, rule_exists: bool, draw_exists: bool) -> str:
    if rule_exists and draw_exists:
        return f"{entity} is in use by rules, draws"
    if rule_exists:
        return f"{entity} is in use by rules"
    if draw_exists:
        return f"{entity} is in use by draws"
    return f"{entity} is in use"


def list_specialties(
    db: Session, subcategory_id: int, params: PageParams
) -> tuple[list[Specialty], int]:
    return SpecialtyRepo(db).list_page(
        subcategory_id,
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def list_specialties_all(db: Session) -> list[Specialty]:
    return SpecialtyRepo(db).list()


def list_specialties_by_subcategory(
    db: Session, subcategory_id: int
) -> list[Specialty]:
    return SpecialtyRepo(db).list_by_subcategory(subcategory_id)


def get_specialty(db: Session, specialty_id: int) -> Specialty:
    specialty = SpecialtyRepo(db).get_by_id(specialty_id)
    if specialty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specialty not found"
        )
    return specialty


def _ensure_specialty_unique(
    db: Session,
    subcategory_id: int,
    name: str | None,
    code: str | None,
    exclude_id: int | None = None,
) -> None:
    repo = SpecialtyRepo(db)
    if code:
        existing = repo.get_by_code(code)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty code already exists",
            )


def create_specialty(
    db: Session, subcategory_id: int, payload: SpecialtyCreate
) -> Specialty:
    subcategory = db.execute(
        select(Subcategory).where(Subcategory.id == subcategory_id)
    ).scalar_one_or_none()
    if subcategory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found"
        )
    code = payload.code.strip() if payload.code else None
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty code is required",
        )
    _ensure_specialty_unique(db, subcategory_id, payload.name, code)
    data = payload.model_dump()
    data["code"] = code
    specialty = Specialty(subcategory_id=subcategory_id, **data)
    db.add(specialty)
    db.commit()
    db.refresh(specialty)
    return specialty


def update_specialty(
    db: Session, specialty_id: int, payload: SpecialtyUpdate
) -> Specialty:
    specialty = get_specialty(db, specialty_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = (
            update_data["code"].strip() if update_data.get("code") else None
        )
    effective_code = update_data.get("code", specialty.code)
    if not effective_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty code is required",
        )
    _ensure_specialty_unique(
        db,
        specialty.subcategory_id,
        update_data.get("name"),
        effective_code,
        exclude_id=specialty_id,
    )

    name_changed = "name" in update_data and update_data["name"] != specialty.name

    for key, value in update_data.items():
        setattr(specialty, key, value)

    if name_changed:
        db.execute(
            Rule.__table__.update()
            .where(Rule.specialty_id == specialty_id)
            .values(specialty=specialty.name)
        )
        db.execute(
            DrawApplication.__table__.update()
            .where(DrawApplication.specialty_id == specialty_id)
            .values(specialty=specialty.name)
        )

    db.commit()
    db.refresh(specialty)
    return specialty


def delete_specialty(db: Session, specialty_id: int) -> None:
    specialty = get_specialty(db, specialty_id)
    rule_exists = (
        db.execute(
            select(Rule.id).where(
                (Rule.specialty_id == specialty_id)
                | (Rule.specialty == specialty.name)
            )
        ).first()
        is not None
    )
    draw_exists = (
        db.execute(
            select(DrawApplication.id).where(
                (DrawApplication.specialty_id == specialty_id)
                | (DrawApplication.specialty == specialty.name)
            )
        ).first()
        is not None
    )
    if rule_exists or draw_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_in_use_detail("Specialty", rule_exists, draw_exists),
        )

    db.execute(
        ExpertSpecialty.__table__.delete().where(
            ExpertSpecialty.specialty_id == specialty_id
        )
    )
    db.delete(specialty)
    db.commit()


def resolve_specialty(
    db: Session,
    specialty_id: int | None,
    specialty_name: str | None,
    subcategory_id: int | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Specialty | None:
    repo = SpecialtyRepo(db)
    specialty = None
    if specialty_id is not None:
        specialty = repo.get_by_id(specialty_id)
        if specialty is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Specialty not found"
            )
    elif specialty_name:
        if subcategory_id is None:
            if strict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subcategory is required for specialty",
                )
            return None
        specialty = repo.get_by_subcategory_and_name(subcategory_id, specialty_name)
        if specialty is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Specialty not found"
            )
        if specialty is None and create_if_missing:
            specialty = Specialty(
                subcategory_id=subcategory_id,
                name=specialty_name,
                code=_generate_unique_code(repo, "spec"),
                is_active=True,
                sort_order=0,
            )
            db.add(specialty)
            db.flush()
    return specialty
