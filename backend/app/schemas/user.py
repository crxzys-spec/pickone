from pydantic import BaseModel, ConfigDict, Field

from app.schemas.role import RoleSummary


class UserBase(BaseModel):
    username: str
    full_name: str | None = None
    email: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    password: str | None = None


class UserSelfUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None


class UserPasswordChange(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)


class UserRolesUpdate(BaseModel):
    role_ids: list[int] = Field(default_factory=list)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    roles: list[RoleSummary] = Field(default_factory=list)
