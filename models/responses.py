from pydantic import BaseModel
from models.requests import CurrentWeatherParameters

class HealthResponse(BaseModel):
    status: str
    message: str


class AgentResponse(BaseModel):
    message: str


# New OpenMeteo API response models
class CurrentWeatherResponse(BaseModel):
    """Response model for current weather data using OpenMeteo API"""
    
    latitude: float
    longitude: float
    elevation: float
    current: CurrentWeatherParameters


