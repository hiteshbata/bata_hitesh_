from pydantic import BaseModel
class StructuredInsight(BaseModel):
    risk_level: str = "low"
    water_stress: bool = False
    recommended_action: str = ""
    language: str = "English"
    conversational_response: str = ""
