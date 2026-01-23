from pydantic import BaseModel, Field

from app.schemas.category import CategoryTreeOut
from app.schemas.expert import ExpertAuditStatus
from app.schemas.organization import OrganizationOut
from app.schemas.region import RegionOut
from app.schemas.title import TitleTreeOut


class ExpertPublicMetadata(BaseModel):
    organizations: list[OrganizationOut] = Field(default_factory=list)
    regions: list[RegionOut] = Field(default_factory=list)
    titles: list[TitleTreeOut] = Field(default_factory=list)
    specialties: list[CategoryTreeOut] = Field(default_factory=list)


class ExpertPublicSubmitOut(BaseModel):
    id: int
    audit_status: ExpertAuditStatus
