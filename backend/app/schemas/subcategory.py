from pydantic import BaseModel, ConfigDict, Field

from app.schemas.specialty import SpecialtyOut


class SubcategoryBase(BaseModel):
    category_id: int
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class SubcategoryCreate(BaseModel):
    name: str
    code: str = Field(min_length=1)
    is_active: bool = True
    sort_order: int = 0


class SubcategoryUpdate(BaseModel):
    name: str | None = None
    code: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None
    sort_order: int | None = None


class SubcategoryOut(SubcategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    specialties: list[SpecialtyOut] = Field(default_factory=list)
