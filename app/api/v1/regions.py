from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.region import Region
from app.schemas.region import RegionResponse, RegionListResponse

router = APIRouter()


@router.get("/", response_model=RegionListResponse)
def get_regions(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """Список всех областей."""
    query = db.query(Region)
    if active_only:
        query = query.filter(Region.is_active == True)
    regions = query.all()
    return RegionListResponse(
        data=[RegionResponse.model_validate(r) for r in regions],
        total=len(regions),
    )


@router.get("/{region_id}", response_model=RegionResponse)
def get_region(region_id: int, db: Session = Depends(get_db)):
    """Одна область по ID."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return RegionResponse.model_validate(region)