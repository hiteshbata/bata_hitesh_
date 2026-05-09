import google.generativeai as genai
import json
from app.core.config import settings
from app.schemas.ai import StructuredInsight

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash',
            system_instruction="You are an expert agricultural AI. Always return valid JSON matching the exact schema requested.")

    def generate_insight(self, system_prompt: str) -> StructuredInsight:
        try:
            response = self.model.generate_content(
                system_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            text = response.text
            data = json.loads(text)
            return StructuredInsight(**data)

        except Exception as e:
            print(f"Gemini AI Error: {e}")
            return StructuredInsight(
                risk_level="unknown",
                water_stress=False,
                recommended_action="Unable to analyze at this moment.",
                language="English",
                conversational_response="I'm sorry, I couldn't process your request right now. Please try again later."
            )
