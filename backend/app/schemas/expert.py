from pydantic import BaseModel, ConfigDict


class ExpertBase(BaseModel):
    name: str
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None
    organization_id: int | None = None
    title: str | None = None
    title_id: int | None = None
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    avoid_units: str | None = None
    avoid_persons: str | None = None
    is_active: bool = True


class ExpertCreate(ExpertBase):
    pass


class ExpertUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None
    organization_id: int | None = None
    title: str | None = None
    title_id: int | None = None
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    avoid_units: str | None = None
    avoid_persons: str | None = None
    is_active: bool | None = None


class ExpertOut(ExpertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
