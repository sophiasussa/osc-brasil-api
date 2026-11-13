from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.analytics.schemas import AnalyticsResponse
from modules.analytics.service import get_analytics as get_analytics_service


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    db: Annotated[Session, Depends(get_db)],
    state: Annotated[str | None, Query()] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    activity_area: Annotated[
        str | None,
        Query(alias="activityArea"),
    ] = None,
    legal_nature: Annotated[int | None, Query(alias="legalNature")] = None,
    founded_from: Annotated[
        int | None,
        Query(ge=1, le=9999, alias="foundedFrom"),
    ] = None,
    founded_to: Annotated[
        int | None,
        Query(ge=1, le=9999, alias="foundedTo"),
    ] = None,
) -> AnalyticsResponse:
    if (
        founded_from is not None
        and founded_to is not None
        and founded_from > founded_to
    ):
        raise HTTPException(
            status_code=422,
            detail="foundedFrom must be less than or equal to foundedTo.",
        )

    return get_analytics_service(
        db,
        state=state,
        status=status_filter,
        activity_area=activity_area,
        legal_nature=legal_nature,
        founded_from=founded_from,
        founded_to=founded_to,
    )