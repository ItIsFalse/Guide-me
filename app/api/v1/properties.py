from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.property import PropertyResponse, PropertyDetailResponse, PropertyListResponse
from app.services.property_service import get_properties, get_property_by_id, get_property_units

router = APIRouter()


@router.get("/", response_model=PropertyListResponse)
def list_properties(
    region_id: Optional[int] = Query(None),
    property_type: Optional[str] = Query(None, description="hotel, museum, park, restaurant, shop, entertainment"),
    stars: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Список всех мест с фильтрацией."""
    properties, total = get_properties(
        db,
        region_id=region_id,
        property_type=property_type,
        stars=stars,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PropertyListResponse(
        data=[PropertyResponse.model_validate(p) for p in properties],
        total=total,
    )


@router.get("/{property_id}", response_model=PropertyDetailResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """Детальная информация о месте с юнитами."""
    prop = get_property_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    units = get_property_units(db, property_id)
    result = PropertyDetailResponse.model_validate(prop)
    result.units = units
    return result