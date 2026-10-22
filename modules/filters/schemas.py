
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StateOption(BaseModel):
    code: str
    name: str


class FoundationYearRange(BaseModel):
    min: int | None
    max: int | None


class FiltersResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    states: list[StateOption]
    statuses: list[str]
    legal_natures: list[str]
    activity_areas: list[str]
    foundation_year: FoundationYearRange


class CityOption(BaseModel):
    code: int
    name: str


class CitiesResponse(BaseModel):
    items: list[CityOption]
