import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User

SCOPE_DEFINITIONS = {
    "expert:read": {"name": "专家查看", "description": "查看专家信息"},
    "expert:write": {"name": "专家维护", "description": "新增或修改专家信息"},
    "rule:read": {"name": "规则查看", "description": "查看抽取规则"},
    "rule:write": {"name": "规则维护", "description": "新增或修改抽取规则"},
    "category:read": {"name": "类别查看", "description": "查看专业类别"},
    "category:write": {"name": "类别管理", "description": "管理专业类别"},
    "subcategory:read": {"name": "子类查看", "description": "查看专业子类"},
    "subcategory:write": {"name": "子类管理", "description": "管理专业子类"},
    "organization:read": {"name": "单位查看", "description": "查看单位枚举"},
    "organization:write": {"name": "单位管理", "description": "管理单位枚举"},
    "title:read": {"name": "职称查看", "description": "查看职称枚举"},
    "title:write": {"name": "职称管理", "description": "管理职称枚举"},
    "draw:read": {"name": "抽取查看", "description": "查看抽取申请与结果"},
    "draw:apply": {"name": "抽取申请", "description": "发起专家抽取申请"},
    "draw:execute": {"name": "抽取执行", "description": "执行专家抽取"},
    "user:read": {"name": "用户查看", "description": "查看用户信息"},
    "user:write": {"name": "用户管理", "description": "新增或修改用户信息"},
    "role:write": {"name": "角色管理", "description": "管理角色与权限"},
}

DEPRECATED_SCOPES = {"expert:approve"}

ROLE_NAME_MAP = {
    "admin": "系统管理员",
    "operator": "业务操作员",
    "rule-admin": "规则管理员",
    "user-admin": "用户管理员",
}

DEPRECATED_ROLE_NAMES = {"auditor", "专家审核员"}

ROLE_DEFS = {
    ROLE_NAME_MAP["admin"]: {
        "description": "系统管理员",
        "scopes": list(SCOPE_DEFINITIONS.keys()),
    },
    ROLE_NAME_MAP["operator"]: {
        "description": "业务操作员",
        "scopes": [
            "expert:read",
            "expert:write",
            "category:read",
            "subcategory:read",
            "organization:read",
            "title:read",
            "draw:read",
            "draw:apply",
            "rule:read",
        ],
    },
    ROLE_NAME_MAP["rule-admin"]: {
        "description": "规则管理员",
        "scopes": [
            "category:read",
            "rule:read",
            "rule:write",
        ],
    },
    ROLE_NAME_MAP["user-admin"]: {
        "description": "用户管理员",
        "scopes": [
            "user:read",
            "user:write",
            "role:write",
        ],
    },
}


def seed_permissions(db: Session) -> dict[str, Permission]:
    existing = db.execute(select(Permission)).scalars().all()
    by_scope = {perm.scope: perm for perm in existing}

    for scope in DEPRECATED_SCOPES:
        permission = by_scope.pop(scope, None)
        if permission is not None:
            db.delete(permission)

    for scope, definition in SCOPE_DEFINITIONS.items():
        name = definition["name"]
        description = definition["description"]
        permission = by_scope.get(scope)
        if permission is None:
            permission = Permission(scope=scope, name=name, description=description)
            db.add(permission)
            by_scope[scope] = permission
        else:
            permission.name = name
            permission.description = description

    db.flush()
    return by_scope


def seed_roles(db: Session, permissions: dict[str, Permission]) -> dict[str, Role]:
    existing = db.execute(select(Role)).scalars().all()
    by_name = {role.name: role for role in existing}
    legacy_name_map = {new: old for old, new in ROLE_NAME_MAP.items()}
    role_map: dict[str, Role] = {}

    for role_name in DEPRECATED_ROLE_NAMES:
        role = by_name.pop(role_name, None)
        if role is not None:
            db.delete(role)

    for name, definition in ROLE_DEFS.items():
        role = by_name.get(name)
        if role is None:
            legacy_name = legacy_name_map.get(name)
            role = by_name.get(legacy_name) if legacy_name else None
            if role is not None:
                role.name = name
            else:
                role = Role(name=name, description=definition["description"])
                db.add(role)
        role.description = definition["description"]

        role.permissions = [permissions[scope] for scope in definition["scopes"]]
        role_map[name] = role

    db.flush()
    return role_map


def seed_admin_user(db: Session, roles: dict[str, Role]) -> User:
    username = os.getenv("SEED_ADMIN_USERNAME", "admin")
    password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")

    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            full_name="Administrator",
            is_active=True,
            is_superuser=True,
        )
        db.add(user)

    admin_role = roles.get(ROLE_NAME_MAP["admin"])
    if admin_role and admin_role not in user.roles:
        user.roles.append(admin_role)

    return user


def seed(db: Session) -> None:
    permissions = seed_permissions(db)
    roles = seed_roles(db, permissions)
    seed_admin_user(db, roles)
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
