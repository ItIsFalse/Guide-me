from sqlalchemy.orm import Session
from app.models.property import Property
from app.models.tour import TourStop
from app.utils.geo import haversine_distance, estimate_travel_time


def calculate_navigation(db: Session, tour) -> list[dict]:
    """Рассчитывает шаги навигации: время в пути, расстояние."""
    stops = (
        db.query(TourStop)
        .filter(TourStop.tour_id == tour.id)
        .order_by(TourStop.stop_order)
        .all()
    )

    if not stops:
        return []

    property_ids = [s.property_id for s in stops]
    properties = {
        p.id: p
        for p in db.query(Property).filter(Property.id.in_(property_ids)).all()
    }

    steps = []
    prev_lat, prev_lon = None, None

    for stop in stops:
        prop = properties.get(stop.property_id)
        if not prop or not prop.lat or not prop.lon:
            continue

        travel_time = 0
        distance = 0.0

        if prev_lat is not None:
            distance = haversine_distance(prev_lat, prev_lon, prop.lat, prop.lon)
            travel_time = estimate_travel_time(distance, tour.transport_type)

        steps.append({
            "stop_order": stop.stop_order,
            "property_id": prop.id,
            "property_name": prop.name_en,
            "property_type": prop.property_type,
            "lat": prop.lat,
            "lon": prop.lon,
            "duration_minutes": stop.duration_minutes or 60,
            "travel_time_minutes": travel_time,
            "distance_km": round(distance, 2),
        })

        prev_lat, prev_lon = prop.lat, prop.lon

    return steps