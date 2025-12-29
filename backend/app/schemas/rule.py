from pydantic import BaseModel, ConfigDict


class RuleBase(BaseModel):
    name: str
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    specialty_id: int | None = None
    specialty: str | None = None
    specialty_ids: list[int] | None = None
    title_required: str | None = None
    title_required_ids: list[int] | None = None
    region_required_id: int | None = None
    region_required: str | None = None
    region_required_ids: list[int] | None = None
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
    specialty_id: int | None = None
    specialty: str | None = None
    specialty_ids: list[int] | None = None
    title_required: str | None = None
    title_required_ids: list[int] | None = None
    region_required_id: int | None = None
    region_required: str | None = None
    region_required_ids: list[int] | None = None
    draw_method: str | None = None
    is_active: bool | None = None


class RuleOut(RuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
