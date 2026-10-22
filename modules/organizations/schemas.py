from datetime import date

from pydantic import BaseModel, ConfigDict


class ActivityAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ActivitySubareaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    area_id: int
    name: str


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cnpj: str
    legal_name: str | None
    trade_name: str | None
    legal_nature_code: int | None
    matrix_or_branch: str | None
    registration_status: str
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
