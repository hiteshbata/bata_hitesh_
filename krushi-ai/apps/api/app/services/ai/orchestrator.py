from app.services.ai.memory import AIMemoryLayer
from app.services.ai.prompts import PromptService
from app.services.ai.gemini import GeminiService
from app.services.geo.agromonitoring import AgroMonitoringService
from app.services.geo.normalization import LocationNormalizationService
from app.schemas.ai import StructuredInsight

class AIOrchestrator:
    def __init__(self):
        self.memory = AIMemoryLayer()
        self.prompts = PromptService()
        self.ai = GeminiService()

    async def process_message(self, farmer_id: str, user_message: str, village_name: str = None) -> StructuredInsight:
        context = self.memory.get_context(farmer_id)

        weather_data = {}
        ndvi_data = {}

        target_village = village_name or "Rajkot"

        loc = await LocationNormalizationService.normalize_village(target_village)
        if loc:
            lat, lon, norm_name = loc
            weather_data = await AgroMonitoringService.get_weather(lat, lon)
            ndvi_data = await AgroMonitoringService.get_ndvi("dummy_poly_id", 0, 0)

        prompt_template = self.prompts.get_latest_prompt("crop_health_analysis")

        formatted_prompt = prompt_template.format(
            farmer_context=context,
            weather_data=weather_data,
            ndvi_data=ndvi_data,
            user_message=user_message
        )

        insight = self.ai.generate_insight(formatted_prompt)

        if "water" in user_message.lower() or "irrigation" in user_message.lower():
            issues = context.get("recurring_issues", [])
            if "water" not in issues:
                issues.append("water")
                self.memory.update_context(farmer_id, {"recurring_issues": issues})

        return insight
