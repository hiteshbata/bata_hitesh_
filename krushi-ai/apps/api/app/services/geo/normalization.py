import httpx
from typing import Optional, Tuple
import urllib.parse

class LocationNormalizationService:
    @staticmethod
    async def normalize_village(village_name: str, state: str = "Gujarat") -> Optional[Tuple[float, float, str]]:
        query = f"{village_name}, {state}, India"
        encoded_query = urllib.parse.quote(query)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1"

        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": "KrushiAIAssistant/1.0"}
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    normalized_name = data[0]["name"]
                    return lat, lon, normalized_name
            return None
