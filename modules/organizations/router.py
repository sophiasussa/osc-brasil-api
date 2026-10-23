from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.organizations.repository import OrganizationRepository
from modules.organizations.schemas import (
    OrganizationListResponse,
    OrganizationResponse,
)
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
    response_model=OrganizationListResponse,
)
def list_organizations(
    service: Annotated[
        OrganizationService,
        Depends(get_organization_service),
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pageSize")] = 20,
    search: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    city: Annotated[str | None, Query()] = None,
    status_filter: Annotated[
        str | None,
        Query(alias="status"),
    ] = None,
    legal_nature: Annotated[
        str | None,
        Query(alias="legalNature"),
    ] = None,
    founded_from: Annotated[
        int | None,
        Query(ge=1, le=9999, alias="foundedFrom"),
    ] = None,
    founded_to: Annotated[
        int | None,
        Query(ge=1, le=9999, alias="foundedTo"),
    ] = None,
    activity_area: Annotated[
        str | None,
        Query(alias="activityArea"),
    ] = None,
) -> OrganizationListResponse:
    return service.list_organizations(
        page=page,
        page_size=page_size,
        search=search,
        state=state,
        city=city,
        status=status_filter,
        legal_nature=legal_nature,
        founded_from=founded_from,
        founded_to=founded_to,
        activity_area=activity_area,
    )


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: int,
    service: Annotated[
        OrganizationService,
        Depends(get_organization_service),
    ],
) -> OrganizationResponse:
    organization = service.get_organization(organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization
