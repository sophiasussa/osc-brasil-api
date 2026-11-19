from sqlalchemy.orm import Session

from core import cache
from modules.analytics.repository import AnalyticsRepository
from modules.analytics.schemas import AnalyticsResponse

import logging

logger = logging.getLogger(__name__)


ANALYTICS_CACHE_KEY = "osc:analytics:v1"
ANALYTICS_CACHE_TTL_SECONDS = 86400


def get_analytics(
    db: Session,
    *,
    state: str | None = None,
    status: str | None = None,
    activity_area: str | None = None,
    legal_nature: int | None = None,
    founded_from: int | None = None,
    founded_to: int | None = None,
) -> AnalyticsResponse:
    filters = (
        state,
        status,
        activity_area,
        legal_nature,
        founded_from,
        founded_to,
    )
    cache_unfiltered_response = all(value is None for value in filters)

    if cache_unfiltered_response:
        cached = cache.get(ANALYTICS_CACHE_KEY)
        if cached is not None:
            try:
                logger.info("Analytics cache HIT")
                return AnalyticsResponse.model_validate_json(cached)
            except (ValueError, TypeError):
                logger.warning("Invalid analytics cache. Deleting key.")
                cache.delete(ANALYTICS_CACHE_KEY)

    repository = AnalyticsRepository(db)
    response = AnalyticsResponse.model_validate(
        repository.get_analytics(
            state=state,
            status=status,
            activity_area=activity_area,
            legal_nature=legal_nature,
            founded_from=founded_from,
            founded_to=founded_to,
        )
    )

    if cache_unfiltered_response:
        cache.set(
            ANALYTICS_CACHE_KEY,
            response.model_dump_json(),
            ANALYTICS_CACHE_TTL_SECONDS,
        )

    return response
