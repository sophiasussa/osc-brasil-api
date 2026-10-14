from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.organizations.repository import OrganizationRepository
from modules.organizations.schemas import OrganizationResponse
from modules.organizations.service import OrganizationService


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


def get_organization_service(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationService:
    repository = OrganizationRepository(db)
    return OrganizationService(repository)


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
def list_organizations(
    service: Annotated[OrganizationService, Depends(get_organization_service)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[OrganizationResponse]:
    return service.list_organizations(offset=offset, limit=limit)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: int,
    service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> OrganizationResponse:
    organization = service.get_organization(organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization
