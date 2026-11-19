from sqlalchemy.orm import Session

from core import cache
from modules.filters import repository
from modules.filters.schemas import (
    CitiesResponse,
    CityOption,
    FiltersResponse,
    FoundationYearRange,
    LegalNatureOption,
    StateOption,
)
import logging

logger = logging.getLogger(__name__)

FILTERS_CACHE_KEY = "osc:filters:v1"
FILTERS_CACHE_TTL_SECONDS = 86400


def get_filters(db: Session) -> FiltersResponse:
    """Returns the available filter options."""

    cached = cache.get(FILTERS_CACHE_KEY)
    if cached is not None:
        try:
            logger.info("Filters cache HIT")
            return FiltersResponse.model_validate_json(cached)
        except (ValueError, TypeError):
            logger.warning("Invalid filters cache. Deleting key.")
            cache.delete(FILTERS_CACHE_KEY)

    logger.info("Filters cache MISS")

    states = repository.get_states(db)
    min_year, max_year = repository.get_foundation_year_range(db)

    response = FiltersResponse(
        states=[
            StateOption(code=code, name=name)
            for code, name in states
        ],
        statuses=repository.get_statuses(db),
        legal_natures=[
            LegalNatureOption(code=code, name=name)
            for code, name in repository.get_legal_natures(db)
        ],
        activity_areas=repository.get_activity_areas(db),
        foundation_year=FoundationYearRange(
            min=min_year,
            max=max_year,
        ),
    )
    cache.set(
        FILTERS_CACHE_KEY,
        response.model_dump_json(),
        FILTERS_CACHE_TTL_SECONDS,
    )
    return response


def get_cities_by_uf(db: Session, uf: str) -> CitiesResponse:
    """Returns the cities associated with organizations in a state."""

    cities = repository.get_cities_by_uf(db, uf)

    return CitiesResponse(
        items=[
            CityOption(code=code, name=name)
            for code, name in cities
        ]
    )
