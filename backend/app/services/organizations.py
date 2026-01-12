from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.models.expert import Expert
from app.models.organization import Organization
from app.repo.organizations import OrganizationRepo
from app.schemas.pagination import PageParams
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


def _generate_unique_code(repo: OrganizationRepo) -> str:
    code = generate_code(prefix="org")
    while repo.get_by_code(code):
        code = generate_code(prefix="org")
    return code


def list_organizations(db: Session, params: PageParams) -> tuple[list[Organization], int]:
    items, total = OrganizationRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )
    _attach_expert_counts(db, items)
    return items, total


def list_organizations_all(db: Session) -> list[Organization]:
    items = OrganizationRepo(db).list()
    _attach_expert_counts(db, items)
    return items


def get_organization(db: Session, organization_id: int) -> Organization:
    organization = OrganizationRepo(db).get_by_id(organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return organization


def _ensure_unique(
    db: Session, name: str | None, code: str | None, exclude_id: int | None = None
) -> None:
    repo = OrganizationRepo(db)
    if name:
        existing = repo.get_by_name(name)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name already exists",
            )
    if code:
        existing = repo.get_by_code(code)
        if existing and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization code already exists",
            )


def create_organization(db: Session, payload: OrganizationCreate) -> Organization:
    _ensure_unique(db, payload.name, payload.code)
    organization = Organization(**payload.model_dump())
    if not organization.code:
        organization.code = _generate_unique_code(OrganizationRepo(db))
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def update_organization(
    db: Session, organization_id: int, payload: OrganizationUpdate
) -> Organization:
    organization = get_organization(db, organization_id)
    update_data = payload.model_dump(exclude_unset=True)
    _ensure_unique(
        db, update_data.get("name"), update_data.get("code"), exclude_id=organization_id
    )

    old_name = organization.name
    name_changed = "name" in update_data and update_data["name"] != organization.name
    for key, value in update_data.items():
        setattr(organization, key, value)

    if name_changed:
        db.execute(
            Expert.__table__.update()
            .where(Expert.organization_id == organization_id)
            .values(company=organization.name)
        )
        db.execute(
            Expert.__table__.update()
            .where(Expert.organization_id.is_(None), Expert.company == old_name)
            .values(company=organization.name)
        )

    db.commit()
    db.refresh(organization)
    return organization


def delete_organization(db: Session, organization_id: int) -> None:
    organization = get_organization(db, organization_id)
    in_use = (
        db.execute(
            select(Expert.id).where(
                (Expert.organization_id == organization_id)
                | (Expert.company == organization.name)
            )
        ).first()
        is not None
    )
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is in use",
        )

    db.delete(organization)
    db.commit()


def delete_organizations(db: Session, organization_ids: list[int]) -> dict[str, int]:
    unique_ids = []
    for item in organization_ids:
        if isinstance(item, int):
            unique_ids.append(item)
    if not unique_ids:
        return {"deleted": 0, "skipped": 0}

    deleted = 0
    skipped = 0
    for organization_id in set(unique_ids):
        try:
            delete_organization(db, organization_id)
            deleted += 1
        except HTTPException:
            db.rollback()
            skipped += 1
        except Exception:
            db.rollback()
            raise
    return {"deleted": deleted, "skipped": skipped}


def resolve_organization(
    db: Session,
    organization_id: int | None,
    organization_name: str | None,
    strict: bool = True,
    create_if_missing: bool = False,
) -> Organization | None:
    repo = OrganizationRepo(db)
    organization = None
    if organization_id is not None:
        organization = repo.get_by_id(organization_id)
        if organization is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
    elif organization_name:
        organization = repo.get_by_name(organization_name)
        if organization is None and strict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        if organization is None and create_if_missing:
            organization = Organization(
                name=organization_name,
                code=_generate_unique_code(repo),
                is_active=True,
                sort_order=0,
            )
            db.add(organization)
            db.flush()
    return organization


def _attach_expert_counts(db: Session, items: list[Organization]) -> None:
    if not items:
        return
    org_ids = [item.id for item in items]
    org_names = [item.name for item in items if item.name]
    id_counts = dict(
        db.execute(
            select(Expert.organization_id, func.count())
            .where(Expert.organization_id.in_(org_ids))
            .group_by(Expert.organization_id)
        ).all()
    )
    name_counts: dict[str, int] = {}
    if org_names:
        name_counts = dict(
            db.execute(
                select(Expert.company, func.count())
                .where(
                    Expert.organization_id.is_(None),
                    Expert.company.in_(org_names),
                )
                .group_by(Expert.company)
            ).all()
        )
    for item in items:
        count = int(id_counts.get(item.id, 0))
        if item.name:
            count += int(name_counts.get(item.name, 0))
        setattr(item, "expert_count", count)
