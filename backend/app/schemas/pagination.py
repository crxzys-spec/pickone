from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")
SortOrder = Literal["asc", "desc"]


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
    sort_by: str | None = None
    sort_order: SortOrder = "asc"
    keyword: str | None = None


class Page(BaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
