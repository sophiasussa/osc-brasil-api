from sqlalchemy import Integer, distinct, func, select
from sqlalchemy.orm import Session

from modules.organizations.completeness import aggregate_completeness
from modules.organizations.models import (
    ActivityArea,
    LegalNature,
    Municipality,
    Organization,
)
from modules.organizations.repository import apply_organization_filters


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_analytics(self, **filters: int | str | None) -> dict:
        filtered_organizations = apply_organization_filters(
            select(Organization.id),
            **filters,
        )
        filtered_ids = filtered_organizations.subquery()
        organization_predicate = Organization.id.in_(
            select(filtered_ids.c.id)
        )

        organizations = self.db.scalar(
            select(func.count(distinct(Organization.id))).where(
                organization_predicate
            )
        ) or 0
        states = self.db.scalar(
            select(func.count(distinct(Municipality.state_code)))
            .select_from(Organization)
            .join(Organization.municipality)
            .where(
                organization_predicate,
                Municipality.state_code.is_not(None),
            )
        ) or 0
        activity_area_count = self.db.scalar(
            select(func.count(distinct(ActivityArea.id)))
            .select_from(Organization)
            .join(Organization.areas)
            .where(organization_predicate)
        ) or 0

        by_state = self.db.execute(
            select(
                Municipality.state_code,
                func.count(distinct(Organization.id)),
            )
            .select_from(Organization)
            .join(Organization.municipality)
            .where(
                organization_predicate,
                Municipality.state_code.is_not(None),
            )
            .group_by(Municipality.state_code)
            .order_by(Municipality.state_code)
        ).all()

        by_activity_area = self.db.execute(
            select(
                ActivityArea.name,
                func.count(distinct(Organization.id)),
            )
            .select_from(Organization)
            .join(Organization.areas)
            .where(organization_predicate)
            .group_by(ActivityArea.id, ActivityArea.name)
            .order_by(
                func.count(distinct(Organization.id)).desc(),
                ActivityArea.name,
            )
        ).all()

        foundation_year = func.extract(
            "year", Organization.foundation_date
        ).cast(Integer)
        by_foundation_year = self.db.execute(
            select(foundation_year, func.count(distinct(Organization.id)))
            .where(
                organization_predicate,
                Organization.foundation_date.is_not(None),
            )
            .group_by(foundation_year)
            .order_by(foundation_year)
        ).all()

        by_legal_nature = self.db.execute(
            select(
                LegalNature.description,
                func.count(distinct(Organization.id)),
            )
            .select_from(Organization)
            .join(Organization.legal_nature)
            .where(organization_predicate)
            .group_by(LegalNature.code, LegalNature.description)
            .order_by(
                func.count(distinct(Organization.id)).desc(),
                LegalNature.description,
            )
        ).all()

        return {
            "summary": {
                "organizations": organizations,
                "states": states,
                "activity_areas": activity_area_count,
            },
            "by_state": [
                {"state": state, "count": count}
                for state, count in by_state
            ],
            "by_activity_area": [
                {"name": name, "count": count}
                for name, count in by_activity_area
            ],
            "by_foundation_year": [
                {"year": int(year), "count": count}
                for year, count in by_foundation_year
            ],
            "by_legal_nature": [
                {"name": name, "count": count}
                for name, count in by_legal_nature
            ],
            "completeness": aggregate_completeness(
                filtered_organizations,
                self.db,
            ),
        }