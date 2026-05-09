import httpx
from app.core.config import settings
class AgroMonitoringService:
    @staticmethod
    async def get_weather(lat: float, lon: float) -> dict:
        try:
            url = f"http://api.agromonitoring.com/agro/1.0/weather?lat={lat}&lon={lon}&appid={settings.AGROMONITORING_API_KEY}"
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=5)
                return r.json()
        except:
            return {}
    @staticmethod
    async def get_ndvi(poly_id: str, lat: float, lon: float) -> dict:
        return {"ndvi": 0.6, "status": "healthy"}
