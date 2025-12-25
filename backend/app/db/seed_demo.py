from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.codes import generate_code
from app.core.security import get_password_hash
from app.db.seeds import seed as seed_core
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.draw import DrawApplication
from app.models.expert import Expert
from app.models.organization import Organization
from app.models.role import Role
from app.models.rule import Rule
from app.models.subcategory import Subcategory
from app.models.title import Title
from app.models.user import User


CATEGORY_SEEDS: list[dict[str, object]] = [
    {
        "name": "工程类",
        "code": "engineering",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "name": "服务类",
        "code": "services",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "name": "货物类",
        "code": "goods",
        "sort_order": 3,
        "is_active": True,
    },
]

SUBCATEGORY_SEEDS: list[dict[str, object]] = [
    {
        "category": "工程类",
        "name": "土建",
        "code": "civil",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "category": "工程类",
        "name": "电气",
        "code": "electrical",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "category": "服务类",
        "name": "咨询",
        "code": "consulting",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "category": "服务类",
        "name": "审计",
        "code": "audit",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "category": "货物类",
        "name": "设备",
        "code": "equipment",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "category": "货物类",
        "name": "材料",
        "code": "materials",
        "sort_order": 2,
        "is_active": True,
    },
]
RULE_SEEDS: list[dict[str, object]] = [
    {
        "name": "工程类-高级规则",
        "category": "工程类",
        "subcategory": "土建",
        "title_required": "高级",
        "avoid_enabled": True,
        "draw_method": "random",
        "is_active": True,
    },
    {
        "name": "服务类-高级摇号",
        "category": "服务类",
        "subcategory": "审计",
        "title_required": "高级",
        "avoid_enabled": True,
        "draw_method": "lottery",
        "is_active": True,
    },
    {
        "name": "货物类-默认规则",
        "category": "货物类",
        "subcategory": "设备",
        "title_required": None,
        "avoid_enabled": False,
        "draw_method": "random",
        "is_active": True,
    },
]

EXPERT_SEEDS: list[dict[str, object]] = [
    {
        "name": "张伟",
        "gender": "男",
        "phone": "1000000001",
        "email": "zhangwei@example.com",
        "company": "华建集团",
        "title": "高级",
        "category": "工程类",
        "subcategory": "土建",
        "avoid_units": "评审大厅A",
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "李娜",
        "gender": "女",
        "phone": "1000000002",
        "email": "lina@example.com",
        "company": "华建集团",
        "title": "高级",
        "category": "工程类",
        "subcategory": "电气",
        "avoid_units": None,
        "avoid_persons": "王强",
        "is_active": True,
    },
    {
        "name": "王强",
        "gender": "男",
        "phone": "1000000003",
        "email": "wangqiang@example.com",
        "company": "城投建设",
        "title": "高级",
        "category": "工程类",
        "subcategory": "土建",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "赵敏",
        "gender": "女",
        "phone": "1000000004",
        "email": "zhaomin@example.com",
        "company": "城投建设",
        "title": "高级",
        "category": "工程类",
        "subcategory": "土建",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "陈杰",
        "gender": "男",
        "phone": "1000000005",
        "email": "chenjie@example.com",
        "company": "电力设计院",
        "title": "高级",
        "category": "工程类",
        "subcategory": "电气",
        "avoid_units": "评审大厅A",
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "刘洋",
        "gender": "女",
        "phone": "1000000006",
        "email": "liuyang@example.com",
        "company": "电力设计院",
        "title": "高级",
        "category": "工程类",
        "subcategory": "电气",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "周婷",
        "gender": "女",
        "phone": "1000000007",
        "email": "zhouting@example.com",
        "company": "华建集团",
        "title": "中级",
        "category": "工程类",
        "subcategory": "土建",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "吴磊",
        "gender": "男",
        "phone": "1000000008",
        "email": "wulei@example.com",
        "company": "华建集团",
        "title": "高级",
        "category": "工程类",
        "subcategory": "土建",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "孙凯",
        "gender": "男",
        "phone": "2000000001",
        "email": "sunkai@example.com",
        "company": "中正咨询",
        "title": "高级",
        "category": "服务类",
        "subcategory": "咨询",
        "avoid_units": "评审大厅B",
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "郑爽",
        "gender": "女",
        "phone": "2000000002",
        "email": "zhengshuang@example.com",
        "company": "中正咨询",
        "title": "高级",
        "category": "服务类",
        "subcategory": "审计",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "黄蓉",
        "gender": "女",
        "phone": "2000000003",
        "email": "huangrong@example.com",
        "company": "德信咨询",
        "title": "高级",
        "category": "服务类",
        "subcategory": "咨询",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "林峰",
        "gender": "男",
        "phone": "2000000004",
        "email": "linfeng@example.com",
        "company": "德信咨询",
        "title": "高级",
        "category": "服务类",
        "subcategory": "审计",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "何丽",
        "gender": "女",
        "phone": "2000000005",
        "email": "heli@example.com",
        "company": "德信咨询",
        "title": "高级",
        "category": "服务类",
        "subcategory": "审计",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "高翔",
        "gender": "男",
        "phone": "3000000001",
        "email": "gaoxiang@example.com",
        "company": "宏达供应",
        "title": "经理",
        "category": "货物类",
        "subcategory": "设备",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "许倩",
        "gender": "女",
        "phone": "3000000002",
        "email": "xuqian@example.com",
        "company": "宏达供应",
        "title": "工程师",
        "category": "货物类",
        "subcategory": "材料",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "马超",
        "gender": "男",
        "phone": "3000000003",
        "email": "machao@example.com",
        "company": "迅达物流",
        "title": "主管",
        "category": "货物类",
        "subcategory": "设备",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "宋佳",
        "gender": "女",
        "phone": "3000000004",
        "email": "songjia@example.com",
        "company": "迅达物流",
        "title": "工程师",
        "category": "货物类",
        "subcategory": "材料",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "唐宇",
        "gender": "男",
        "phone": "3000000005",
        "email": "tangyu@example.com",
        "company": "迅达物流",
        "title": "经理",
        "category": "货物类",
        "subcategory": "设备",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "郭涛",
        "gender": "男",
        "phone": "3000000007",
        "email": "guotao@example.com",
        "company": "万通贸易",
        "title": "工程师",
        "category": "货物类",
        "subcategory": "设备",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
    {
        "name": "谢宁",
        "gender": "女",
        "phone": "3000000006",
        "email": "xiening@example.com",
        "company": "万通贸易",
        "title": "经理",
        "category": "货物类",
        "subcategory": "材料",
        "avoid_units": None,
        "avoid_persons": None,
        "is_active": True,
    },
]

USER_SEEDS: list[dict[str, object]] = [
    {
        "username": "operator1",
        "password": "operator123",
        "full_name": "业务操作员1",
        "email": "operator1@example.com",
        "roles": ["业务操作员"]
    },
    {
        "username": "ruleadmin1",
        "password": "ruleadmin123",
        "full_name": "规则管理员1",
        "email": "ruleadmin1@example.com",
        "roles": ["规则管理员"]
    },
    {
        "username": "useradmin1",
        "password": "useradmin123",
        "full_name": "用户管理员1",
        "email": "useradmin1@example.com",
        "roles": ["用户管理员"]
    },
]

def upsert_category(db: Session, payload: dict[str, object]) -> Category:
    category = (
        db.execute(select(Category).where(Category.name == payload["name"]))
        .scalar_one_or_none()
    )
    if category is None:
        category = Category(**payload)
        db.add(category)
        return category

    for key, value in payload.items():
        setattr(category, key, value)
    return category


def upsert_subcategory(db: Session, payload: dict[str, object]) -> Subcategory:
    stmt = select(Subcategory).where(
        Subcategory.category_id == payload["category_id"],
        Subcategory.name == payload["name"],
    )
    subcategory = db.execute(stmt).scalar_one_or_none()
    if subcategory is None:
        subcategory = Subcategory(**payload)
        db.add(subcategory)
        return subcategory

    for key, value in payload.items():
        setattr(subcategory, key, value)
    return subcategory


def upsert_organization(db: Session, payload: dict[str, object]) -> Organization:
    organization = (
        db.execute(select(Organization).where(Organization.name == payload["name"]))
        .scalar_one_or_none()
    )
    if organization is None:
        organization = Organization(**payload)
        db.add(organization)
        return organization

    for key, value in payload.items():
        setattr(organization, key, value)
    return organization


def upsert_title(db: Session, payload: dict[str, object]) -> Title:
    title = db.execute(select(Title).where(Title.name == payload["name"])).scalar_one_or_none()
    if title is None:
        title = Title(**payload)
        db.add(title)
        return title

    for key, value in payload.items():
        setattr(title, key, value)
    return title


def upsert_rule(db: Session, payload: dict[str, object]) -> Rule:
    rule = db.execute(select(Rule).where(Rule.name == payload["name"])).scalar_one_or_none()
    if rule is None:
        rule = Rule(**payload)
        db.add(rule)
        return rule

    for key, value in payload.items():
        setattr(rule, key, value)
    return rule


def upsert_expert(db: Session, payload: dict[str, object]) -> Expert:
    stmt = select(Expert).where(
        Expert.name == payload["name"], Expert.phone == payload["phone"]
    )
    expert = db.execute(stmt).scalars().first()
    if expert is None:
        expert = Expert(**payload)
        db.add(expert)
        return expert

    for key, value in payload.items():
        setattr(expert, key, value)
    return expert


def ensure_user(db: Session, payload: dict[str, object], role_map: dict[str, Role]) -> User:
    username = str(payload["username"])
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        user = User(
            username=username,
            hashed_password=get_password_hash(str(payload["password"])),
            full_name=str(payload["full_name"]),
            email=str(payload["email"]),
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
    else:
        user.full_name = str(payload["full_name"])
        user.email = str(payload["email"])
        user.is_active = True

    for role_name in payload.get("roles", []):
        role = role_map.get(str(role_name))
        if role and role not in user.roles:
            user.roles.append(role)
    return user


def ensure_draw(
    db: Session,
    payload: dict[str, object],
    rule_map: dict[str, Rule],
    user_map: dict[str, User],
) -> DrawApplication:
    stmt = select(DrawApplication).where(
        DrawApplication.review_location == payload["review_location"]
    )
    if payload.get("category_id") is not None:
        stmt = stmt.where(DrawApplication.category_id == payload["category_id"])
    else:
        stmt = stmt.where(DrawApplication.category == payload["category"])
    draw = db.execute(stmt).scalar_one_or_none()
    rule_name = payload.get("rule_name")
    rule = rule_map.get(str(rule_name)) if rule_name else None
    created_by = user_map.get(str(payload.get("created_by"))) if payload.get("created_by") else None
    if draw is None:
        draw = DrawApplication(
            category_id=payload.get("category_id"),
            category=str(payload["category"]),
            subcategory_id=payload.get("subcategory_id"),
            subcategory=payload.get("subcategory"),
            expert_count=int(payload["expert_count"]),
            backup_count=int(payload.get("backup_count") or 0),
            draw_method=str(payload["draw_method"]),
            review_time=payload.get("review_time"),
            review_location=str(payload["review_location"]),
            status=str(payload["status"]),
            rule_id=rule.id if rule else None,
            created_by_id=created_by.id if created_by else None,
        )
        db.add(draw)
        return draw

    draw.category_id = payload.get("category_id")
    draw.category = str(payload["category"])
    draw.subcategory = payload.get("subcategory")
    draw.subcategory_id = payload.get("subcategory_id")
    draw.expert_count = int(payload["expert_count"])
    draw.backup_count = int(payload.get("backup_count") or 0)
    draw.draw_method = str(payload["draw_method"])
    draw.review_time = payload.get("review_time")
    draw.status = str(payload["status"])
    draw.rule_id = rule.id if rule else None
    draw.created_by_id = created_by.id if created_by else None
    return draw


def seed_demo(db: Session) -> None:
    seed_core(db)

    roles = db.execute(select(Role)).scalars().all()
    role_map = {role.name: role for role in roles}

    for payload in USER_SEEDS:
        ensure_user(db, payload, role_map)

    categories: dict[str, Category] = {}
    for payload in CATEGORY_SEEDS:
        category = upsert_category(db, payload)
        categories[category.name] = category
    db.flush()

    subcategories: dict[tuple[str, str], Subcategory] = {}
    for payload in SUBCATEGORY_SEEDS:
        category = categories.get(str(payload["category"]))
        if category is None:
            continue
        if category.id is None:
            db.flush()
        sub_payload = {
            "category_id": category.id,
            "name": payload["name"],
            "code": payload.get("code"),
            "sort_order": payload.get("sort_order", 0),
            "is_active": payload.get("is_active", True),
        }
        subcategory = upsert_subcategory(db, sub_payload)
        subcategories[(category.name, subcategory.name)] = subcategory
    db.flush()

    organizations: dict[str, Organization] = {}
    titles: dict[str, Title] = {}
    for payload in EXPERT_SEEDS:
        org_name = str(payload.get("company") or "").strip()
        if org_name and org_name not in organizations:
            organization = upsert_organization(
                db,
                {
                    "name": org_name,
                    "code": generate_code(prefix="org"),
                    "sort_order": 0,
                    "is_active": True,
                },
            )
            organizations[organization.name] = organization

        title_name = str(payload.get("title") or "").strip()
        if title_name and title_name not in titles:
            title = upsert_title(
                db,
                {
                    "name": title_name,
                    "code": generate_code(prefix="title"),
                    "sort_order": 0,
                    "is_active": True,
                },
            )
            titles[title.name] = title
    db.flush()

    rules = {}
    for payload in RULE_SEEDS:
        data = payload.copy()
        category = categories.get(str(data["category"]))
        if category:
            data["category_id"] = category.id
            data["category"] = category.name
        subcategory_name = data.get("subcategory")
        if category and subcategory_name:
            subcategory = subcategories.get((category.name, str(subcategory_name)))
            if subcategory:
                data["subcategory_id"] = subcategory.id
                data["subcategory"] = subcategory.name
        rule = upsert_rule(db, data)
        rules[rule.name] = rule

    for payload in EXPERT_SEEDS:
        data = payload.copy()
        category = categories.get(str(data.get("category")))
        if category:
            data["category_id"] = category.id
            data["category"] = category.name
        subcategory_name = data.get("subcategory")
        if category and subcategory_name:
            subcategory = subcategories.get((category.name, str(subcategory_name)))
            if subcategory:
                data["subcategory_id"] = subcategory.id
                data["subcategory"] = subcategory.name
        organization = organizations.get(str(data.get("company")))
        if organization:
            data["organization_id"] = organization.id
            data["company"] = organization.name
        title = titles.get(str(data.get("title")))
        if title:
            data["title_id"] = title.id
            data["title"] = title.name
        upsert_expert(db, data)

    base_time = datetime.now(timezone.utc) + timedelta(days=2)
    draw_seeds = [
        {
            "category": "工程类",
            "subcategory": "土建",
            "expert_count": 3,
            "backup_count": 1,
            "draw_method": "random",
            "review_time": base_time,
            "review_location": "评审大厅A",
            "status": "pending",
            "rule_name": "工程类-高级规则",
            "created_by": "operator1",
        },
        {
            "category": "服务类",
            "subcategory": "审计",
            "expert_count": 2,
            "backup_count": 2,
            "draw_method": "lottery",
            "review_time": base_time + timedelta(days=1),
            "review_location": "评审大厅B",
            "status": "pending",
            "rule_name": "服务类-高级摇号",
            "created_by": "operator1",
        },
        {
            "category": "货物类",
            "subcategory": "设备",
            "expert_count": 3,
            "backup_count": 1,
            "draw_method": "random",
            "review_time": base_time + timedelta(days=2),
            "review_location": "评审大厅C",
            "status": "pending",
            "rule_name": "货物类-默认规则",
            "created_by": "operator1",
        },
    ]

    users = db.execute(select(User)).scalars().all()
    user_map = {user.username: user for user in users}
    for payload in draw_seeds:
        data = payload.copy()
        category = categories.get(str(data.get("category")))
        if category:
            data["category_id"] = category.id
            data["category"] = category.name
        subcategory_name = data.get("subcategory")
        if category and subcategory_name:
            subcategory = subcategories.get((category.name, str(subcategory_name)))
            if subcategory:
                data["subcategory_id"] = subcategory.id
                data["subcategory"] = subcategory.name
        ensure_draw(db, data, rules, user_map)

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_demo(db)
    print("Seed demo data completed.")


if __name__ == "__main__":
    main()
