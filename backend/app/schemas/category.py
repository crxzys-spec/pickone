from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.subcategory import SubcategoryOut


class CategoryBase(BaseModel):
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    code: str = Field(min_length=1)


class CategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryTreeOut(CategoryOut):
    subcategories: list[SubcategoryOut] = Field(default_factory=list)


class CategoryBatchItem(BaseModel):
    id: int
    type: Literal["category", "subcategory", "specialty"]


class CategoryBatchAction(BaseModel):
    action: Literal["enable", "disable", "delete"]
    items: list[CategoryBatchItem] = Field(default_factory=list)


class CategoryBatchError(BaseModel):
    id: int
    type: Literal["category", "subcategory", "specialty"]
    detail: str


class CategoryBatchResult(BaseModel):
    updated: int = 0
    deleted: int = 0
    skipped: int = 0
    errors: list[CategoryBatchError] = Field(default_factory=list)
