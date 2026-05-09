from app.db.supabase import get_supabase_client

class PromptService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def get_latest_prompt(self, name: str) -> str:
        fallback_prompt = """
        You are Krushi AI Assistant, a helpful AI for Indian farmers.

        The farmer in {known_village} is reporting issues or asking questions.
        Current weather data (if available): {weather_data}.
        NDVI data: {ndvi_data}.
        Based on their history of {farmer_context}, what is the likely cause or best advice?

        User Message: {user_message}

        Return JSON matching this exact schema:
        {{
            "risk_level": "low/medium/high",
            "water_stress": true/false,
            "recommended_action": "brief english text",
            "language": "Gujarati",
            "conversational_response": "The final translated Gujarati message directly responding to the user. Use the weather and crop history to make it highly accurate and natural.",
            "location_detected": "Extract any new village/location mentioned, or null",
            "crop_detected": "Extract any new crop mentioned, or null",
            "area_detected": "Extract farm size/area mentioned, or null"
        }}
        """
        try:
            response = self.supabase.table("prompt_templates")\
                .select("content")\
                .eq("name", name)\
                .eq("is_active", True)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            if response.data:
                return response.data[0]["content"]
        except Exception:
            pass
        return fallback_prompt
