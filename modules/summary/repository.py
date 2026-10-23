from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from modules.organizations.models import (
    ActivityArea,
    Municipality,
    Organization,
)


def get_organization_records(db: Session) -> int:
    """Returns the total number of registered organizations."""
    statement = select(func.count()).select_from(Organization)

    return db.scalar(statement) or 0


def get_active_organizations(db: Session) -> int:
    """Returns the number of active organizations."""
    statement = (
        select(func.count())
        .select_from(Organization)
        .where(Organization.registration_status == "ACTIVE")
    )

    return db.scalar(statement) or 0


def get_states(db: Session) -> int:
    """Returns the number of distinct states with registered organizations."""
    statement = (
        select(func.count(distinct(Municipality.state_code)))
        .select_from(Organization)
        .join(Organization.municipality)
        .where(Municipality.state_code.is_not(None))
    )

    return db.scalar(statement) or 0


def get_cities(db: Session) -> int:
    """Returns the number of distinct municipalities with registered organizations."""
    statement = (
        select(func.count(distinct(Organization.municipality_code)))
        .select_from(Organization)
        .where(Organization.municipality_code.is_not(None))
    )

    return db.scalar(statement) or 0


def get_activity_areas(db: Session) -> int:
    """Returns the total number of registered activity areas."""
    statement = select(func.count()).select_from(ActivityArea)

    return db.scalar(statement) or 0
