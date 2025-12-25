from typing import Any, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.repo.users import UserRepo

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "expert:read": "查看专家信息",
        "expert:write": "新增或修改专家信息",
        "rule:read": "查看抽取规则",
        "rule:write": "新增或修改抽取规则",
        "category:read": "查看专业类别",
        "category:write": "管理专业类别",
        "subcategory:read": "查看专业子类",
        "subcategory:write": "管理专业子类",
        "organization:read": "查看单位枚举",
        "organization:write": "管理单位枚举",
        "title:read": "查看职称枚举",
        "title:write": "管理职称枚举",
        "draw:read": "查看抽取申请与结果",
        "draw:apply": "发起专家抽取申请",
        "draw:execute": "执行专家抽取",
        "user:read": "查看用户信息",
        "user:write": "新增或修改用户信息",
        "role:write": "管理角色与权限",
    },
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_user_and_payload(token: str, db: Session) -> tuple[User, dict[str, Any]]:
    payload = decode_access_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc

    user = UserRepo(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return user, payload


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user, _payload = _get_user_and_payload(token, db)
    return user


def require_scopes(required_scopes: list[str]):
    def dependency(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> None:
        _user, payload = _get_user_and_payload(token, db)
        token_scopes = payload.get("scopes", [])
        if "*" in token_scopes:
            return None
        missing = [scope for scope in required_scopes if scope not in token_scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return None

    return dependency
