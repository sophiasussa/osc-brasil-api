from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, String, case, func, literal, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from modules.organizations.models import Organization


GENERAL_DATA_FIELDS = (
    "legal_name",
    "cnpj",
    "trade_name",
    "legal_nature_code",
    "matrix_or_branch",
    "registration_status",
    "removed_from_mosc",
    "foundation_date",
    "closing_date",
    "closing_year",
    "address",
    "municipality_code",
    "latitude",
    "longitude",
)

CATEGORY_DEFINITIONS = (
    ("general_data", "General Data"),
    ("activity_areas", "Areas & Subareas"),
    ("description", "Description"),
    ("governance", "Work & Governance"),
    ("projects", "Projects & Programs"),
    ("funding", "Funding Sources"),
)

CALCULABLE_CATEGORIES = ("general_data", "activity_areas")


def _is_string_field(field: str) -> bool:
    return isinstance(Organization.__table__.c[field].type, String)


def _filled(field: str, value: Any) -> bool:
    if _is_string_field(field):
        if not isinstance(value, str):
            return False
        return bool(value.strip())
    return value is not None


def calculate_organization_completeness(organization: Organization) -> dict:
    general_filled = sum(
        _filled(field, getattr(organization, field))
        for field in GENERAL_DATA_FIELDS
    )
    activity_filled = int(bool(organization.areas)) + int(
        bool(organization.subareas)
    )
    general_percentage = general_filled * 100 / len(GENERAL_DATA_FIELDS)
    activity_percentage = activity_filled * 50

    percentages: dict[str, float | None] = {
        "general_data": round(general_percentage, 1),
        "activity_areas": round(activity_percentage, 1),
        "description": None,
        "governance": None,
        "projects": None,
        "funding": None,
    }

    available_percentages = [
        percentages[key]
        for key in CALCULABLE_CATEGORIES
        if percentages[key] is not None
    ]

    return {
        "average": (
            round(
                (general_percentage + activity_percentage) / 2,
                1,
            )
            if available_percentages
            else None
        ),
        "categories": [
            {
                "key": key,
                "label": label,
                "percentage": percentages[key],
            }
            for key, label in CATEGORY_DEFINITIONS
        ],
    }


def _column_is_filled(field: str) -> ColumnElement[bool]:
    column = Organization.__table__.c[field]
    if _is_string_field(field):
        return func.nullif(func.trim(column), "").is_not(None)
    return column.is_not(None)


def _percentage_expression(fields: Sequence[str]) -> ColumnElement[Any]:
    filled = sum(
        (
            case((_column_is_filled(field), 1), else_=0)
            for field in fields
        ),
        literal(0),
    )
    return filled * 100.0 / len(fields)


def aggregate_completeness(
    filtered_organizations: Select,
    db: Session,
) -> dict:
    organization_ids = filtered_organizations.subquery()
    general_percentage = _percentage_expression(GENERAL_DATA_FIELDS)

    area_filled = (
        case((Organization.areas.any(), 1), else_=0)
        + case((Organization.subareas.any(), 1), else_=0)
    )
    activity_percentage = area_filled * 50.0
    average_percentage = (general_percentage + activity_percentage) / 2.0

    result = db.execute(
        select(
            func.avg(general_percentage),
            func.avg(activity_percentage),
            func.avg(average_percentage),
        )
        .select_from(Organization)
        .join(
            organization_ids,
            Organization.id == organization_ids.c.id,
        )
    ).one()

    values = {
        "general_data": result[0],
        "activity_areas": result[1],
        "description": None,
        "governance": None,
        "projects": None,
        "funding": None,
    }

    return {
        "average": round(float(result[2]), 1) if result[2] is not None else None,
        "categories": [
            {
                "key": key,
                "label": label,
                "percentage": (
                    round(float(values[key]), 1)
                    if values[key] is not None
                    else None
                ),
            }
            for key, label in CATEGORY_DEFINITIONS
        ],
    }
