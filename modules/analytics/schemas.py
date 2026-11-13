from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from modules.organizations.schemas import CompletenessResponse


class AnalyticsSummary(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    organizations: int
    states: int
    activity_areas: int


class StateCount(BaseModel):
    state: str
    count: int


class NamedCount(BaseModel):
    name: str
    count: int


class FoundationYearCount(BaseModel):
    year: int
    count: int


class AnalyticsResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    summary: AnalyticsSummary
    by_state: list[StateCount]
    by_activity_area: list[NamedCount]
    by_foundation_year: list[FoundationYearCount]
    by_legal_nature: list[NamedCount]
    completeness: CompletenessResponse