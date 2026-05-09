class PromptService:
    def get_latest_prompt(self, prompt_type: str) -> str:
        return ("You are an expert agricultural AI for Indian farmers. "
            "Farmer context: {farmer_context}. Weather: {weather_data}. "
            "NDVI: {ndvi_data}. Farmer says: {user_message}. Respond in Gujarati with JSON.")
