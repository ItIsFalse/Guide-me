from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.property import Property
from app.schemas.tour import RouteRequest, RouteResponse
from app.schemas.common import DataResponse
from app.utils.geo import haversine_distance, estimate_travel_time

router = APIRouter()


@router.post("/route", response_model=DataResponse[RouteResponse])
def build_route(request: RouteRequest, db: Session = Depends(get_db)):
    """Построить маршрут от пользователя до выбранного места."""
    prop = db.query(Property).filter(
        Property.id == request.property_id,
        Property.is_active == True
    ).first()

    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if prop.lat is None or prop.lon is None:
        raise HTTPException(status_code=400, detail="Property has no coordinates")

    distance = haversine_distance(request.user_lat, request.user_lon, prop.lat, prop.lon)
    time_min = estimate_travel_time(distance, request.transport_type)

    result = RouteResponse(
        from_lat=request.user_lat,
        from_lon=request.user_lon,
        to_name=prop.name_en,
        to_lat=prop.lat,
        to_lon=prop.lon,
        distance_km=round(distance, 2),
        time_minutes=time_min,
        transport=request.transport_type,
    )

    return DataResponse(data=result, message="Route calculated")