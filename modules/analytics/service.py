from sqlalchemy.orm import Session

from modules.analytics.repository import AnalyticsRepository
from modules.analytics.schemas import AnalyticsResponse


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
    repository = AnalyticsRepository(db)
    return AnalyticsResponse.model_validate(
        repository.get_analytics(
            state=state,
            status=status,
            activity_area=activity_area,
            legal_nature=legal_nature,
            founded_from=founded_from,
            founded_to=founded_to,
        )
    )