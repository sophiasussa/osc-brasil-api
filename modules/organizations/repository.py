import unicodedata
from datetime import date

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from modules.organizations.models import (
    ActivityArea,
    Municipality,
    Organization,
    OrganizationCnae,
)


def _normalize_search_term(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.lower())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


def apply_organization_filters(
    statement: Select,
    *,
    search: str | None = None,
    state: str | None = None,
    city: str | None = None,
    status: str | None = None,
    legal_nature: int | None = None,
    founded_from: int | None = None,
    founded_to: int | None = None,
    activity_area: str | None = None,
) -> Select:
    if search:
        term = search.strip()
        if term:
            normalized_term = _normalize_search_term(term)
            search_terms = dict.fromkeys(
                value
                for value in (term, normalized_term)
                if value
            )
            search_conditions = []
            for value in search_terms:
                pattern = f"%{value}%"
                search_conditions.extend(
                    (
                        Organization.legal_name.ilike(pattern),
                        Organization.trade_name.ilike(pattern),
                        Organization.cnpj.ilike(pattern),
                        Organization.municipality.has(
                            Municipality.name.ilike(pattern)
                        ),
                    )
                )
            statement = statement.where(or_(*search_conditions))

    if state:
        statement = statement.where(
            Organization.municipality.has(Municipality.state_code == state)
        )

    if city:
        statement = statement.where(
            Organization.municipality.has(
                Municipality.name.ilike(f"%{city.strip()}%")
            )
        )

    if status:
        statement = statement.where(Organization.registration_status == status)

    if legal_nature is not None:
        statement = statement.where(Organization.legal_nature_code == legal_nature)

    if founded_from is not None:
        statement = statement.where(
            Organization.foundation_date >= date(founded_from, 1, 1)
        )

    if founded_to is not None and founded_to < 9999:
        statement = statement.where(
            Organization.foundation_date < date(founded_to + 1, 1, 1)
        )

    if activity_area:
        statement = statement.where(
            Organization.areas.any(ActivityArea.name == activity_area)
        )

    return statement


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
        legal_nature: int | None = None,
        founded_from: int | None = None,
        founded_to: int | None = None,
        activity_area: str | None = None,
    ) -> list[Organization]:
        statement = apply_organization_filters(
            select(Organization),
            search=search,
            state=state,
            city=city,
            status=status,
            legal_nature=legal_nature,
            founded_from=founded_from,
            founded_to=founded_to,
            activity_area=activity_area,
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
        legal_nature: int | None = None,
        founded_from: int | None = None,
        founded_to: int | None = None,
        activity_area: str | None = None,
    ) -> int:
        statement = apply_organization_filters(
            select(func.count(Organization.id)),
            search=search,
            state=state,
            city=city,
            status=status,
            legal_nature=legal_nature,
            founded_from=founded_from,
            founded_to=founded_to,
            activity_area=activity_area,
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
