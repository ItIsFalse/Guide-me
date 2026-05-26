import httpx
from app.core.config import settings


async def get_weather(lat: float, lon: float) -> dict | None:
    """Получает текущую погоду через OpenWeatherMap."""
    if not settings.OPENWEATHER_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": settings.OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "en",
                },
            )
            if response.status_code != 200:
                return None

            data = response.json()
            return {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "city": data.get("name", ""),
            }
    except Exception:
        return None