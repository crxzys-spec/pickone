from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.schemas.specialty import SpecialtyOut


class DrawApply(BaseModel):
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    specialty_id: int | None = None
    specialty: str | None = None
    project_name: str | None = None
    project_code: str | None = None
    expert_count: int
    total_count: int | None = None
    backup_count: int = 0
    draw_method: str = "random"
    review_time: datetime | None = None
    review_location: str | None = None
    avoid_units: str | None = None
    avoid_persons: str | None = None
    rule_id: int | None = None


class DrawOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None = None
    category: str
    subcategory_id: int | None = None
    subcategory: str | None = None
    specialty_id: int | None = None
    specialty: str | None = None
    project_name: str | None = None
    project_code: str | None = None
    expert_count: int
    total_count: int
    backup_count: int
    draw_method: str
    review_time: datetime | None = None
    review_location: str | None = None
    avoid_units: str | None = None
    avoid_persons: str | None = None
    status: str
    rule_id: int | None = None


class DrawUpdate(BaseModel):
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    specialty_id: int | None = None
    specialty: str | None = None
    project_name: str | None = None
    project_code: str | None = None
    expert_count: int | None = None
    total_count: int | None = None
    backup_count: int | None = None
    draw_method: str | None = None
    review_time: datetime | None = None
    review_location: str | None = None
    avoid_units: str | None = None
    avoid_persons: str | None = None
    status: str | None = None
    rule_id: int | None = None


class DrawReplace(BaseModel):
    result_id: int


class DrawBatchDelete(BaseModel):
    ids: list[int] = Field(default_factory=list, min_length=1)


class DrawResultExpert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    company: str | None = None
    phone: str | None = None
    title: str | None = None
    specialties: list[SpecialtyOut] = Field(default_factory=list)
    specialty_ids: list[int] = Field(default_factory=list)

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


class DrawResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    draw_id: int
    expert_id: int
    is_backup: bool
    is_replacement: bool = False
    contact_status: str | None = None
    ordinal: int | None = None
    expert: DrawResultExpert | None = None


class DrawExecuteResult(BaseModel):
    results: list[DrawResultOut] = Field(default_factory=list)


class DrawResultContactOut(BaseModel):
    name: str
    phone: str | None = None


class DrawResultContactUpdate(BaseModel):
    status: str
    auto_replace: bool = False
