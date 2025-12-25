from pydantic import BaseModel, ConfigDict


class SubcategoryBase(BaseModel):
    category_id: int
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class SubcategoryCreate(BaseModel):
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class SubcategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class SubcategoryOut(SubcategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
