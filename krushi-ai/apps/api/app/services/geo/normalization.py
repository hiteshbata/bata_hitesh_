import httpx
class LocationNormalizationService:
    @staticmethod
    async def normalize_village(village_name: str):
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={village_name},Gujarat,India&format=json&limit=1"
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=5, headers={"User-Agent": "KrushiAI/1.0"})
                data = r.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]
        except:
            pass
        return None
