from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role import Role
from app.repo.permissions import PermissionRepo
from app.repo.roles import RoleRepo
from app.schemas.role import RoleCreate, RolePermissionsUpdate, RoleUpdate


def list_roles(db: Session) -> list[Role]:
    return RoleRepo(db).list()


def get_role(db: Session, role_id: int) -> Role:
    role = RoleRepo(db).get_by_id(role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


def create_role(db: Session, payload: RoleCreate) -> Role:
    repo = RoleRepo(db)
    if repo.get_by_name(payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Role already exists"
        )

    role = Role(name=payload.name, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, payload: RoleUpdate) -> Role:
    role = get_role(db, role_id)
    if payload.name and payload.name != role.name:
        if RoleRepo(db).get_by_name(payload.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists",
            )
        role.name = payload.name
    if payload.description is not None:
        role.description = payload.description

    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> None:
    role = get_role(db, role_id)
    db.delete(role)
    db.commit()


def assign_permissions(
    db: Session, role_id: int, payload: RolePermissionsUpdate
) -> Role:
    role = get_role(db, role_id)
    permission_ids = sorted(set(payload.permission_ids))
    permissions = PermissionRepo(db).list_by_ids(permission_ids)
    if len(permissions) != len(permission_ids):
        found_ids = {permission.id for permission in permissions}
        missing = [
            str(permission_id)
            for permission_id in permission_ids
            if permission_id not in found_ids
        ]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permissions not found: {', '.join(missing)}",
        )
    role.permissions = permissions
    db.commit()
    db.refresh(role)
    return role
