from pydantic import BaseModel, ConfigDict, Field


class RegionBase(BaseModel):
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class RegionOut(RegionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RegionBatchDelete(BaseModel):
    ids: list[int] = Field(default_factory=list, min_length=1)
