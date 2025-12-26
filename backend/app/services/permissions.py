from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.repo.permissions import PermissionRepo
from app.schemas.pagination import PageParams
from app.schemas.permission import PermissionCreate, PermissionUpdate


def list_permissions(db: Session, params: PageParams) -> tuple[list[Permission], int]:
    return PermissionRepo(db).list_page(
        params.keyword,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size,
    )


def list_permissions_all(db: Session) -> list[Permission]:
    return PermissionRepo(db).list()


def get_permission(db: Session, permission_id: int) -> Permission:
    permission = PermissionRepo(db).get_by_id(permission_id)
    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return permission


def create_permission(db: Session, payload: PermissionCreate) -> Permission:
    repo = PermissionRepo(db)
    if repo.get_by_scope(payload.scope):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Scope already exists"
        )
    permission = Permission(
        name=payload.name, scope=payload.scope, description=payload.description
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def update_permission(
    db: Session, permission_id: int, payload: PermissionUpdate
) -> Permission:
    permission = get_permission(db, permission_id)
    if payload.scope and payload.scope != permission.scope:
        if PermissionRepo(db).get_by_scope(payload.scope):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Scope already exists",
            )
        permission.scope = payload.scope
    if payload.name is not None:
        permission.name = payload.name
    if payload.description is not None:
        permission.description = payload.description

    db.commit()
    db.refresh(permission)
    return permission


def delete_permission(db: Session, permission_id: int) -> None:
    permission = get_permission(db, permission_id)
    db.delete(permission)
    db.commit()
