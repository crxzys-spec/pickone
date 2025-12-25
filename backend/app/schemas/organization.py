from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    name: str
    code: str | None = None
    is_active: bool = True
    sort_order: int = 0


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class OrganizationOut(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
