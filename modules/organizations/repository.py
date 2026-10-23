from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from modules.organizations.models import (
    ActivityArea,
    Municipality,
    Organization,
    OrganizationCnae,
)


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        state: str | None = None,
        city: str | None = None,
        status: str | None = None,
        legal_nature: str | None = None,
        founded_from: int | None = None,
        founded_to: int | None = None,
        activity_area: str | None = None,
    ) -> list[Organization]:
        statement = select(Organization)

        if search:
            term = search.strip()
            if term:
                statement = statement.where(
                    or_(
                        Organization.legal_name.ilike(f"%{term}%"),
                        Organization.trade_name.ilike(f"%{term}%"),
                        Organization.cnpj.ilike(f"%{term}%"),
                    )
                )

        if state:
            statement = statement.where(
                Organization.municipality.has(
                    Municipality.state_code == state
                )
            )

        if city:
            statement = statement.where(
                Organization.municipality.has(
                    Municipality.name.ilike(f"%{city.strip()}%")
                )
            )

        if status:
            statement = statement.where(
                Organization.registration_status == status
            )

        if legal_nature:
            statement = statement.where(
                Organization.legal_nature_code == legal_nature
            )

        if founded_from is not None:
            statement = statement.where(
                Organization.foundation_date >= date(founded_from, 1, 1)
            )

        if founded_to is not None:
            statement = statement.where(
                Organization.foundation_date < date(founded_to + 1, 1, 1)
            )

        if activity_area:
            statement = statement.where(
                Organization.areas.any(
                    ActivityArea.name == activity_area
                )
            )

        statement = (
            statement
            .options(
                selectinload(Organization.municipality),
                selectinload(Organization.legal_nature),
                selectinload(Organization.areas),
            )
            .order_by(Organization.id)
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def count(
        self,
        *,
        search: str | None = None,
        state: str | None = None,
        city: str | None = None,
        status: str | None = None,
        legal_nature: str | None = None,
        founded_from: int | None = None,
        founded_to: int | None = None,
        activity_area: str | None = None,
    ) -> int:
        statement = select(func.count(Organization.id))

        if search:
            term = search.strip()
            if term:
                statement = statement.where(
                    or_(
                        Organization.legal_name.ilike(f"%{term}%"),
                        Organization.trade_name.ilike(f"%{term}%"),
                        Organization.cnpj.ilike(f"%{term}%"),
                    )
                )

        if state:
            statement = statement.where(
                Organization.municipality.has(
                    Municipality.state_code == state
                )
            )

        if city:
            statement = statement.where(
                Organization.municipality.has(
                    Municipality.name.ilike(f"%{city.strip()}%")
                )
            )

        if status:
            statement = statement.where(
                Organization.registration_status == status
            )

        if legal_nature:
            statement = statement.where(
                Organization.legal_nature_code == legal_nature
            )

        if founded_from is not None:
            statement = statement.where(
                Organization.foundation_date >= date(founded_from, 1, 1)
            )

        if founded_to is not None:
            statement = statement.where(
                Organization.foundation_date < date(founded_to + 1, 1, 1)
            )

        if activity_area:
            statement = statement.where(
                Organization.areas.any(
                    ActivityArea.name == activity_area
                )
            )

        return self.db.scalar(statement) or 0

    def get_by_id(self, organization_id: int) -> Organization | None:
        statement = (
            select(Organization)
            .options(
                selectinload(Organization.areas),
                selectinload(Organization.subareas),
                selectinload(Organization.municipality),
                selectinload(Organization.legal_nature),
                selectinload(Organization.cnaes).selectinload(
                    OrganizationCnae.cnae
                ),
            )
            .where(Organization.id == organization_id)
        )

        return self.db.scalars(statement).first()
