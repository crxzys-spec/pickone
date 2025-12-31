import json
import os
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.expert import Expert
from app.models.permission import Permission
from app.models.region import Region
from app.models.role import Role
from app.models.rule import Rule
from app.models.specialty import Specialty
from app.models.title import Title
from app.models.user import User
from app.repo.specialties import SpecialtyRepo
from app.repo.titles import TitleRepo
from app.services import experts as expert_service

SCOPE_DEFINITIONS = {
    "expert:read": {"name": "专家查看", "description": "查看专家信息"},
    "expert:write": {"name": "专家维护", "description": "新增或修改专家信息"},
    "rule:read": {"name": "规则查看", "description": "查看抽取规则"},
    "rule:write": {"name": "规则维护", "description": "新增或修改抽取规则"},
    "category:read": {"name": "专业目录查看", "description": "查看专业目录"},
    "category:write": {"name": "专业目录管理", "description": "管理专业目录"},
    "organization:read": {"name": "单位查看", "description": "查看单位枚举"},
    "organization:write": {"name": "单位管理", "description": "管理单位枚举"},
    "region:read": {"name": "地域查看", "description": "查看地域枚举"},
    "region:write": {"name": "地域管理", "description": "管理地域枚举"},
    "title:read": {"name": "职称查看", "description": "查看职称枚举"},
    "title:write": {"name": "职称管理", "description": "管理职称枚举"},
    "draw:read": {"name": "抽取查看", "description": "查看抽取申请与结果"},
    "draw:apply": {"name": "抽取申请", "description": "发起专家抽取申请"},
    "draw:execute": {"name": "抽取执行", "description": "执行专家抽取"},
    "user:read": {"name": "用户查看", "description": "查看用户信息"},
    "user:write": {"name": "用户管理", "description": "新增或修改用户信息"},
    "role:write": {"name": "角色管理", "description": "管理角色与权限"},
}

DEPRECATED_SCOPES = {
    "expert:approve",
    "subcategory:read",
    "subcategory:write",
    "specialty:read",
    "specialty:write",
}

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
            "organization:read",
            "region:read",
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
            "region:read",
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
    seed_titles_from_json(db)
    seed_specialties_from_json(db)
    seed_regions_from_json(db)
    seed_experts(db)
    db.commit()


def _load_json_payload(source: Path) -> dict:
    raw = source.read_bytes()
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return json.loads(raw.decode(encoding))
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    return {}


def _normalize_name(code: str | None, name: str | None) -> str:
    raw = (name or "").strip()
    if not raw:
        return code or ""
    if code and raw.startswith(code):
        trimmed = raw[len(code) :].strip()
        return trimmed or raw
    return raw


def seed_specialties_from_json(db: Session) -> None:
    root = Path(__file__).resolve().parents[3]
    source = root / "docs" / "新专业表.json"
    if not source.exists():
        legacy = root / "docs" / "专业树状表格.json"
        if legacy.exists():
            source = legacy
        else:
            return

    payload = _load_json_payload(source)
    nodes = payload.get("result") or []
    repo = SpecialtyRepo(db)
    existing = {item.code: item for item in repo.list() if item.code}

    def extract_code(item: dict) -> str:
        raw = (
            item.get("specialCode")
            or item.get("bidAreaId")
            or item.get("code")
            or item.get("id")
            or ""
        )
        return str(raw).strip()

    def extract_name(item: dict, code: str) -> str:
        raw = (
            item.get("specialName")
            or item.get("bidAreaName")
            or item.get("name")
            or ""
        )
        return _normalize_name(code, str(raw))

    def extract_children(item: dict) -> list[dict]:
        children = item.get("children")
        if children is None:
            children = item.get("childs")
        if isinstance(children, list):
            return children
        return []

    def walk(items: list[dict], parent_id: int | None) -> None:
        for index, item in enumerate(items, start=1):
            code = extract_code(item)
            if not code:
                code = generate_code(prefix="spec")
            name = extract_name(item, code) or code
            specialty = existing.get(code)
            if specialty is None:
                specialty = Specialty(
                    parent_id=parent_id,
                    name=name,
                    code=code,
                    is_active=True,
                    sort_order=index,
                )
                db.add(specialty)
                db.flush()
                existing[code] = specialty
            else:
                specialty.parent_id = parent_id
                specialty.name = name or code
                specialty.sort_order = index
                specialty.is_active = True

            children = extract_children(item)
            if children:
                walk(children, specialty.id)

    if isinstance(nodes, list) and nodes:
        walk(nodes, None)


def seed_titles_from_json(db: Session) -> None:
    root = Path(__file__).resolve().parents[3]
    source = root / "docs" / "职称分类.json"
    if not source.exists():
        return

    existing_title_ids = db.execute(select(Title.id)).scalars().all()
    if existing_title_ids:
        db.execute(
            Expert.__table__.update().values(title_id=None, title=None)
        )
        db.execute(
            Rule.__table__.update().values(
                title_required_ids=None, title_required=None
            )
        )
        db.execute(delete(Title))
        db.commit()

    payload = _load_json_payload(source)
    nodes = payload.get("result") or []
    repo = TitleRepo(db)
    existing = {item.code: item for item in repo.list() if item.code}

    def walk(items: list[dict], parent_id: int | None) -> None:
        for index, item in enumerate(items, start=1):
            code = str(item.get("jobtitleId") or item.get("code") or "").strip()
            if not code:
                code = generate_code(prefix="title")
            name = _normalize_name(code, str(item.get("jobtitleName") or item.get("name") or code))
            disabled = item.get("disabled")
            is_active = not bool(disabled) if disabled is not None else True
            order_value = item.get("order")
            try:
                sort_order = int(order_value) if order_value is not None else index
            except (TypeError, ValueError):
                sort_order = index

            title = existing.get(code)
            if title is None:
                title = Title(
                    parent_id=parent_id,
                    name=name or code,
                    code=code,
                    is_active=is_active,
                    sort_order=sort_order,
                )
                db.add(title)
                db.flush()
                existing[code] = title
            else:
                title.parent_id = parent_id
                title.name = name or code
                title.is_active = is_active
                title.sort_order = sort_order

            children = item.get("childs") or []
            if isinstance(children, list) and children:
                walk(children, title.id)

    if isinstance(nodes, list) and nodes:
        walk(nodes, None)


def seed_regions_from_json(db: Session) -> None:
    root = Path(__file__).resolve().parents[3]
    source = root / "docs" / "专家级别划分.json"
    if not source.exists():
        return

    existing_ids = db.execute(select(Region.id)).scalars().all()
    if existing_ids:
        db.execute(
            Expert.__table__.update().values(region_id=None, region=None)
        )
        db.execute(
            Rule.__table__.update().values(
                region_required_id=None,
                region_required=None,
                region_required_ids=None,
            )
        )
        db.execute(delete(Region))
        db.commit()

    payload = _load_json_payload(source)
    nodes = payload.get("result") or []
    if not isinstance(nodes, list):
        return

    seen_codes: set[str] = set()
    seen_names: set[str] = set()
    for index, item in enumerate(nodes, start=1):
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "").strip()
        raw_name = item.get("desc") or item.get("districtName") or item.get("name") or ""
        name = _normalize_name(code, str(raw_name))
        if not name and not code:
            continue
        if code and code in seen_codes:
            continue
        if name and name in seen_names and not code:
            continue

        region = Region(
            name=name or code,
            code=code or None,
            is_active=True,
            sort_order=index,
        )
        db.add(region)
        if code:
            seen_codes.add(code)
        if name:
            seen_names.add(name)

    db.flush()


def seed_experts(db: Session) -> None:
    root = Path(__file__).resolve().parents[3]
    source = root / "docs" / "专家导入表.xlsx"
    if not source.exists():
        return

    class _SeedFile:
        def __init__(self, file_obj):
            self.file = file_obj

    with source.open("rb") as file_obj:
        expert_service.import_experts(db, _SeedFile(file_obj))


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
