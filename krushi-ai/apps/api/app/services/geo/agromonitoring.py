import httpx
from app.core.config import settings

class AgroMonitoringService:
    BASE_URL = "http://api.agromonitoring.com/agro/1.0"

    @classmethod
    async def get_weather(cls, lat: float, lon: float) -> dict:
        url = f"{cls.BASE_URL}/weather?lat={lat}&lon={lon}&appid={settings.AGROMONITORING_API_KEY}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e), "message": "Weather data unavailable"}

    @classmethod
    async def get_ndvi(cls, poly_id: str, start: int, end: int) -> dict:
        return {"ndvi_mean": 0.65, "status": "Healthy (Mock)"}
