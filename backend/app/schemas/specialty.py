from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SpecialtyBase(BaseModel):
    parent_id: int | None = None
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class SpecialtyCreate(SpecialtyBase):
    code: str | None = Field(default=None, min_length=1)


class SpecialtyUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    code: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None
    sort_order: int | None = None


class SpecialtyOut(SpecialtyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SpecialtyTreeOut(SpecialtyOut):
    children: list[SpecialtyTreeOut] = Field(default_factory=list)
