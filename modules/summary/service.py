from sqlalchemy.orm import Session

from modules.summary import repository
from modules.summary.schemas import SummaryResponse


def get_summary(db: Session) -> SummaryResponse:
    return SummaryResponse(
        organization_records=repository.get_organization_records(db),
        active_organizations=repository.get_active_organizations(db),
        states=repository.get_states(db),
        cities=repository.get_cities(db),
        activity_areas=repository.get_activity_areas(db),
    )
