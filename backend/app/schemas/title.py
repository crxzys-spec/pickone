from pydantic import BaseModel, ConfigDict, Field


class TitleBase(BaseModel):
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class TitleCreate(TitleBase):
    pass


class TitleUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class TitleOut(TitleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TitleBatchDelete(BaseModel):
    ids: list[int] = Field(default_factory=list, min_length=1)
