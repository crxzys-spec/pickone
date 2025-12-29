from pydantic import BaseModel, ConfigDict, Field


class SpecialtyBase(BaseModel):
    subcategory_id: int
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class SpecialtyCreate(BaseModel):
    name: str
    code: str = Field(min_length=1)
    is_active: bool = True
    sort_order: int = 0


class SpecialtyUpdate(BaseModel):
    name: str | None = None
    code: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None
    sort_order: int | None = None


class SpecialtyOut(SpecialtyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
