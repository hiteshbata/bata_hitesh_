from pydantic import BaseModel, Field

class StructuredInsight(BaseModel):
    risk_level: str = Field(description="The risk level of the crop (e.g., low, medium, high)")
    water_stress: bool = Field(description="Whether the crop is experiencing water stress")
    recommended_action: str = Field(description="Actionable advice for the farmer")
    language: str = Field(description="Language of the response, e.g., 'Gujarati' or 'English'")
    conversational_response: str = Field(description="The final friendly, conversational message to send back to the farmer")
