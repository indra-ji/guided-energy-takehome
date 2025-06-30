from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import httpx

from models.responses import HealthResponse, AgentResponse, CurrentWeatherResponse
from models.requests import CurrentWeatherRequest, AgentRequest
from agents.simple_agent import classify_weather_query, generate_weather_request, answer_weather_query
from utils.request_utils import build_openmeteo_params


# Create FastAPI app with custom metadata for Swagger
app = FastAPI(
    title="Weather Agents",
    description="A weather agent API that provides weather information and related services, using OpenMeteo. Exposes both the agent endpoints and the weather API endpoints.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

@app.get("/", response_model=dict)
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Welcome to Simple Weather Agent API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        message="Weather Agents API is running"
    )


@app.post("/weather/current", response_model=CurrentWeatherResponse)
async def get_current_weather(request: CurrentWeatherRequest = Depends()):
    """
    Get current weather information for a given location using OpenMeteo API.
    """
    
    # Weather.com Current Conditions API endpoint
    base_url = "https://api.open-meteo.com"
    api_url = "/v1/forecast"
    url = f"{base_url}{api_url}"
    
    # Build params dictionary using utility function
    params = build_openmeteo_params(request)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            response_data = response.json()

            # Parse the response data into CurrentWeatherResponse
            parsed_response = CurrentWeatherResponse(**response_data)
            
            return parsed_response
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"HTTP error occurred: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/simple_weather_agent", response_model=AgentResponse)
async def simple_weather_agent(request: AgentRequest):
    """
    A simple weather agent that uses the weather API to get the weather for the current location.
    """

    # Classify whether the query is within scope
    is_weather_query = classify_weather_query(request.query)

    # If the query is not about weather, return a message
    if not is_weather_query:
        return AgentResponse(message="I'm sorry, I can only answer questions about the weather at your current time and location.")

    # Generate weather request for weather-related queries
    weather_request = generate_weather_request(request.query)

    # Get the current weather
    current_weather_response = await get_current_weather(weather_request)

    # Answer the weather query
    answer = answer_weather_query(current_weather_response, request.query)

    # Return the agent response
    agent_response = AgentResponse(message=answer)

    return agent_response



def main():
    """
    Run the FastAPI application
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
