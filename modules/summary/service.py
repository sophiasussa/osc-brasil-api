import logging

from sqlalchemy.orm import Session

from core import cache
from modules.summary import repository
from modules.summary.schemas import SummaryResponse


logger = logging.getLogger(__name__)

SUMMARY_CACHE_KEY = "osc:summary:v1"
SUMMARY_CACHE_TTL_SECONDS = 86400


def get_summary(db: Session) -> SummaryResponse:
    cached = cache.get(SUMMARY_CACHE_KEY)
    if cached is not None:
        try:
            response = SummaryResponse.model_validate_json(cached)
            logger.info("Summary cache HIT")
            return response
        except (ValueError, TypeError):
            logger.warning("Invalid summary cache. Deleting key.")
            cache.delete(SUMMARY_CACHE_KEY)

    logger.info("Summary cache MISS")

    response = SummaryResponse(
        organization_records=repository.get_organization_records(db),
        active_organizations=repository.get_active_organizations(db),
        states=repository.get_states(db),
        cities=repository.get_cities(db),
        activity_areas=repository.get_activity_areas(db),
    )
    cache.set(
        SUMMARY_CACHE_KEY,
        response.model_dump_json(),
        SUMMARY_CACHE_TTL_SECONDS,
    )
    return response
