from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repo.roles import RoleRepo
from app.repo.users import UserRepo
from app.schemas.user import (
    UserCreate,
    UserPasswordChange,
    UserRolesUpdate,
    UserSelfUpdate,
    UserUpdate,
)


def list_users(db: Session) -> list[User]:
    return UserRepo(db).list()


def get_user(db: Session, user_id: int) -> User:
    user = UserRepo(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    repo = UserRepo(db)
    if repo.get_by_username(payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        email=payload.email,
        is_active=payload.is_active,
        is_superuser=payload.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    if payload.username and payload.username != user.username:
        if UserRepo(db).get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )
        user.username = payload.username

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        user.email = payload.email
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_superuser is not None:
        user.is_superuser = payload.is_superuser
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)

    db.commit()
    db.refresh(user)
    return user


def update_self(db: Session, user: User, payload: UserSelfUpdate) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        user.email = payload.email
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, payload: UserPasswordChange) -> None:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()


def assign_roles(db: Session, user_id: int, payload: UserRolesUpdate) -> User:
    user = get_user(db, user_id)
    role_ids = sorted(set(payload.role_ids))
    roles = RoleRepo(db).list_by_ids(role_ids)
    if len(roles) != len(role_ids):
        found_ids = {role.id for role in roles}
        missing = [str(role_id) for role_id in role_ids if role_id not in found_ids]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roles not found: {', '.join(missing)}",
        )
    user.roles = roles
    db.commit()
    db.refresh(user)
    return user
