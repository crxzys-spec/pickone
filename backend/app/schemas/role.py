from pydantic import BaseModel, ConfigDict, Field

from app.schemas.permission import PermissionOut


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RolePermissionsUpdate(BaseModel):
    permission_ids: list[int] = Field(default_factory=list)


class RoleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    permissions: list[PermissionOut] = Field(default_factory=list)
