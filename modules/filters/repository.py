from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from modules.organizations.models import (
    ActivityArea,
    LegalNature,
    Municipality,
    Organization,
)


STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


def get_states(db: Session) -> list[tuple[str, str]]:
    """Returns distinct state codes and names for states with organizations."""
    statement = (
        select(distinct(Municipality.state_code))
        .select_from(Organization)
        .join(Organization.municipality)
        .where(Municipality.state_code.is_not(None))
        .order_by(Municipality.state_code)
    )

    state_codes = db.scalars(statement).all()

    return [
        (code, STATE_NAMES[code])
        for code in state_codes
        if code in STATE_NAMES
    ]


def get_statuses(db: Session) -> list[str]:
    """Returns distinct registration statuses present in the dataset."""
    statement = (
        select(distinct(Organization.registration_status))
        .where(Organization.registration_status.is_not(None))
        .order_by(Organization.registration_status)
    )

    return list(db.scalars(statement).all())


def get_legal_natures(db: Session) -> list[str]:
    """Returns legal nature names available in the database."""
    statement = (
        select(distinct(LegalNature.description))
        .where(LegalNature.description.is_not(None))
        .order_by(LegalNature.description)
    )

    return list(db.scalars(statement).all())


def get_activity_areas(db: Session) -> list[str]:
    """Returns activity area names available in the database."""
    statement = (
        select(distinct(ActivityArea.name))
        .where(ActivityArea.name.is_not(None))
        .order_by(ActivityArea.name)
    )

    return list(db.scalars(statement).all())


def get_foundation_year_range(
    db: Session,
) -> tuple[int | None, int | None]:
    """Returns the earliest and latest foundation years available."""
    statement = select(
        func.min(func.extract("year", Organization.foundation_date)),
        func.max(func.extract("year", Organization.foundation_date)),
    )

    min_year, max_year = db.execute(statement).one()

    return (
        int(min_year) if min_year is not None else None,
        int(max_year) if max_year is not None else None,
    )


def get_cities_by_uf(
    db: Session,
    uf: str,
) -> list[tuple[int, str]]:
    """Returns municipality codes and names for a given state."""
    statement = (
        select(
            Municipality.code,
            Municipality.name,
        )
        .select_from(Organization)
        .join(Organization.municipality)
        .where(
            Municipality.state_code == uf,
            Municipality.name.is_not(None),
        )
        .distinct()
        .order_by(Municipality.name)
    )

    return [
        (code, name)
        for code, name in db.execute(statement).all()
    ]
