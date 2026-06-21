from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.property import PropertyResponse, PropertyDetailResponse, PropertyListResponse
from app.services.property_service import get_properties, get_property_by_id, get_property_units
from app.models.property import Property
from app.models.property_hotel import PropertyHotel
from app.schemas.property_hotel import PropertyHotelResponse
from app.schemas.common import DataResponse
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

@router.get("/{property_id}/nearby", response_model=PropertyListResponse)
def nearby_properties(
    property_id: int,
    radius_km: float = Query(5.0, ge=0.5, le=50),
    db: Session = Depends(get_db),
):
    """Места того же типа неподалёку."""
    prop = get_property_by_id(db, property_id)
    if not prop or not prop.lat or not prop.lon:
        raise HTTPException(status_code=404, detail="Property not found or no coordinates")

    from app.utils.geo import haversine_distance

    candidates = (
        db.query(Property)
        .filter(
            Property.is_active == True,
            Property.moderation_status == "approved",
            Property.property_type == prop.property_type,
            Property.id != property_id,
        )
        .all()
    )

    nearby = []
    for c in candidates:
        if c.lat and c.lon:
            dist = haversine_distance(prop.lat, prop.lon, c.lat, c.lon)
            if dist <= radius_km:
                nearby.append((c, dist))

    nearby.sort(key=lambda x: x[1])
    result = [PropertyResponse.model_validate(p) for p, d in nearby[:5]]

    return PropertyListResponse(data=result, total=len(result))

@router.get("/{property_id}/hotels", response_model=DataResponse[list[PropertyHotelResponse]])
def get_property_hotels(property_id: int, db: Session = Depends(get_db)):
    """Список номеров/коттеджей отеля."""
    hotels = db.query(PropertyHotel).filter(
        PropertyHotel.property_id == property_id,
        PropertyHotel.is_active == True
    ).order_by(PropertyHotel.base_price.asc()).all()
    return DataResponse(data=[PropertyHotelResponse.model_validate(h) for h in hotels])