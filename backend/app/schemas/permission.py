from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    name: str
    scope: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: str | None = None
    scope: str | None = None
    description: str | None = None


class PermissionOut(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
