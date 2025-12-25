from io import BytesIO

from fastapi import HTTPException, status
from openpyxl import Workbook, load_workbook
from sqlalchemy.orm import Session

from app.models.expert import Expert
from app.repo.experts import ExpertRepo
from app.services import organizations as organization_service
from app.services import titles as title_service
from app.services import categories as category_service
from app.schemas.expert import ExpertCreate, ExpertUpdate

EXPORT_FIELDS = [
    ("name", "姓名"),
    ("gender", "性别"),
    ("phone", "电话"),
    ("email", "邮箱"),
    ("company", "单位"),
    ("title", "职称"),
    ("category", "专业"),
    ("subcategory", "子专业"),
    ("avoid_units", "回避单位"),
    ("avoid_persons", "回避人员"),
    ("is_active", "启用"),
]
EXPORT_HEADERS = [label for _, label in EXPORT_FIELDS]
HEADER_MAP = {label.lower(): field for field, label in EXPORT_FIELDS}
LEGACY_HEADER_MAP = {
    "name": "name",
    "gender": "gender",
    "phone": "phone",
    "email": "email",
    "company": "company",
    "title": "title",
    "category": "category",
    "subcategory": "subcategory",
    "avoidunits": "avoid_units",
    "avoid units": "avoid_units",
    "avoidpersons": "avoid_persons",
    "avoid persons": "avoid_persons",
    "isactive": "is_active",
    "is active": "is_active",
}
HEADER_MAP.update(LEGACY_HEADER_MAP)
HEADER_MAP.update({field: field for field, _ in EXPORT_FIELDS})


def _coerce_str(value: object | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)
    return str(value).strip()


def _coerce_bool(value: object | None, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, float):
        return bool(int(value))
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y"}:
            return True
        if normalized in {"0", "false", "no", "n"}:
            return False
    return default


def list_experts(db: Session) -> list[Expert]:
    return ExpertRepo(db).list()


def get_expert(db: Session, expert_id: int) -> Expert:
    expert = ExpertRepo(db).get_by_id(expert_id)
    if expert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expert not found"
        )
    return expert


def create_expert(db: Session, payload: ExpertCreate) -> Expert:
    data = payload.model_dump()
    category = category_service.resolve_category(
        db, data.get("category_id"), data.get("category")
    )
    subcategory = category_service.resolve_subcategory(
        db, data.get("subcategory_id"), data.get("subcategory"), category
    )
    if subcategory and category is None:
        category = category_service.resolve_category(
            db, subcategory.category_id, None
        )

    organization = organization_service.resolve_organization(
        db,
        data.get("organization_id"),
        data.get("company"),
        strict=data.get("organization_id") is not None,
    )
    title = title_service.resolve_title(
        db,
        data.get("title_id"),
        data.get("title"),
        strict=data.get("title_id") is not None,
    )

    expert = Expert(**data)
    if organization:
        expert.organization_id = organization.id
        expert.company = organization.name
    if title:
        expert.title_id = title.id
        expert.title = title.name
    if category:
        expert.category_id = category.id
        expert.category = category.name
    if subcategory:
        expert.subcategory_id = subcategory.id
        expert.subcategory = subcategory.name
    db.add(expert)
    db.commit()
    db.refresh(expert)
    return expert


def update_expert(db: Session, expert_id: int, payload: ExpertUpdate) -> Expert:
    expert = get_expert(db, expert_id)
    update_data = payload.model_dump(exclude_unset=True)
    category_input = "category_id" in update_data or "category" in update_data
    subcategory_input = "subcategory_id" in update_data or "subcategory" in update_data
    organization_input = (
        "organization_id" in update_data or "company" in update_data
    )
    title_input = "title_id" in update_data or "title" in update_data

    if category_input or subcategory_input:
        category = category_service.resolve_category(
            db, update_data.get("category_id"), update_data.get("category")
        )
        subcategory = category_service.resolve_subcategory(
            db,
            update_data.get("subcategory_id"),
            update_data.get("subcategory"),
            category,
        )
        if subcategory and category is None:
            category = category_service.resolve_category(
                db, subcategory.category_id, None
            )
        if category_input or (subcategory and not category_input):
            expert.category_id = category.id if category else None
            expert.category = category.name if category else update_data.get("category")
        if subcategory_input:
            expert.subcategory_id = subcategory.id if subcategory else None
            expert.subcategory = (
                subcategory.name if subcategory else update_data.get("subcategory")
            )

    if organization_input:
        organization = organization_service.resolve_organization(
            db,
            update_data.get("organization_id"),
            update_data.get("company"),
            strict=update_data.get("organization_id") is not None,
        )
        if organization:
            expert.organization_id = organization.id
            expert.company = organization.name
        else:
            expert.organization_id = update_data.get("organization_id")
            if "company" in update_data:
                expert.company = update_data.get("company")

    if title_input:
        title = title_service.resolve_title(
            db,
            update_data.get("title_id"),
            update_data.get("title"),
            strict=update_data.get("title_id") is not None,
        )
        if title:
            expert.title_id = title.id
            expert.title = title.name
        else:
            expert.title_id = update_data.get("title_id")
            if "title" in update_data:
                expert.title = update_data.get("title")

    for key, value in update_data.items():
        if key in {
            "category_id",
            "category",
            "subcategory_id",
            "subcategory",
            "organization_id",
            "company",
            "title_id",
            "title",
        }:
            continue
        setattr(expert, key, value)
    db.commit()
    db.refresh(expert)
    return expert


def delete_expert(db: Session, expert_id: int) -> None:
    expert = get_expert(db, expert_id)
    db.delete(expert)
    db.commit()


def import_experts(db: Session, file) -> dict[str, int]:
    file.file.seek(0)
    workbook = load_workbook(file.file, data_only=True)
    worksheet = workbook.active

    rows = worksheet.iter_rows(values_only=True)
    header_row = next(rows, None)
    if not header_row:
        return {"created": 0, "skipped": 0}

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
    skipped = 0
    for row in rows:
        if not row or all(cell is None for cell in row):
            continue
        data: dict[str, object | None] = {}
        for idx, field in index_to_field.items():
            value = row[idx] if idx < len(row) else None
            data[field] = value

        name = _coerce_str(data.get("name"))
        if not name:
            skipped += 1
            continue

        expert = Expert(
            name=name,
            gender=_coerce_str(data.get("gender")),
            phone=_coerce_str(data.get("phone")),
            email=_coerce_str(data.get("email")),
            company=_coerce_str(data.get("company")),
            title=_coerce_str(data.get("title")),
            category=_coerce_str(data.get("category")),
            subcategory=_coerce_str(data.get("subcategory")),
            avoid_units=_coerce_str(data.get("avoid_units")),
            avoid_persons=_coerce_str(data.get("avoid_persons")),
            is_active=_coerce_bool(data.get("is_active"), True),
        )
        category = category_service.resolve_category(
            db,
            None,
            expert.category,
            strict=False,
            create_if_missing=True,
        )
        subcategory = category_service.resolve_subcategory(
            db,
            None,
            expert.subcategory,
            category,
            strict=False,
            create_if_missing=True,
        )
        organization = organization_service.resolve_organization(
            db,
            None,
            expert.company,
            strict=False,
            create_if_missing=True,
        )
        title = title_service.resolve_title(
            db,
            None,
            expert.title,
            strict=False,
            create_if_missing=True,
        )
        if subcategory and category is None:
            category = category_service.resolve_category(
                db, subcategory.category_id, None, strict=False
            )
        if category:
            expert.category_id = category.id
            expert.category = category.name
        if subcategory:
            expert.subcategory_id = subcategory.id
            expert.subcategory = subcategory.name
        if organization:
            expert.organization_id = organization.id
            expert.company = organization.name
        if title:
            expert.title_id = title.id
            expert.title = title.name
        db.add(expert)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}


def export_experts(db: Session) -> BytesIO:
    experts = ExpertRepo(db).list()
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(EXPORT_HEADERS)

    for expert in experts:
        row = [getattr(expert, field) for field, _ in EXPORT_FIELDS]
        worksheet.append(row)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
