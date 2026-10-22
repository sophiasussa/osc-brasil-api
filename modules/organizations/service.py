from modules.organizations.models import Organization
from modules.organizations.repository import OrganizationRepository


class OrganizationService:
    def __init__(self, repository: OrganizationRepository) -> None:
        self.repository = repository

    def list_organizations(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Organization]:
        return self.repository.list(offset=offset, limit=limit)

    def get_organization(self, organization_id: int) -> Organization | None:
        return self.repository.get_by_id(organization_id)
