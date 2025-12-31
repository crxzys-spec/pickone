from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TitleBase(BaseModel):
    parent_id: int | None = None
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class TitleCreate(TitleBase):
    code: str | None = Field(default=None, min_length=1)


class TitleUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    code: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None
    sort_order: int | None = None


class TitleOut(TitleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TitleTreeOut(TitleOut):
    children: list[TitleTreeOut] = Field(default_factory=list)


class TitleBatchItem(BaseModel):
    id: int


class TitleBatchAction(BaseModel):
    action: Literal["enable", "disable", "delete"]
    items: list[TitleBatchItem] = Field(default_factory=list)


class TitleBatchError(BaseModel):
    id: int
    detail: str


class TitleBatchResult(BaseModel):
    updated: int = 0
    deleted: int = 0
    skipped: int = 0
    errors: list[TitleBatchError] = Field(default_factory=list)
