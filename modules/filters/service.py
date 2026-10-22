from sqlalchemy.orm import Session

from modules.filters import repository
from modules.filters.schemas import (
    CitiesResponse,
    CityOption,
    FiltersResponse,
    FoundationYearRange,
    StateOption,
)


def get_filters(db: Session) -> FiltersResponse:
    """Returns the available filter options."""

    states = repository.get_states(db)
    min_year, max_year = repository.get_foundation_year_range(db)

    return FiltersResponse(
        states=[
            StateOption(code=code, name=name)
            for code, name in states
        ],
        statuses=repository.get_statuses(db),
        legal_natures=repository.get_legal_natures(db),
        activity_areas=repository.get_activity_areas(db),
        foundation_year=FoundationYearRange(
            min=min_year,
            max=max_year,
        ),
    )


def get_cities_by_uf(db: Session, uf: str) -> CitiesResponse:
    """Returns the cities associated with organizations in a state."""

    cities = repository.get_cities_by_uf(db, uf)

    return CitiesResponse(
        items=[
            CityOption(code=code, name=name)
            for code, name in cities
        ]
    )
