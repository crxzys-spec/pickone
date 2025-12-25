from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repo.users import UserRepo


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = UserRepo(db).get_by_username(username)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_scopes(user: User) -> list[str]:
    if user.is_superuser:
        return ["*"]
    scopes: set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            if permission.scope:
                scopes.add(permission.scope)
    return sorted(scopes)


def create_user_token(user: User) -> tuple[str, list[str]]:
    scopes = build_scopes(user)
    token = create_access_token(subject=str(user.id), scopes=scopes)
    return token, scopes
