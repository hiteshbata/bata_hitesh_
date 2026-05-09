from pydantic import BaseModel, Field
from typing import Optional

class StructuredInsight(BaseModel):
    risk_level: str = Field(description="The risk level of the crop (e.g., low, medium, high)")
    water_stress: bool = Field(description="Whether the crop is experiencing water stress")
    recommended_action: str = Field(description="Actionable advice for the farmer")
    language: str = Field(description="Language of the response, e.g., 'Gujarati' or 'English'")
    conversational_response: str = Field(description="The final friendly, conversational message to send back to the farmer")
    location_detected: Optional[str] = Field(default=None, description="The name of the village or location detected in the user's message, if any.")
    crop_detected: Optional[str] = Field(default=None, description="The name of the crop detected in the user's message, if any.")
    area_detected: Optional[str] = Field(default=None, description="The size or area of the farm detected in the user's message, if any.")
