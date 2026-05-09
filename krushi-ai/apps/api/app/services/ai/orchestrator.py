from app.services.ai.memory import AIMemoryLayer
from app.services.ai.prompts import PromptService
from app.services.ai.gemini import GeminiService
from app.services.geo.agromonitoring import AgroMonitoringService
from app.services.geo.normalization import LocationNormalizationService
from app.schemas.ai import StructuredInsight
from app.db.supabase import get_supabase_client

class AIOrchestrator:
    def __init__(self):
        self.memory = AIMemoryLayer()
        self.prompts = PromptService()
        self.ai = GeminiService()
        self.supabase = get_supabase_client()

    async def process_message(self, farmer_id: str, user_message: str) -> StructuredInsight:
        # 1. Fetch Farmer DB context & known village
        context = self.memory.get_context(farmer_id)

        farmer_res = self.supabase.table("farmers").select("village_id").eq("id", farmer_id).execute()
        village_name = None
        if farmer_res.data and farmer_res.data[0].get("village_id"):
            vid = farmer_res.data[0]["village_id"]
            village_res = self.supabase.table("villages").select("name, normalized_name, gps_location").eq("id", vid).execute()
            if village_res.data:
                village_name = village_res.data[0].get("name")

        weather_data = {}
        ndvi_data = {}

        # 2. Fetch Geo/Weather data if village is known
        if village_name:
            loc = await LocationNormalizationService.normalize_village(village_name)
            if loc:
                lat, lon, norm_name = loc
                weather_data = await AgroMonitoringService.get_weather(lat, lon)
                ndvi_data = await AgroMonitoringService.get_ndvi("dummy_poly_id", 0, 0)

        # 3. Formulate prompt & call Gemini 2.0
        prompt_template = self.prompts.get_latest_prompt("crop_health_analysis")
        formatted_prompt = prompt_template.format(
            farmer_context=context,
            known_village=village_name or "Unknown",
            weather_data=weather_data,
            ndvi_data=ndvi_data,
            user_message=user_message
        )

        insight = self.ai.generate_insight(formatted_prompt)

        # 4. Save Extracted Intents to DB
        # Update Location Memory (Slot Filling)
        if insight.location_detected:
            loc = await LocationNormalizationService.normalize_village(insight.location_detected)
            if loc:
                lat, lon, norm_name = loc
                # Find or create village
                v_res = self.supabase.table("villages").select("id").eq("normalized_name", norm_name).execute()
                if v_res.data:
                    new_vid = v_res.data[0]["id"]
                else:
                    # Create new village
                    # Note: For PostGIS gps_location, we pass a WKT string. If it fails, we fall back to null.
                    try:
                        v_insert = self.supabase.table("villages").insert({
                            "name": insight.location_detected,
                            "normalized_name": norm_name,
                            "gps_location": f"POINT({lon} {lat})"
                        }).execute()
                        new_vid = v_insert.data[0]["id"]
                    except Exception:
                        v_insert = self.supabase.table("villages").insert({
                            "name": insight.location_detected,
                            "normalized_name": norm_name
                        }).execute()
                        new_vid = v_insert.data[0]["id"]

                # Update farmer profile
                self.supabase.table("farmers").update({"village_id": new_vid}).eq("id", farmer_id).execute()

        # Update Crop Memory
        if insight.crop_detected:
            history = context.get("crop_history", [])
            if insight.crop_detected not in history:
                history.append(insight.crop_detected)
                self.memory.update_context(farmer_id, {"crop_history": history})

        if "water" in user_message.lower() or "irrigation" in user_message.lower():
            issues = context.get("recurring_issues", [])
            if "water" not in issues:
                issues.append("water")
                self.memory.update_context(farmer_id, {"recurring_issues": issues})

        return insight
