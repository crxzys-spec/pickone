from pydantic import BaseModel, ConfigDict


class RuleBase(BaseModel):
    name: str
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    title_required: str | None = None
    avoid_enabled: bool = True
    draw_method: str = "random"
    is_active: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    title_required: str | None = None
    avoid_enabled: bool | None = None
    draw_method: str | None = None
    is_active: bool | None = None


class RuleOut(RuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
