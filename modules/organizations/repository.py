from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.organizations.models import Organization


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Organization]:
        statement = (
            select(Organization)
            .options(
                selectinload(Organization.areas),
                selectinload(Organization.subareas),
            )
            .order_by(Organization.id)
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, organization_id: int) -> Organization | None:
        statement = (
            select(Organization)
            .options(
                selectinload(Organization.areas),
                selectinload(Organization.subareas),
            )
            .where(Organization.id == organization_id)
        )

        return self.db.scalars(statement).first()
