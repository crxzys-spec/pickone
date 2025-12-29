from __future__ import annotations

import random
from io import BytesIO

from fastapi import HTTPException, status
from openpyxl import Workbook
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.draw import DrawApplication, DrawResult
from app.models.expert import Expert
from app.models.expert_specialty import ExpertSpecialty
from app.models.category import Category
from app.models.rule import Rule
from app.models.organization import Organization
from app.models.specialty import Specialty
from app.models.subcategory import Subcategory
from app.repo.draws import DrawRepo
from app.repo.rules import RuleRepo
from app.repo.utils import apply_keyword, apply_sort, paginate
from app.services import categories as category_service
from app.services import experts as expert_service
from app.services import specialties as specialty_service
from app.schemas.pagination import PageParams
from app.schemas.draw import DrawApply, DrawUpdate

SUPPORTED_DRAW_METHODS = {"random", "lottery"}


def _split_terms(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value
    for sep in ["、", "，", "；", ",", ";", "|", "\n"]:
        normalized = normalized.replace(sep, ";")
    return [item.strip() for item in normalized.split(";") if item.strip()]


def _split_numeric_terms(value: str | None) -> tuple[list[int], list[str]]:
    numeric: list[int] = []
    text: list[str] = []
    for item in _split_terms(value):
        if item.isdigit():
            numeric.append(int(item))
        else:
            text.append(item)
    return numeric, text


def _unique_ints(values: list[int] | None) -> list[int]:
    unique: list[int] = []
    for item in values or []:
        try:
            value = int(item)
        except (TypeError, ValueError):
            continue
        if value not in unique:
            unique.append(value)
    return unique


def _is_id_card(value: str) -> bool:
    normalized = value.strip().upper()
    if len(normalized) not in {15, 18}:
        return False
    if not normalized[:-1].isdigit():
        return False
    last = normalized[-1]
    return last.isdigit() or last == "X"


def _masked_id_parts(value: str) -> tuple[str, str] | None:
    normalized = value.strip().upper()
    if "*" not in normalized or len(normalized) < 8:
        return None
    prefix = normalized[:3]
    suffix = normalized[-4:]
    if not prefix.isdigit() or not suffix.isdigit():
        return None
    return prefix, suffix


def _split_person_terms(
    value: str | None,
) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    id_cards: list[str] = []
    names: list[str] = []
    masked_ids: list[tuple[str, str]] = []
    for item in _split_terms(value):
        normalized = item.strip()
        if not normalized:
            continue
        if _is_id_card(normalized):
            id_cards.append(normalized.upper())
            continue
        masked = _masked_id_parts(normalized)
        if masked:
            masked_ids.append(masked)
            continue
        names.append(normalized)
    return id_cards, names, masked_ids


def _mask_phone(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if len(raw) <= 7:
        return raw
    return f"{raw[:3]}{'*' * (len(raw) - 7)}{raw[-4:]}"


def _mask_id_card(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if len(raw) <= 7:
        return raw
    return f"{raw[:3]}{'*' * (len(raw) - 7)}{raw[-4:]}"


def _mask_name(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if len(raw) == 1:
        return raw
    if len(raw) == 2:
        return f"{raw[0]}*"
    return f"{raw[0]}{'*' * (len(raw) - 2)}{raw[-1]}"


def _find_active_rule_by_specialties(
    db: Session, specialty_ids: list[int], specialty_name: str | None
) -> Rule | None:
    if not specialty_ids and not specialty_name:
        return None
    stmt = select(Rule).where(Rule.is_active.is_(True)).order_by(Rule.id.desc())
    rules = db.execute(stmt).scalars().all()
    name_terms = _split_terms(specialty_name) if specialty_name else []
    specialty_id_set = set(specialty_ids)
    for rule in rules:
        rule_ids = _unique_ints(rule.specialty_ids)
        if specialty_id_set and rule_ids:
            if specialty_id_set.intersection(rule_ids):
                return rule
        if name_terms:
            rule_names = _split_terms(rule.specialty)
            if any(name in rule_names for name in name_terms):
                return rule
    return None


def resolve_draw_method(draw: DrawApplication, rule) -> str:
    if draw.draw_method:
        return draw.draw_method
    if rule is not None and rule.draw_method:
        return rule.draw_method
    return "random"


def pick_experts(
    candidates: list[Expert], total_needed: int, draw_method: str
) -> list[Expert]:
    if draw_method == "random":
        return random.sample(candidates, total_needed)
    if draw_method == "lottery":
        tickets = [(random.random(), expert) for expert in candidates]
        tickets.sort(key=lambda item: item[0])
        return [expert for _, expert in tickets[:total_needed]]
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported draw method",
    )


def list_draws(db: Session, params: PageParams) -> tuple[list[DrawApplication], int]:
    return DrawRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def get_draw(db: Session, draw_id: int) -> DrawApplication:
    draw = DrawRepo(db).get_by_id(draw_id)
    if draw is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draw not found")
    return draw


def create_draw(db: Session, payload: DrawApply, created_by_id: int | None) -> DrawApplication:
    data = payload.model_dump()
    rule = None
    if payload.rule_id is not None:
        rule = RuleRepo(db).get_by_id(payload.rule_id)
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )

    category = None
    subcategory = None
    specialty = None
    if rule is not None:
        rule_specialty_ids = _unique_ints(rule.specialty_ids)
        if rule_specialty_ids:
            if len(rule_specialty_ids) == 1:
                specialty = specialty_service.get_specialty(
                    db, rule_specialty_ids[0]
                )
        else:
            category = category_service.resolve_category(
                db, rule.category_id, rule.category, strict=False
            )
            if rule.category_id is not None and category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found",
                )
            if rule.subcategory_id is not None or rule.subcategory:
                subcategory = category_service.resolve_subcategory(
                    db, rule.subcategory_id, rule.subcategory, category, strict=False
                )
            if rule.specialty_id is not None or rule.specialty:
                if rule.specialty_id is not None:
                    specialty = specialty_service.get_specialty(
                        db, rule.specialty_id
                    )
                elif subcategory is not None:
                    specialty = specialty_service.resolve_specialty(
                        db, None, rule.specialty, subcategory.id, strict=False
                    )
        if specialty is not None and subcategory is None:
            subcategory = category_service.get_subcategory(db, specialty.subcategory_id)
        if subcategory is not None and category is None:
            category = category_service.get_category(db, subcategory.category_id)
    else:
        category = category_service.resolve_category(
            db, data.get("category_id"), data.get("category")
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required",
            )
        if data.get("subcategory_id") is not None or data.get("subcategory"):
            subcategory = category_service.resolve_subcategory(
                db, data.get("subcategory_id"), data.get("subcategory"), category
            )
        if data.get("specialty_id") is not None or data.get("specialty"):
            if data.get("specialty_id") is not None:
                specialty = specialty_service.get_specialty(db, data.get("specialty_id"))
                if subcategory and specialty.subcategory_id != subcategory.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Specialty does not belong to subcategory",
                    )
            else:
                if subcategory is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Subcategory is required for specialty",
                    )
                specialty = specialty_service.resolve_specialty(
                    db, None, data.get("specialty"), subcategory.id
                )
        if subcategory is None and specialty is not None:
            subcategory = category_service.get_subcategory(db, specialty.subcategory_id)
        if category is None and subcategory is not None:
            category = category_service.get_category(db, subcategory.category_id)

    draw = DrawApplication(**data, created_by_id=created_by_id)
    if rule is not None:
        draw.rule_id = rule.id
        draw.category_id = category.id if category else None
        draw.category = category.name if category else (rule.category or "不限")
        if subcategory:
            draw.subcategory_id = subcategory.id
            draw.subcategory = subcategory.name
        else:
            draw.subcategory_id = None
            draw.subcategory = rule.subcategory
        if specialty:
            draw.specialty_id = specialty.id
            draw.specialty = specialty.name
        else:
            draw.specialty_id = None
            draw.specialty = rule.specialty
    else:
        draw.category_id = category.id
        draw.category = category.name
        if subcategory:
            draw.subcategory_id = subcategory.id
            draw.subcategory = subcategory.name
        else:
            draw.subcategory_id = None
            draw.subcategory = None
        if specialty:
            draw.specialty_id = specialty.id
            draw.specialty = specialty.name
        else:
            draw.specialty_id = None
            draw.specialty = None
    db.add(draw)
    db.commit()
    db.refresh(draw)
    return draw


def update_draw(db: Session, draw_id: int, payload: DrawUpdate) -> DrawApplication:
    draw = get_draw(db, draw_id)
    update_data = payload.model_dump(exclude_unset=True)
    condition_fields = {
        "rule_id",
        "category_id",
        "category",
        "subcategory_id",
        "subcategory",
        "specialty_id",
        "specialty",
        "expert_count",
        "backup_count",
        "draw_method",
        "avoid_units",
        "avoid_persons",
    }
    original_conditions = {field: getattr(draw, field) for field in condition_fields}
    original_status = draw.status

    rule = None
    if "rule_id" in update_data:
        rule_id = update_data.get("rule_id")
        if rule_id is not None:
            rule = RuleRepo(db).get_by_id(rule_id)
            if rule is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
                )
            draw.rule_id = rule.id
            subcategory = None
            specialty = None
            category = None
            rule_specialty_ids = _unique_ints(rule.specialty_ids)
            if rule_specialty_ids:
                if len(rule_specialty_ids) == 1:
                    specialty = specialty_service.get_specialty(
                        db, rule_specialty_ids[0]
                    )
            else:
                category = category_service.resolve_category(
                    db, rule.category_id, rule.category, strict=False
                )
                if rule.category_id is not None and category is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found",
                    )
                if rule.subcategory_id is not None or rule.subcategory:
                    subcategory = category_service.resolve_subcategory(
                        db, rule.subcategory_id, rule.subcategory, category, strict=False
                    )
                if rule.specialty_id is not None or rule.specialty:
                    if rule.specialty_id is not None:
                        specialty = specialty_service.get_specialty(
                            db, rule.specialty_id
                        )
                    elif subcategory is not None:
                        specialty = specialty_service.resolve_specialty(
                            db, None, rule.specialty, subcategory.id, strict=False
                        )
            if specialty is not None and subcategory is None:
                subcategory = category_service.get_subcategory(
                    db, specialty.subcategory_id
                )
            if subcategory is not None and category is None:
                category = category_service.get_category(db, subcategory.category_id)
            draw.category_id = category.id if category else None
            draw.category = category.name if category else (rule.category or "不限")
            draw.subcategory_id = subcategory.id if subcategory else None
            draw.subcategory = (
                subcategory.name if subcategory else rule.subcategory
            )
            draw.specialty_id = specialty.id if specialty else None
            draw.specialty = specialty.name if specialty else rule.specialty
        else:
            draw.rule_id = None

    category_input = "category_id" in update_data or "category" in update_data
    subcategory_input = "subcategory_id" in update_data or "subcategory" in update_data
    specialty_input = "specialty_id" in update_data or "specialty" in update_data
    if rule is None and (category_input or subcategory_input or specialty_input):
        category = None
        if category_input:
            category = category_service.resolve_category(
                db, update_data.get("category_id"), update_data.get("category")
            )
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category is required",
                )

        subcategory = None
        subcategory_value = update_data.get("subcategory")
        subcategory_id_value = update_data.get("subcategory_id")
        if subcategory_input and (subcategory_id_value is not None or subcategory_value):
            subcategory = category_service.resolve_subcategory(
                db,
                subcategory_id_value,
                subcategory_value,
                category,
            )
            if subcategory and category is None:
                category = category_service.resolve_category(
                    db, subcategory.category_id, None
                )

        if category_input or (subcategory and not category_input):
            draw.category_id = category.id if category else None
            draw.category = category.name if category else update_data.get("category")
        if subcategory_input:
            draw.subcategory_id = subcategory.id if subcategory else None
            draw.subcategory = (
                subcategory.name if subcategory else update_data.get("subcategory")
            )

        specialty = None
        if specialty_input:
            specialty_id = update_data.get("specialty_id")
            specialty_name = update_data.get("specialty")
            if specialty_id is not None:
                specialty = specialty_service.get_specialty(db, specialty_id)
                if subcategory and specialty.subcategory_id != subcategory.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Specialty does not belong to subcategory",
                    )
            elif specialty_name:
                if subcategory is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Subcategory is required for specialty",
                    )
                specialty = specialty_service.resolve_specialty(
                    db, None, specialty_name, subcategory.id
                )
        if specialty_input:
            draw.specialty_id = specialty.id if specialty else None
            draw.specialty = specialty.name if specialty else update_data.get("specialty")
        elif category_input or subcategory_input:
            draw.specialty_id = None
            draw.specialty = None

    for key, value in update_data.items():
        if key in {
            "category_id",
            "category",
            "subcategory_id",
            "subcategory",
            "specialty_id",
            "specialty",
            "rule_id",
        }:
            continue
        setattr(draw, key, value)

    conditions_changed = any(
        getattr(draw, field) != original_conditions[field]
        for field in condition_fields
    )
    status_changed = "status" in update_data and update_data["status"] != original_status
    reset_results = conditions_changed
    if status_changed and update_data["status"] in {"pending", "scheduled"}:
        reset_results = True
    if reset_results:
        db.execute(delete(DrawResult).where(DrawResult.draw_id == draw_id))
        if "status" not in update_data and draw.status != "cancelled":
            draw.status = "pending"

    db.commit()
    db.refresh(draw)
    return draw


def delete_draw(db: Session, draw_id: int) -> None:
    draw = get_draw(db, draw_id)
    db.delete(draw)
    db.commit()


def delete_draws(db: Session, draw_ids: list[int]) -> dict[str, int]:
    unique_ids = {int(item) for item in draw_ids if isinstance(item, int)}
    if not unique_ids:
        return {"deleted": 0, "skipped": 0}
    existing = set(
        db.execute(select(DrawApplication.id).where(DrawApplication.id.in_(unique_ids)))
        .scalars()
        .all()
    )
    if not existing:
        return {"deleted": 0, "skipped": len(unique_ids)}
    db.execute(delete(DrawResult).where(DrawResult.draw_id.in_(existing)))
    db.execute(delete(DrawApplication).where(DrawApplication.id.in_(existing)))
    db.commit()
    return {"deleted": len(existing), "skipped": len(unique_ids) - len(existing)}


def list_results(db: Session, draw_id: int) -> list[DrawResult]:
    _ = get_draw(db, draw_id)
    stmt = (
        select(DrawResult)
        .where(DrawResult.draw_id == draw_id)
        .options(selectinload(DrawResult.expert))
        .order_by(DrawResult.is_backup, DrawResult.ordinal)
    )
    results = list(db.execute(stmt).scalars().all())
    experts = [result.expert for result in results if result.expert]
    expert_service._attach_expert_details(db, experts)
    return results


def export_results(db: Session, draw_id: int) -> BytesIO:
    draw = get_draw(db, draw_id)
    results = list_results(db, draw_id)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(
        [
            "抽取编号",
            "项目名称",
            "项目编号",
            "序号",
            "候补",
            "递补",
            "专家姓名",
            "单位",
            "专业",
            "职称",
            "电话",
            "邮箱",
            "身份证号",
        ]
    )

    for result in results:
        expert = result.expert
        specialties = getattr(expert, "specialties", []) if expert else []
        specialty_names = ";".join([item.name for item in specialties if item.name])
        worksheet.append(
            [
                draw.id,
                draw.project_name or "",
                draw.project_code or "",
                result.ordinal or "",
                "是" if result.is_backup else "否",
                "是" if result.is_replacement else "否",
                _mask_name(expert.name) if expert else "",
                expert.company if expert else "",
                specialty_names,
                expert.title if expert else "",
                _mask_phone(expert.phone) if expert else "",
                expert.email if expert else "",
                _mask_id_card(expert.id_card_no) if expert else "",
            ]
        )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def list_results_page(
    db: Session, draw_id: int, params: PageParams
) -> tuple[list[DrawResult], int]:
    _ = get_draw(db, draw_id)
    stmt = (
        select(DrawResult)
        .where(DrawResult.draw_id == draw_id)
        .options(selectinload(DrawResult.expert))
    )
    if params.keyword:
        stmt = stmt.join(Expert, Expert.id == DrawResult.expert_id, isouter=True)
        stmt = apply_keyword(
            stmt,
            params.keyword,
            [Expert.name, Expert.company, Expert.phone, Expert.email],
        )
    sort_map = {
        "id": DrawResult.id,
        "ordinal": DrawResult.ordinal,
        "is_backup": DrawResult.is_backup,
        "is_replacement": DrawResult.is_replacement,
    }
    if params.sort_by:
        stmt = apply_sort(
            stmt, params.sort_by, params.sort_order, sort_map, DrawResult.id
        )
    else:
        stmt = stmt.order_by(DrawResult.is_backup, DrawResult.ordinal, DrawResult.id)
    items, total = paginate(db, stmt, params.page, params.page_size)
    experts = [result.expert for result in items if result.expert]
    expert_service._attach_expert_details(db, experts)
    return items, total


def execute_draw(db: Session, draw_id: int) -> list[DrawResult]:
    draw = get_draw(db, draw_id)
    if draw.status == "completed":
        return list_results(db, draw.id)
    if draw.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Draw already completed or cancelled",
        )

    existing = db.execute(
        select(DrawResult.id).where(DrawResult.draw_id == draw.id)
    ).first()
    if existing:
        db.execute(delete(DrawResult).where(DrawResult.draw_id == draw.id))
        db.flush()

    rule = None
    if draw.rule_id is not None:
        rule = RuleRepo(db).get_by_id(draw.rule_id)
    if rule is None:
        if draw.specialty_id is not None:
            rule = RuleRepo(db).get_active_by_specialty_id(draw.specialty_id)
            if rule is None:
                rule = _find_active_rule_by_specialties(
                    db, [draw.specialty_id], None
                )
        elif draw.specialty:
            rule = RuleRepo(db).get_active_by_specialty(draw.specialty)
            if rule is None:
                rule = _find_active_rule_by_specialties(db, [], draw.specialty)
        elif draw.subcategory_id is not None:
            rule = RuleRepo(db).get_active_by_category_and_subcategory_id(
                draw.category_id, draw.subcategory_id
            )
            if rule is None and draw.category_id is not None:
                rule = RuleRepo(db).get_active_by_category_id(draw.category_id)
        elif draw.subcategory:
            if draw.category:
                rule = RuleRepo(db).get_active_by_category_and_subcategory(
                    draw.category, draw.subcategory
                )
            if rule is None and draw.category:
                rule = RuleRepo(db).get_active_by_category(draw.category)
        elif draw.category_id is not None:
            rule = RuleRepo(db).get_active_by_category_id(draw.category_id)
        elif draw.category:
            rule = RuleRepo(db).get_active_by_category(draw.category)
        if rule is not None:
            draw.rule_id = rule.id

    stmt = select(Expert).where(Expert.is_active.is_(True)).distinct()
    rule_specialty_ids = _unique_ints(rule.specialty_ids) if rule else []
    specialty_ids = rule_specialty_ids
    if not specialty_ids:
        if rule is not None and rule.specialty_id is not None:
            specialty_ids = [rule.specialty_id]
        elif draw.specialty_id is not None:
            specialty_ids = [draw.specialty_id]
    specialty_names = []
    if not specialty_ids:
        specialty_name = draw.specialty or (rule.specialty if rule else None)
        specialty_names = _split_terms(specialty_name)
    subcategory_id = draw.subcategory_id or (rule.subcategory_id if rule else None)
    subcategory_name = draw.subcategory or (rule.subcategory if rule else None)
    category_id = draw.category_id or (rule.category_id if rule else None)
    category_name = draw.category or (rule.category if rule else None)
    if category_name in {"不限", "多专业"}:
        category_name = None

    if (
        specialty_ids
        or specialty_names
        or subcategory_id is not None
        or subcategory_name
        or category_id is not None
        or category_name
    ):
        stmt = stmt.join(
            ExpertSpecialty, ExpertSpecialty.expert_id == Expert.id
        ).join(Specialty, Specialty.id == ExpertSpecialty.specialty_id)
        if specialty_ids:
            stmt = stmt.where(Specialty.id.in_(specialty_ids))
        elif specialty_names:
            stmt = stmt.where(Specialty.name.in_(specialty_names))
        else:
            stmt = stmt.join(Subcategory, Subcategory.id == Specialty.subcategory_id)
            if subcategory_id is not None:
                stmt = stmt.where(Subcategory.id == subcategory_id)
            elif subcategory_name:
                stmt = stmt.where(Subcategory.name == subcategory_name)
            if category_id is not None or category_name:
                stmt = stmt.join(Category, Category.id == Subcategory.category_id)
                if category_id is not None:
                    stmt = stmt.where(Category.id == category_id)
                elif category_name:
                    stmt = stmt.where(Category.name == category_name)
    if rule is not None:
        title_required_ids = _unique_ints(rule.title_required_ids)
        title_names = _split_terms(rule.title_required)
        if title_required_ids:
            if title_names:
                stmt = stmt.where(
                    or_(
                        Expert.title_id.in_(title_required_ids),
                        Expert.title.in_(title_names),
                    )
                )
            else:
                stmt = stmt.where(Expert.title_id.in_(title_required_ids))
        elif rule.title_required:
            stmt = stmt.where(Expert.title.in_(title_names))
        region_required_ids = _unique_ints(rule.region_required_ids)
        region_names = _split_terms(rule.region_required)
        if region_required_ids:
            if region_names:
                stmt = stmt.where(
                    or_(
                        Expert.region_id.in_(region_required_ids),
                        Expert.region.in_(region_names),
                    )
                )
            else:
                stmt = stmt.where(Expert.region_id.in_(region_required_ids))
        elif rule.region_required_id is not None:
            stmt = stmt.where(Expert.region_id == rule.region_required_id)
        elif rule.region_required:
            stmt = stmt.where(Expert.region.in_(region_names))
    avoid_unit_ids, avoid_unit_names = _split_numeric_terms(draw.avoid_units)
    if avoid_unit_names:
        matched_ids = (
            db.execute(
                select(Organization.id).where(Organization.name.in_(avoid_unit_names))
            )
            .scalars()
            .all()
        )
        for org_id in matched_ids:
            if org_id not in avoid_unit_ids:
                avoid_unit_ids.append(org_id)
    if avoid_unit_ids:
        stmt = stmt.where(
            or_(Expert.organization_id.is_(None), ~Expert.organization_id.in_(avoid_unit_ids))
        )
    if avoid_unit_names:
        unit_matches = [Expert.company.contains(item) for item in avoid_unit_names]
        stmt = stmt.where(or_(Expert.company.is_(None), ~or_(*unit_matches)))

    avoid_person_ids, avoid_person_names, avoid_person_masks = _split_person_terms(
        draw.avoid_persons
    )
    if avoid_person_ids:
        stmt = stmt.where(~func.upper(Expert.id_card_no).in_(avoid_person_ids))
    if avoid_person_masks:
        mask_conditions = [
            Expert.id_card_no.startswith(prefix)
            & Expert.id_card_no.endswith(suffix)
            for prefix, suffix in avoid_person_masks
        ]
        stmt = stmt.where(~or_(*mask_conditions))
    if avoid_person_names:
        person_matches = [Expert.name.contains(item) for item in avoid_person_names]
        stmt = stmt.where(~or_(*person_matches))

    candidates = list(db.execute(stmt).scalars().all())
    backup_count = draw.backup_count or 0
    total_needed = draw.expert_count + backup_count
    if len(candidates) < total_needed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough qualified experts",
        )

    method = resolve_draw_method(draw, rule)
    if method not in SUPPORTED_DRAW_METHODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported draw method",
        )
    chosen = pick_experts(candidates, total_needed, method)
    for index, expert in enumerate(chosen, start=1):
        is_backup = index > draw.expert_count
        result = DrawResult(
            draw_id=draw.id,
            expert_id=expert.id,
            is_backup=is_backup,
            ordinal=index,
        )
        db.add(result)

    draw.draw_method = method
    draw.status = "completed"
    db.commit()

    return list_results(db, draw.id)


def replace_draw_result(db: Session, draw_id: int, result_id: int) -> list[DrawResult]:
    draw = get_draw(db, draw_id)
    if draw.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Draw is not completed",
        )

    target = db.execute(
        select(DrawResult).where(
            DrawResult.draw_id == draw.id, DrawResult.id == result_id
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Result not found"
        )
    if target.is_backup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot replace a backup expert",
        )

    backup = (
        db.execute(
            select(DrawResult)
            .where(DrawResult.draw_id == draw.id, DrawResult.is_backup.is_(True))
            .order_by(DrawResult.ordinal, DrawResult.id)
        )
        .scalars()
        .first()
    )
    if backup is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backup experts available",
        )

    target_ordinal = target.ordinal
    db.delete(target)
    backup.is_backup = False
    backup.is_replacement = True
    if target_ordinal is not None:
        backup.ordinal = target_ordinal
    db.commit()

    return list_results(db, draw.id)
