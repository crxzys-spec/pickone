from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.schemas.specialty import SpecialtyOut


class ExpertBase(BaseModel):
    name: str
    id_card_no: str
    gender: str | None = None
    phone: str | None = None
    company: str | None = None
    organization_id: int | None = None
    region_id: int | None = None
    region: str | None = None
    title: str | None = None
    title_id: int | None = None
    is_active: bool = True


class ExpertCreate(ExpertBase):
    specialty_ids: list[int] = Field(default_factory=list)
    appointment_letter_urls: list[str] = Field(default_factory=list)


class ExpertUpdate(BaseModel):
    name: str | None = None
    id_card_no: str | None = Field(default=None, min_length=1)
    gender: str | None = None
    phone: str | None = None
    company: str | None = None
    organization_id: int | None = None
    region_id: int | None = None
    region: str | None = None
    title: str | None = None
    title_id: int | None = None
    is_active: bool | None = None
    specialty_ids: list[int] | None = None
    appointment_letter_urls: list[str] | None = None


class ExpertOut(ExpertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    specialties: list[SpecialtyOut] = Field(default_factory=list)
    specialty_ids: list[int] = Field(default_factory=list)
    appointment_letter_urls: list[str] = Field(default_factory=list)

    @field_serializer("name")
    def _mask_name(self, value: str | None) -> str | None:
        if not value:
            return None
        raw = value.strip()
        if not raw:
            return None
        if len(raw) == 1:
            return raw
        if len(raw) == 2:
            return f"{raw[0]}*"
        return f"{raw[0]}{'*' * (len(raw) - 2)}{raw[-1]}"

    @field_serializer("id_card_no")
    def _mask_id_card(self, value: str | None) -> str | None:
        if not value:
            return None
        raw = value.strip()
        if not raw:
            return None
        if len(raw) <= 7:
            return raw
        return f"{raw[:3]}{'*' * (len(raw) - 7)}{raw[-4:]}"

    @field_serializer("phone")
    def _mask_phone(self, value: str | None) -> str | None:
        if not value:
            return None
        raw = value.strip()
        if not raw:
            return None
        if len(raw) <= 7:
            return raw
        return f"{raw[:3]}{'*' * (len(raw) - 7)}{raw[-4:]}"


class ExpertBatchDelete(BaseModel):
    ids: list[int] = Field(default_factory=list, min_length=1)
