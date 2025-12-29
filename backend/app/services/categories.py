from __future__ import annotations

from io import BytesIO

from fastapi import HTTPException, status
from openpyxl import Workbook, load_workbook
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.category import Category
from app.models.draw import DrawApplication
from app.models.expert import Expert
from app.models.expert_specialty import ExpertSpecialty
from app.models.rule import Rule
from app.models.specialty import Specialty
from app.models.subcategory import Subcategory
from app.repo.categories import CategoryRepo
from app.repo.specialties import SpecialtyRepo
from app.repo.subcategories import SubcategoryRepo
from app.schemas.pagination import PageParams
from app.schemas.category import CategoryBatchAction, CategoryCreate, CategoryUpdate
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate
from app.services import specialties as specialty_service


def _generate_unique_code(repo, prefix: str) -> str:
    code = generate_code(prefix=prefix)
    while repo.get_by_code(code):
        code = generate_code(prefix=prefix)
    return code


EXPORT_FIELDS = [
    ("category_name", "一级名称"),
    ("category_code", "一级编码"),
    ("category_sort", "一级排序"),
    ("category_active", "一级启用"),
    ("subcategory_name", "二级名称"),
    ("subcategory_code", "二级编码"),
    ("subcategory_sort", "二级排序"),
    ("subcategory_active", "二级启用"),
    ("specialty_name", "专业名称"),
    ("specialty_code", "专业编码"),
    ("specialty_sort", "专业排序"),
    ("specialty_active", "专业启用"),
]
EXPORT_HEADERS = [label for _, label in EXPORT_FIELDS]
HEADER_MAP = {label.lower(): field for field, label in EXPORT_FIELDS}
HEADER_MAP.update({field: field for field, _ in EXPORT_FIELDS})
HEADER_MAP.update(
    {
        "专业一级目录": "category_name",
        "专业二级目录": "subcategory_name",
        "专业三级目录": "specialty_name",
        "专业目录": "specialty_name",
        "一级目录": "category_name",
        "二级目录": "subcategory_name",
        "三级目录": "specialty_name",
        "三级名称": "specialty_name",
        "三级编码": "specialty_code",
        "三级排序": "specialty_sort",
        "三级启用": "specialty_active",
    }
)


def _coerce_str(value: object | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)
    stripped = str(value).strip()
    return stripped or None


def _coerce_int(value: object | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(float(stripped))
        except ValueError:
            return None
    return None


def _coerce_bool(value: object | None) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, float):
        return bool(int(value))
    if isinstance(value, str):
        normalized = value.strip().lower()
        if not normalized:
            return None
        if normalized in {"1", "true", "yes", "y", "是", "启用"}:
            return True
        if normalized in {"0", "false", "no", "n", "否", "禁用"}:
            return False
    return None


def _apply_category_updates(
    db: Session,
    repo: CategoryRepo,
    category: Category,
    name: str | None,
    code: str | None,
    sort_order: int | None,
    is_active: bool | None,
) -> bool:
    updated = False
    name_changed = False
    if name is not None and name != category.name:
        category.name = name
        updated = True
        name_changed = True
    if code is not None and code != category.code:
        if code:
            existing = repo.get_by_code(code)
            if existing is None or existing.id == category.id:
                category.code = code
                updated = True
        else:
            category.code = None
            updated = True
    if sort_order is not None and sort_order != category.sort_order:
        category.sort_order = sort_order
        updated = True
    if is_active is not None and is_active != category.is_active:
        category.is_active = is_active
        updated = True
    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.category_id == category.id)
            .values(category=category.name)
        )
        db.execute(
            Rule.__table__.update()
            .where(Rule.category_id == category.id)
            .values(category=category.name)
        )
        db.execute(
            DrawApplication.__table__.update()
            .where(DrawApplication.category_id == category.id)
            .values(category=category.name)
        )
    return updated


def _apply_subcategory_updates(
    db: Session,
    repo: SubcategoryRepo,
    subcategory: Subcategory,
    name: str | None,
    code: str | None,
    sort_order: int | None,
    is_active: bool | None,
) -> bool:
    updated = False
    name_changed = False
    if name is not None and name != subcategory.name:
        subcategory.name = name
        updated = True
        name_changed = True
    if code is not None and code != subcategory.code:
        if code:
            existing = repo.get_by_code(code)
            if existing is None or existing.id == subcategory.id:
                subcategory.code = code
                updated = True
        else:
            subcategory.code = None
            updated = True
    if sort_order is not None and sort_order != subcategory.sort_order:
        subcategory.sort_order = sort_order
        updated = True
    if is_active is not None and is_active != subcategory.is_active:
        subcategory.is_active = is_active
        updated = True
    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.subcategory_id == subcategory.id)
            .values(subcategory=subcategory.name)
        )
        db.execute(
            Rule.__table__.update()
            .where(Rule.subcategory_id == subcategory.id)
            .values(subcategory=subcategory.name)
        )
        db.execute(
            DrawApplication.__table__.update()
            .where(DrawApplication.subcategory_id == subcategory.id)
            .values(subcategory=subcategory.name)
        )
    return updated


def _apply_specialty_updates(
    db: Session,
    repo: SpecialtyRepo,
    specialty: Specialty,
    name: str | None,
    code: str | None,
    sort_order: int | None,
    is_active: bool | None,
) -> bool:
    updated = False
    name_changed = False
    if name is not None and name != specialty.name:
        specialty.name = name
        updated = True
        name_changed = True
    if code is not None and code != specialty.code:
        if code:
            existing = repo.get_by_code(code)
            if existing is None or existing.id == specialty.id:
                specialty.code = code
                updated = True
        else:
            specialty.code = None
            updated = True
    if sort_order is not None and sort_order != specialty.sort_order:
        specialty.sort_order = sort_order
        updated = True
    if is_active is not None and is_active != specialty.is_active:
        specialty.is_active = is_active
        updated = True
    if name_changed:
        db.execute(
            Rule.__table__.update()
            .where(Rule.specialty_id == specialty.id)
            .values(specialty=specialty.name)
        )
        db.execute(
            DrawApplication.__table__.update()
            .where(DrawApplication.specialty_id == specialty.id)
            .values(specialty=specialty.name)
        )
    return updated


def _in_use_detail(entity: str, rule_exists: bool, draw_exists: bool) -> str:
    if rule_exists and draw_exists:
        return f"{entity} is in use by rules, draws"
    if rule_exists:
        return f"{entity} is in use by rules"
    if draw_exists:
        return f"{entity} is in use by draws"
    return f"{entity} is in use"


def list_categories(db: Session, params: PageParams) -> tuple[list[Category], int]:
    return CategoryRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def list_categories_all(db: Session) -> list[Category]:
    return CategoryRepo(db).list()


def list_category_tree(db: Session) -> list[Category]:
    def _sort_key(item: Category | Subcategory | Specialty) -> tuple[int, str, str, int]:
        code = (item.code or "").strip()
        name = item.name.strip()
        return (item.sort_order, code, name, item.id)

    categories = list_categories_all(db)
    subcategories = SubcategoryRepo(db).list()
    specialties = SpecialtyRepo(db).list()
    grouped: dict[int, list[Subcategory]] = {}
    for subcategory in subcategories:
        grouped.setdefault(subcategory.category_id, []).append(subcategory)
    specialty_grouped: dict[int, list[Specialty]] = {}
    for specialty in specialties:
        specialty_grouped.setdefault(specialty.subcategory_id, []).append(specialty)
    for category in sorted(categories, key=_sort_key):
        category_subs = sorted(grouped.get(category.id, []), key=_sort_key)
        for subcategory in category_subs:
            setattr(
                subcategory,
                "specialties",
                sorted(specialty_grouped.get(subcategory.id, []), key=_sort_key),
            )
        setattr(category, "subcategories", category_subs)
    return sorted(categories, key=_sort_key)


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
    if code:
        existing = repo.get_by_code(code)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category code already exists",
            )


def create_category(db: Session, payload: CategoryCreate) -> Category:
    code = payload.code.strip() if payload.code else None
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category code is required",
        )
    _ensure_category_unique(db, payload.name, code)
    data = payload.model_dump()
    data["code"] = code
    category = Category(**data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = (
            update_data["code"].strip() if update_data.get("code") else None
        )
    effective_code = update_data.get("code", category.code)
    if not effective_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category code is required",
        )
    _ensure_category_unique(
        db, update_data.get("name"), effective_code, exclude_id=category_id
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
    rule_exists = (
        db.execute(
            select(Rule.id).where(
                (Rule.category_id == category_id) | (Rule.category == category.name)
            )
        ).first()
        is not None
    )
    draw_exists = (
        db.execute(
            select(DrawApplication.id).where(
                (DrawApplication.category_id == category_id)
                | (DrawApplication.category == category.name)
            )
        ).first()
        is not None
    )
    if rule_exists or draw_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_in_use_detail("Category", rule_exists, draw_exists),
        )

    subcategory_rows = db.execute(
        select(Subcategory.id, Subcategory.name).where(
            Subcategory.category_id == category_id
        )
    ).all()
    subcategory_ids = [row[0] for row in subcategory_rows]
    subcategory_names = [row[1] for row in subcategory_rows if row[1]]
    specialty_ids: list[int] = []
    if subcategory_ids:
        specialty_ids = db.execute(
            select(Specialty.id).where(Specialty.subcategory_id.in_(subcategory_ids))
        ).scalars().all()

    expert_conditions = [
        Expert.category_id == category_id,
        Expert.category == category.name,
    ]
    if subcategory_ids:
        expert_conditions.append(Expert.subcategory_id.in_(subcategory_ids))
    if subcategory_names:
        expert_conditions.append(
            (Expert.subcategory.in_(subcategory_names))
            & (
                (Expert.category_id == category_id)
                | (Expert.category == category.name)
            )
        )
    db.execute(
        Expert.__table__.update()
        .where(or_(*expert_conditions))
        .values(
            category_id=None,
            category=None,
            subcategory_id=None,
            subcategory=None,
        )
    )

    if specialty_ids:
        db.execute(
            ExpertSpecialty.__table__.delete().where(
                ExpertSpecialty.specialty_id.in_(specialty_ids)
            )
        )
        db.execute(
            Specialty.__table__.delete().where(Specialty.id.in_(specialty_ids))
        )
    if subcategory_ids:
        db.execute(
            Subcategory.__table__.delete().where(Subcategory.id.in_(subcategory_ids))
        )

    db.delete(category)
    db.commit()


def list_subcategories(
    db: Session, category_id: int, params: PageParams
) -> tuple[list[Subcategory], int]:
    _ = get_category(db, category_id)
    return SubcategoryRepo(db).list_page(
        category_id,
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def get_subcategory(db: Session, subcategory_id: int) -> Subcategory:
    subcategory = SubcategoryRepo(db).get_by_id(subcategory_id)
    if subcategory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found"
        )
    return subcategory


def _ensure_subcategory_unique(
    db: Session, code: str | None, exclude_id: int | None = None
) -> None:
    if not code:
        return
    existing = SubcategoryRepo(db).get_by_code(code)
    if existing and existing.id != exclude_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory code already exists",
        )


def create_subcategory(
    db: Session, category_id: int, payload: SubcategoryCreate
) -> Subcategory:
    _ = get_category(db, category_id)
    code = payload.code.strip() if payload.code else None
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory code is required",
        )
    _ensure_subcategory_unique(db, code)
    data = payload.model_dump()
    data["code"] = code
    subcategory = Subcategory(category_id=category_id, **data)
    db.add(subcategory)
    db.commit()
    db.refresh(subcategory)
    return subcategory


def update_subcategory(
    db: Session, subcategory_id: int, payload: SubcategoryUpdate
) -> Subcategory:
    subcategory = get_subcategory(db, subcategory_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = (
            update_data["code"].strip() if update_data.get("code") else None
        )
    effective_code = update_data.get("code", subcategory.code)
    if not effective_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory code is required",
        )
    _ensure_subcategory_unique(
        db,
        effective_code,
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

    rule_exists = (
        db.execute(
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
    )
    draw_exists = (
        db.execute(
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
    if rule_exists or draw_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_in_use_detail("Subcategory", rule_exists, draw_exists),
        )

    specialty_ids = db.execute(
        select(Specialty.id).where(Specialty.subcategory_id == subcategory_id)
    ).scalars().all()

    expert_condition = Expert.subcategory_id == subcategory_id
    name_condition = (Expert.subcategory == subcategory.name) & (
        Expert.category_id == subcategory.category_id
    )
    if category_name:
        name_condition = name_condition | (
            (Expert.subcategory == subcategory.name)
            & (Expert.category == category_name)
        )
    expert_condition = expert_condition | name_condition
    db.execute(
        Expert.__table__.update()
        .where(expert_condition)
        .values(subcategory_id=None, subcategory=None)
    )

    if specialty_ids:
        db.execute(
            ExpertSpecialty.__table__.delete().where(
                ExpertSpecialty.specialty_id.in_(specialty_ids)
            )
        )
        db.execute(
            Specialty.__table__.delete().where(Specialty.id.in_(specialty_ids))
        )

    db.delete(subcategory)
    db.commit()


def batch_categories(db: Session, payload: CategoryBatchAction) -> dict[str, int]:
    if not payload.items:
        return {"updated": 0, "deleted": 0, "skipped": 0}

    category_ids = {
        item.id for item in payload.items if item.type == "category"
    }
    subcategory_ids = {
        item.id for item in payload.items if item.type == "subcategory"
    }
    specialty_ids = {
        item.id for item in payload.items if item.type == "specialty"
    }

    if payload.action in {"enable", "disable"}:
        is_active = payload.action == "enable"
        updated = 0
        if category_ids:
            result = db.execute(
                Category.__table__.update()
                .where(Category.id.in_(category_ids))
                .values(is_active=is_active)
            )
            updated += int(result.rowcount or 0)
        if subcategory_ids:
            result = db.execute(
                Subcategory.__table__.update()
                .where(Subcategory.id.in_(subcategory_ids))
                .values(is_active=is_active)
            )
            updated += int(result.rowcount or 0)
        if specialty_ids:
            result = db.execute(
                Specialty.__table__.update()
                .where(Specialty.id.in_(specialty_ids))
                .values(is_active=is_active)
            )
            updated += int(result.rowcount or 0)
        db.commit()
        return {"updated": updated, "deleted": 0, "skipped": 0}

    if payload.action != "delete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid batch action"
        )

    if category_ids:
        sub_ids_under_categories = set(
            db.execute(
                select(Subcategory.id).where(Subcategory.category_id.in_(category_ids))
            )
            .scalars()
            .all()
        )
        if sub_ids_under_categories:
            subcategory_ids.difference_update(sub_ids_under_categories)
            spec_ids_under_categories = set(
                db.execute(
                    select(Specialty.id).where(
                        Specialty.subcategory_id.in_(sub_ids_under_categories)
                    )
                )
                .scalars()
                .all()
            )
            specialty_ids.difference_update(spec_ids_under_categories)

    if subcategory_ids:
        spec_ids_under_subcategories = set(
            db.execute(
                select(Specialty.id).where(Specialty.subcategory_id.in_(subcategory_ids))
            )
            .scalars()
            .all()
        )
        specialty_ids.difference_update(spec_ids_under_subcategories)

    deleted = 0
    skipped = 0
    errors: list[dict[str, object]] = []

    subcategories_by_category: dict[int, set[int]] = {}
    if category_ids:
        rows = db.execute(
            select(Subcategory.id, Subcategory.category_id).where(
                Subcategory.category_id.in_(category_ids)
            )
        ).all()
        for subcategory_id, category_id in rows:
            subcategories_by_category.setdefault(category_id, set()).add(subcategory_id)

    subcategory_ids_for_specialties = set(subcategory_ids)
    for sub_ids in subcategories_by_category.values():
        subcategory_ids_for_specialties.update(sub_ids)

    specialties_by_subcategory: dict[int, set[int]] = {}
    if subcategory_ids_for_specialties:
        rows = db.execute(
            select(Specialty.id, Specialty.subcategory_id).where(
                Specialty.subcategory_id.in_(subcategory_ids_for_specialties)
            )
        ).all()
        for specialty_id, subcategory_id in rows:
            specialties_by_subcategory.setdefault(subcategory_id, set()).add(
                specialty_id
            )

    deleted_categories: set[int] = set()
    for category_id in category_ids:
        try:
            delete_category(db, category_id)
            deleted += 1
            deleted_categories.add(category_id)
        except HTTPException as exc:
            skipped += 1
            errors.append(
                {
                    "id": category_id,
                    "type": "category",
                    "detail": str(exc.detail),
                }
            )

    for category_id in deleted_categories:
        for sub_id in subcategories_by_category.get(category_id, set()):
            subcategory_ids.discard(sub_id)
            for spec_id in specialties_by_subcategory.get(sub_id, set()):
                specialty_ids.discard(spec_id)

    deleted_subcategories: set[int] = set()
    for subcategory_id in subcategory_ids:
        try:
            delete_subcategory(db, subcategory_id)
            deleted += 1
            deleted_subcategories.add(subcategory_id)
        except HTTPException as exc:
            skipped += 1
            errors.append(
                {
                    "id": subcategory_id,
                    "type": "subcategory",
                    "detail": str(exc.detail),
                }
            )

    for sub_id in deleted_subcategories:
        for spec_id in specialties_by_subcategory.get(sub_id, set()):
            specialty_ids.discard(spec_id)

    for specialty_id in specialty_ids:
        try:
            specialty_service.delete_specialty(db, specialty_id)
            deleted += 1
        except HTTPException as exc:
            skipped += 1
            errors.append(
                {
                    "id": specialty_id,
                    "type": "specialty",
                    "detail": str(exc.detail),
                }
            )

    return {"updated": 0, "deleted": deleted, "skipped": skipped, "errors": errors}


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
                code=_generate_unique_code(repo, "sub"),
                is_active=True,
                sort_order=0,
            )
            db.add(subcategory)
            db.flush()
    return subcategory


def import_categories(db: Session, file) -> dict[str, object]:
    file.file.seek(0)
    workbook = load_workbook(file.file, data_only=True)
    worksheet = workbook.active

    rows = worksheet.iter_rows(values_only=True)
    header_row = next(rows, None)
    if not header_row:
        return {"created": 0, "updated": 0, "skipped": 0}

    index_to_field: dict[int, str] = {}
    for idx, cell in enumerate(header_row):
        if cell is None:
            continue
        key = str(cell).strip().lower()
        field = HEADER_MAP.get(key)
        if field:
            index_to_field[idx] = field

    if not index_to_field:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing valid headers",
        )

    created = 0
    updated = 0
    skipped = 0
    errors: list[dict[str, object]] = []
    category_repo = CategoryRepo(db)
    subcategory_repo = SubcategoryRepo(db)
    specialty_repo = SpecialtyRepo(db)

    for row_index, row in enumerate(rows, start=2):
        if not row or all(cell is None for cell in row):
            continue
        data: dict[str, object | None] = {}
        for idx, field in index_to_field.items():
            value = row[idx] if idx < len(row) else None
            data[field] = value

        category_name = _coerce_str(data.get("category_name"))
        category_code = _coerce_str(data.get("category_code"))
        category_sort = _coerce_int(data.get("category_sort"))
        category_active = _coerce_bool(data.get("category_active"))
        if not category_name and not category_code:
            skipped += 1
            continue
        if category_name and not category_code:
            errors.append(
                {
                    "row": row_index,
                    "level": "category",
                    "detail": f"第{row_index}行：一级编码缺失",
                }
            )
            skipped += 1
            continue

        category = None
        if category_code:
            category = category_repo.get_by_code(category_code)
        elif category_name:
            category = category_repo.get_by_name(category_name)
        if category is None:
            if not category_name:
                skipped += 1
                continue
            category = Category(
                name=category_name,
                code=category_code,
                sort_order=category_sort if category_sort is not None else 0,
                is_active=category_active if category_active is not None else True,
            )
            db.add(category)
            db.flush()
            created += 1
        else:
            if _apply_category_updates(
                db,
                category_repo,
                category,
                category_name,
                category_code,
                category_sort,
                category_active,
            ):
                updated += 1

        subcategory_name = _coerce_str(data.get("subcategory_name"))
        subcategory_code = _coerce_str(data.get("subcategory_code"))
        subcategory_sort = _coerce_int(data.get("subcategory_sort"))
        subcategory_active = _coerce_bool(data.get("subcategory_active"))
        if not subcategory_name and not subcategory_code:
            continue
        if subcategory_name and not subcategory_code:
            errors.append(
                {
                    "row": row_index,
                    "level": "subcategory",
                    "detail": f"第{row_index}行：二级编码缺失",
                }
            )
            skipped += 1
            continue

        subcategory = None
        if subcategory_code:
            subcategory = subcategory_repo.get_by_code(subcategory_code)
            if subcategory and subcategory.category_id != category.id:
                skipped += 1
                continue
        elif subcategory_name:
            subcategory = subcategory_repo.get_by_category_and_name(
                category.id, subcategory_name
            )
        if subcategory is None:
            if not subcategory_name:
                skipped += 1
                continue
            subcategory = Subcategory(
                category_id=category.id,
                name=subcategory_name,
                code=subcategory_code,
                sort_order=subcategory_sort if subcategory_sort is not None else 0,
                is_active=subcategory_active if subcategory_active is not None else True,
            )
            db.add(subcategory)
            db.flush()
            created += 1
        else:
            if _apply_subcategory_updates(
                db,
                subcategory_repo,
                subcategory,
                subcategory_name,
                subcategory_code,
                subcategory_sort,
                subcategory_active,
            ):
                updated += 1

        specialty_name = _coerce_str(data.get("specialty_name"))
        specialty_code = _coerce_str(data.get("specialty_code"))
        specialty_sort = _coerce_int(data.get("specialty_sort"))
        specialty_active = _coerce_bool(data.get("specialty_active"))
        if not specialty_name and not specialty_code:
            continue
        if specialty_name and not specialty_code:
            errors.append(
                {
                    "row": row_index,
                    "level": "specialty",
                    "detail": f"第{row_index}行：专业编码缺失",
                }
            )
            skipped += 1
            continue

        specialty = None
        if specialty_code:
            specialty = specialty_repo.get_by_code(specialty_code)
            if specialty and specialty.subcategory_id != subcategory.id:
                skipped += 1
                continue
        elif specialty_name:
            specialty = specialty_repo.get_by_subcategory_and_name(
                subcategory.id, specialty_name
            )
        if specialty is None:
            if not specialty_name:
                skipped += 1
                continue
            specialty = Specialty(
                subcategory_id=subcategory.id,
                name=specialty_name,
                code=specialty_code,
                sort_order=specialty_sort if specialty_sort is not None else 0,
                is_active=specialty_active if specialty_active is not None else True,
            )
            db.add(specialty)
            db.flush()
            created += 1
        else:
            if _apply_specialty_updates(
                db,
                specialty_repo,
                specialty,
                specialty_name,
                specialty_code,
                specialty_sort,
                specialty_active,
            ):
                updated += 1

    db.commit()
    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }


def export_categories(db: Session) -> BytesIO:
    categories = list_category_tree(db)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(EXPORT_HEADERS)

    for category in categories:
        category_row = [
            category.name,
            category.code,
            category.sort_order,
            category.is_active,
        ]
        subcategories = getattr(category, "subcategories", [])
        if not subcategories:
            worksheet.append(category_row + ["", "", "", "", "", "", "", ""])
            continue
        for subcategory in subcategories:
            subcategory_row = [
                subcategory.name,
                subcategory.code,
                subcategory.sort_order,
                subcategory.is_active,
            ]
            specialties = getattr(subcategory, "specialties", [])
            if not specialties:
                worksheet.append(category_row + subcategory_row + ["", "", "", ""])
                continue
            for specialty in specialties:
                specialty_row = [
                    specialty.name,
                    specialty.code,
                    specialty.sort_order,
                    specialty.is_active,
                ]
                worksheet.append(category_row + subcategory_row + specialty_row)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
