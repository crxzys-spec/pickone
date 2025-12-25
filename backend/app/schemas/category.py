from pydantic import BaseModel, ConfigDict, Field

from app.schemas.subcategory import SubcategoryOut


class CategoryBase(BaseModel):
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryTreeOut(CategoryOut):
    subcategories: list[SubcategoryOut] = Field(default_factory=list)
