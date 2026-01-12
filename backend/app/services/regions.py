from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.expert import Expert
from app.models.region import Region
from app.repo.regions import RegionRepo
from app.schemas.pagination import PageParams
from app.schemas.region import RegionCreate, RegionUpdate


def _generate_unique_code(repo: RegionRepo) -> str:
    code = generate_code(prefix="region")
    while repo.get_by_code(code):
        code = generate_code(prefix="region")
    return code


def list_regions(db: Session, params: PageParams) -> tuple[list[Region], int]:
    items, total = RegionRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )
    _attach_expert_counts(db, items)
    return items, total


def list_regions_all(db: Session) -> list[Region]:
    items = RegionRepo(db).list()
    _attach_expert_counts(db, items)
    return items


def get_region(db: Session, region_id: int) -> Region:
    region = RegionRepo(db).get_by_id(region_id)
    if region is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Region not found"
        )
    return region


def _ensure_unique(
    db: Session, name: str | None, code: str | None, exclude_id: int | None = None
) -> None:
    repo = RegionRepo(db)
    if name:
        existing = repo.get_by_name(name)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region name already exists",
            )
    if code:
        existing = repo.get_by_code(code)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region code already exists",
            )


def create_region(db: Session, payload: RegionCreate) -> Region:
    _ensure_unique(db, payload.name, payload.code)
    region = Region(**payload.model_dump())
    if not region.code:
        region.code = _generate_unique_code(RegionRepo(db))
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def update_region(db: Session, region_id: int, payload: RegionUpdate) -> Region:
    region = get_region(db, region_id)
    update_data = payload.model_dump(exclude_unset=True)
    _ensure_unique(
        db, update_data.get("name"), update_data.get("code"), exclude_id=region_id
    )

    old_name = region.name
    name_changed = "name" in update_data and update_data["name"] != region.name
    for key, value in update_data.items():
        setattr(region, key, value)

    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.region_id == region_id)
            .values(region=region.name)
        )
        db.execute(
            Expert.__table__.update()
            .where(Expert.region_id.is_(None), Expert.region == old_name)
            .values(region=region.name)
        )

    db.commit()
    db.refresh(region)
    return region


def delete_region(db: Session, region_id: int) -> None:
    region = get_region(db, region_id)
    in_use = (
        db.execute(
            select(Expert.id).where(
                (Expert.region_id == region_id) | (Expert.region == region.name)
            )
        ).first()
        is not None
    )
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Region is in use",
        )

    db.delete(region)
    db.commit()


def delete_regions(db: Session, region_ids: list[int]) -> dict[str, int]:
    unique_ids = []
    for item in region_ids:
        if isinstance(item, int):
            unique_ids.append(item)
    if not unique_ids:
        return {"deleted": 0, "skipped": 0}

    deleted = 0
    skipped = 0
    for region_id in set(unique_ids):
        try:
            delete_region(db, region_id)
            deleted += 1
        except HTTPException:
            db.rollback()
            skipped += 1
        except Exception:
            db.rollback()
            raise
    return {"deleted": deleted, "skipped": skipped}


def resolve_region(
    db: Session,
    region_id: int | None,
    region_name: str | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Region | None:
    repo = RegionRepo(db)
    region = None
    if region_id is not None:
        region = repo.get_by_id(region_id)
        if region is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found",
            )
    elif region_name:
        region = repo.get_by_name(region_name)
        if region is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found",
            )
        if region is None and create_if_missing:
            region = Region(
                name=region_name,
                code=_generate_unique_code(repo),
                is_active=True,
                sort_order=0,
            )
            db.add(region)
            db.flush()
    return region


def _attach_expert_counts(db: Session, items: list[Region]) -> None:
    if not items:
        return
    region_ids = [item.id for item in items]
    region_names = [item.name for item in items if item.name]
    id_counts = dict(
        db.execute(
            select(Expert.region_id, func.count())
            .where(Expert.region_id.in_(region_ids))
            .group_by(Expert.region_id)
        ).all()
    )
    name_counts: dict[str, int] = {}
    if region_names:
        name_counts = dict(
            db.execute(
                select(Expert.region, func.count())
                .where(
                    Expert.region_id.is_(None),
                    Expert.region.in_(region_names),
                )
                .group_by(Expert.region)
            ).all()
        )
    for item in items:
        count = int(id_counts.get(item.id, 0))
        if item.name:
            count += int(name_counts.get(item.name, 0))
        setattr(item, "expert_count", count)
