from app.db.supabase import get_supabase_client

class PromptService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def get_latest_prompt(self, name: str) -> str:
        fallback_prompt = """
        You are Krushi AI Assistant, a helpful AI for Indian farmers.
        Given the following context, generate a structured insight in JSON format.

        Farmer Context: {farmer_context}
        Weather Data: {weather_data}
        NDVI Data: {ndvi_data}
        User Message: {user_message}

        Return JSON matching this schema:
        {{
            "risk_level": "low/medium/high",
            "water_stress": true/false,
            "recommended_action": "brief english text",
            "language": "Gujarati",
            "conversational_response": "The final translated Gujarati message"
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
