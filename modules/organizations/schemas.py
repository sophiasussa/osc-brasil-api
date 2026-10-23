
from datetime import date

from pydantic import BaseModel, ConfigDict


class ActivityAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ActivitySubareaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    area_id: int | None
    name: str


class CnaeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str | None


class OrganizationCnaeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cnae_code: str
    is_primary: bool
    cnae: CnaeResponse


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cnpj: str | None
    legal_name: str
    trade_name: str | None
    legal_nature_code: int | None
    matrix_or_branch: str | None
    registration_status: str | None
    removed_from_mosc: bool | None
    foundation_date: date | None
    closing_date: date | None
    closing_year: int | None
    address: str | None
    municipality_code: int | None
    latitude: float | None
    longitude: float | None
    areas: list[ActivityAreaResponse]
    subareas: list[ActivitySubareaResponse]
    cnaes: list[OrganizationCnaeResponse]


class OrganizationListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cnpj: str | None
    city: str | None
    state: str | None
    status: str | None
    legal_nature: str | None
    foundation_year: int | None
    activity_areas: list[str]


class OrganizationListResponse(BaseModel):
    items: list[OrganizationListItemResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
