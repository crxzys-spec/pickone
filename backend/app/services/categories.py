from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.category import Category
from app.models.draw import DrawApplication
from app.models.expert import Expert
from app.models.rule import Rule
from app.models.subcategory import Subcategory
from app.repo.categories import CategoryRepo
from app.repo.subcategories import SubcategoryRepo
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate


def _generate_unique_code(repo, prefix: str) -> str:
    code = generate_code(prefix=prefix)
    while repo.get_by_code(code):
        code = generate_code(prefix=prefix)
    return code


def list_categories(db: Session) -> list[Category]:
    return CategoryRepo(db).list()


def list_category_tree(db: Session) -> list[Category]:
    categories = CategoryRepo(db).list()
    subcategories = SubcategoryRepo(db).list()
    grouped: dict[int, list[Subcategory]] = {}
    for subcategory in subcategories:
        grouped.setdefault(subcategory.category_id, []).append(subcategory)
    for category in categories:
        setattr(category, "subcategories", grouped.get(category.id, []))
    return categories


def get_category(db: Session, category_id: int) -> Category:
    category = CategoryRepo(db).get_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


def _ensure_category_unique(
    db: Session, name: str | None, code: str | None, exclude_id: int | None = None
) -> None:
    repo = CategoryRepo(db)
    if name:
        existing = repo.get_by_name(name)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )
    if code:
        existing = repo.get_by_code(code)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category code already exists",
            )


def create_category(db: Session, payload: CategoryCreate) -> Category:
    _ensure_category_unique(db, payload.name, payload.code)
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    update_data = payload.model_dump(exclude_unset=True)
    _ensure_category_unique(
        db, update_data.get("name"), update_data.get("code"), exclude_id=category_id
    )

    name_changed = "name" in update_data and update_data["name"] != category.name

    for key, value in update_data.items():
        setattr(category, key, value)

    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.category_id == category_id)
            .values(category=category.name)
        )
        db.execute(
            Rule.__table__.update()
            .where(Rule.category_id == category_id)
            .values(category=category.name)
        )
        db.execute(
            DrawApplication.__table__.update()
            .where(DrawApplication.category_id == category_id)
            .values(category=category.name)
        )

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    subcategory_exists = (
        db.execute(
            select(Subcategory.id).where(Subcategory.category_id == category_id)
        ).first()
        is not None
    )
    if subcategory_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category has subcategories",
        )

    in_use = (
        db.execute(
            select(Expert.id).where(
                (Expert.category_id == category_id) | (Expert.category == category.name)
            )
        ).first()
        is not None
        or db.execute(
            select(Rule.id).where(
                (Rule.category_id == category_id) | (Rule.category == category.name)
            )
        ).first()
        is not None
        or db.execute(
            select(DrawApplication.id).where(
                (DrawApplication.category_id == category_id)
                | (DrawApplication.category == category.name)
            )
        ).first()
        is not None
    )
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is in use",
        )

    db.delete(category)
    db.commit()


def list_subcategories(db: Session, category_id: int) -> list[Subcategory]:
    _ = get_category(db, category_id)
    return SubcategoryRepo(db).list_by_category(category_id)


def get_subcategory(db: Session, subcategory_id: int) -> Subcategory:
    subcategory = SubcategoryRepo(db).get_by_id(subcategory_id)
    if subcategory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found"
        )
    return subcategory


def _ensure_subcategory_unique(
    db: Session, category_id: int, name: str | None, exclude_id: int | None = None
) -> None:
    if not name:
        return
    existing = SubcategoryRepo(db).get_by_category_and_name(category_id, name)
    if existing and existing.id != exclude_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory name already exists",
        )


def create_subcategory(
    db: Session, category_id: int, payload: SubcategoryCreate
) -> Subcategory:
    _ = get_category(db, category_id)
    _ensure_subcategory_unique(db, category_id, payload.name)
    subcategory = Subcategory(category_id=category_id, **payload.model_dump())
    db.add(subcategory)
    db.commit()
    db.refresh(subcategory)
    return subcategory


def update_subcategory(
    db: Session, subcategory_id: int, payload: SubcategoryUpdate
) -> Subcategory:
    subcategory = get_subcategory(db, subcategory_id)
    update_data = payload.model_dump(exclude_unset=True)
    _ensure_subcategory_unique(
        db,
        subcategory.category_id,
        update_data.get("name"),
        exclude_id=subcategory_id,
    )

    name_changed = "name" in update_data and update_data["name"] != subcategory.name

    for key, value in update_data.items():
        setattr(subcategory, key, value)

    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.subcategory_id == subcategory_id)
            .values(subcategory=subcategory.name)
        )
        db.execute(
            Rule.__table__.update()
            .where(Rule.subcategory_id == subcategory_id)
            .values(subcategory=subcategory.name)
        )
        db.execute(
            DrawApplication.__table__.update()
            .where(DrawApplication.subcategory_id == subcategory_id)
            .values(subcategory=subcategory.name)
        )

    db.commit()
    db.refresh(subcategory)
    return subcategory


def delete_subcategory(db: Session, subcategory_id: int) -> None:
    subcategory = get_subcategory(db, subcategory_id)
    category = CategoryRepo(db).get_by_id(subcategory.category_id)
    category_name = category.name if category else None

    in_use = (
        db.execute(
            select(Expert.id).where(
                (Expert.subcategory_id == subcategory_id)
                | (
                    (Expert.subcategory == subcategory.name)
                    & (
                        (Expert.category_id == subcategory.category_id)
                        | (Expert.category == category_name)
                    )
                )
            )
        ).first()
        is not None
        or db.execute(
            select(Rule.id).where(
                (Rule.subcategory_id == subcategory_id)
                | (
                    (Rule.subcategory == subcategory.name)
                    & (
                        (Rule.category_id == subcategory.category_id)
                        | (Rule.category == category_name)
                    )
                )
            )
        ).first()
        is not None
        or db.execute(
            select(DrawApplication.id).where(
                (DrawApplication.subcategory_id == subcategory_id)
                | (
                    (DrawApplication.subcategory == subcategory.name)
                    & (
                        (DrawApplication.category_id == subcategory.category_id)
                        | (DrawApplication.category == category_name)
                    )
                )
            )
        ).first()
        is not None
    )
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory is in use",
        )

    db.delete(subcategory)
    db.commit()


def resolve_category(
    db: Session,
    category_id: int | None,
    category_name: str | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Category | None:
    repo = CategoryRepo(db)
    category = None
    if category_id is not None:
        category = repo.get_by_id(category_id)
        if category is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
    elif category_name:
        category = repo.get_by_name(category_name)
        if category is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        if category is None and create_if_missing:
            category = Category(
                name=category_name,
                code=_generate_unique_code(repo, "cat"),
                is_active=True,
                sort_order=0,
            )
            db.add(category)
            db.flush()
    return category


def resolve_subcategory(
    db: Session,
    subcategory_id: int | None,
    subcategory_name: str | None,
    category: Category | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Subcategory | None:
    repo = SubcategoryRepo(db)
    subcategory = None
    if subcategory_id is not None:
        subcategory = repo.get_by_id(subcategory_id)
        if subcategory is None:
            if strict:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Subcategory not found",
                )
            return None
        if category is not None and subcategory.category_id != category.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subcategory does not belong to category",
            )
    elif subcategory_name:
        if category is None:
            if strict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category is required for subcategory",
                )
            return None
        subcategory = repo.get_by_category_and_name(category.id, subcategory_name)
        if subcategory is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategory not found",
            )
        if subcategory is None and create_if_missing:
            subcategory = Subcategory(
                category_id=category.id,
                name=subcategory_name,
                code=generate_code(prefix="sub"),
                is_active=True,
                sort_order=0,
            )
            db.add(subcategory)
            db.flush()
    return subcategory
