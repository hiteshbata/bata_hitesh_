from app.db.supabase import get_supabase_client

class PromptService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def get_latest_prompt(self, name: str) -> str:
        fallback_prompt = """
        You are Krushi AI Assistant, a helpful AI for Indian farmers.
        Given the following context, generate a structured insight in JSON format.

        Farmer Context: {farmer_context}
        Known Village: {known_village}
        Weather Data: {weather_data}
        NDVI Data: {ndvi_data}
        User Message: {user_message}

        Return JSON matching this exact schema:
        {{
            "risk_level": "low/medium/high",
            "water_stress": true/false,
            "recommended_action": "brief english text",
            "language": "Gujarati",
            "conversational_response": "The final translated Gujarati message directly responding to the user. If they ask about their location and Known Village is present, tell them their village name.",
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
