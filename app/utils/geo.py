import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками в километрах (формула гаверсинуса)."""
    R = 6371.0  # радиус Земли
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def estimate_travel_time(distance_km: float, transport_type: str = "public") -> int:
    """Примерное время в пути в минутах."""
    speeds = {
        "walking": 5.0,
        "public": 40.0,
        "car": 50.0,
        "bicycle": 15.0,
    }
    speed = speeds.get(transport_type, 40.0)
    return max(1, round((distance_km / speed) * 60))