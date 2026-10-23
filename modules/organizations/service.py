from math import ceil

from modules.organizations.models import Organization
from modules.organizations.repository import OrganizationRepository


class OrganizationService:
    def __init__(self, repository: OrganizationRepository) -> None:
        self.repository = repository

    def list_organizations(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        state: str | None = None,
        city: str | None = None,
        status: str | None = None,
        legal_nature: str | None = None,
        founded_from: int | None = None,
        founded_to: int | None = None,
        activity_area: str | None = None,
    ) -> dict:
        filters = {
            "search": search,
            "state": state,
            "city": city,
            "status": status,
            "legal_nature": legal_nature,
            "founded_from": founded_from,
            "founded_to": founded_to,
            "activity_area": activity_area,
        }

        offset = (page - 1) * page_size

        organizations = self.repository.list(
            offset=offset,
            limit=page_size,
            **filters,
        )

        total = self.repository.count(**filters)

        items = [
            {
                "id": organization.id,
                "name": organization.legal_name,
                "cnpj": organization.cnpj,
                "city": (
                    organization.municipality.name
                    if organization.municipality
                    else None
                ),
                "state": (
                    organization.municipality.state_code
                    if organization.municipality
                    else None
                ),
                "status": organization.registration_status,
                "legal_nature": (
                    organization.legal_nature.description
                    if organization.legal_nature
                    else None
                ),
                "foundation_year": (
                    organization.foundation_date.year
                    if organization.foundation_date
                    else None
                ),
                "activity_areas": [
                    area.name for area in organization.areas
                ],
            }
            for organization in organizations
        ]

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        }

    def get_organization(
        self,
        organization_id: int,
    ) -> Organization | None:
        return self.repository.get_by_id(organization_id)
