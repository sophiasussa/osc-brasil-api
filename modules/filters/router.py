from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.filters import service
from modules.filters.schemas import CitiesResponse, FiltersResponse


router = APIRouter(prefix="/filters", tags=["Filters"])


@router.get("", response_model=FiltersResponse)
def get_filters(db: Session = Depends(get_db)):
    """Returns the available filter options."""
    return service.get_filters(db)


@router.get("/cities", response_model=CitiesResponse)
def get_cities_by_uf(
    uf: str = Query(
        min_length=2,
        max_length=2,
        pattern="^[A-Za-z]{2}$",
        description="Two-letter Brazilian state code, e.g. GO",
    ),
    db: Session = Depends(get_db),
):
    """Returns cities associated with organizations in a state."""
    uf = uf.upper()

    valid_ufs = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF",
        "ES", "GO", "MA", "MT", "MS", "MG", "PA",
        "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
        "RO", "RR", "SC", "SP", "SE", "TO",
    }

    if uf not in valid_ufs:
        raise HTTPException(
            status_code=422,
            detail="Invalid Brazilian state code.",
        )

    return service.get_cities_by_uf(db, uf)
