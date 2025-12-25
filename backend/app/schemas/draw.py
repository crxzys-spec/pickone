from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DrawApply(BaseModel):
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    expert_count: int
    backup_count: int = 0
    draw_method: str = "random"
    review_time: datetime | None = None
    review_location: str | None = None
    rule_id: int | None = None


class DrawOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None = None
    category: str
    subcategory_id: int | None = None
    subcategory: str | None = None
    expert_count: int
    backup_count: int
    draw_method: str
    review_time: datetime | None = None
    review_location: str | None = None
    status: str
    rule_id: int | None = None


class DrawUpdate(BaseModel):
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    expert_count: int | None = None
    backup_count: int | None = None
    draw_method: str | None = None
    review_time: datetime | None = None
    review_location: str | None = None
    status: str | None = None
    rule_id: int | None = None


class DrawReplace(BaseModel):
    result_id: int


class DrawResultExpert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    company: str | None = None
    category_id: int | None = None
    category: str | None = None
    subcategory_id: int | None = None
    subcategory: str | None = None
    phone: str | None = None
    email: str | None = None
    title: str | None = None


class DrawResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    draw_id: int
    expert_id: int
    is_backup: bool
    is_replacement: bool = False
    ordinal: int | None = None
    expert: DrawResultExpert | None = None


class DrawExecuteResult(BaseModel):
    results: list[DrawResultOut] = Field(default_factory=list)
