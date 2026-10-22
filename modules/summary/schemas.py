
from pydantic import BaseModel, ConfigDict


class SummaryResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: (
            field_name.split("_")[0]
            + "".join(
                part.capitalize()
                for part in field_name.split("_")[1:]
            )
        ),
        populate_by_name=True,
    )

    organization_records: int
    active_organizations: int
    states: int
    cities: int
    activity_areas: int
