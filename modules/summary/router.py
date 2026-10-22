
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.summary import service
from modules.summary.schemas import SummaryResponse


router = APIRouter(
    prefix="/summary",
    tags=["Summary"],
)


@router.get("", response_model=SummaryResponse)
def read_summary(
    db: Session = Depends(get_db),
) -> SummaryResponse:
    return service.get_summary(db)
