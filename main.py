from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import httpx
import logging
import os
import dotenv

from models.responses import HealthResponse, AgentResponse, CurrentWeatherResponse
from models.requests import CurrentWeatherRequest, AgentRequest
from agents.simple_agent import classify_weather_query, generate_weather_request, answer_weather_query
from utils.request_utils import build_weather_params

# Load environment variables
dotenv.load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with custom metadata for Swagger
app = FastAPI(
    title="Weather Agents",
    description="A weather agent API that provides weather information and related services, using OpenMeteo. Exposes both the agent endpoints and the weather API endpoints.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

logger.info(f"FastAPI application initialized with log level: {log_level}")

@app.get("/", response_model=dict)
async def root():
    """
    Root endpoint - API information
    """
    logger.info("Root endpoint accessed")
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
    logger.info("Health check endpoint accessed")
    response = HealthResponse(
        status="healthy",
        message="Weather Agents API is running"
    )
    logger.debug(f"Health check response: {response}")
    return response


@app.post("/weather/current", response_model=CurrentWeatherResponse)
async def get_current_weather(request: CurrentWeatherRequest = Depends()):
    """
    Get current weather information for a given location using OpenMeteo API.
    """
    logger.info(f"Current weather endpoint accessed for location: lat={request.latitude}, lon={request.longitude}")
    logger.debug(f"Weather request parameters: {request}")
    
    # Weather.com Current Conditions API endpoint
    base_url = "https://api.open-meteo.com"
    api_url = "/v1/forecast"
    url = f"{base_url}{api_url}"
    
    logger.debug(f"OpenMeteo API URL: {url}")
    
    # Build params dictionary using utility function
    params = build_weather_params(request)
    logger.debug(f"API parameters: {params}")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.debug("Making HTTP request to OpenMeteo API")
            response = await client.get(url, params=params)
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"OpenMeteo API response status: {response.status_code}")
            logger.debug(f"OpenMeteo API response data size: {len(str(response_data))} characters")

            # Parse the response data into CurrentWeatherResponse
            parsed_response = CurrentWeatherResponse(**response_data)
            logger.info("Weather data successfully retrieved and parsed")
            logger.debug(f"Parsed weather response: {parsed_response}")
            
            return parsed_response
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching weather data: {e}")
            logger.debug(f"Failed request URL: {url}")
            logger.debug(f"Failed request params: {params}")
            raise HTTPException(status_code=500, detail=f"HTTP error occurred: {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching weather data: {e}")
            logger.debug(f"Failed request URL: {url}")
            logger.debug(f"Failed request params: {params}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/simple_weather_agent", response_model=AgentResponse)
async def simple_weather_agent(request: AgentRequest):
    """
    A simple weather agent that uses the weather API to get the weather for the current location.
    """
    logger.info(f"Simple weather agent endpoint accessed with query: '{request.query}'")
    
    try:
        # Classify whether the query is within scope
        logger.debug("Starting query classification")
        is_weather_query = classify_weather_query(request.query)
        logger.info(f"Query classification result: {is_weather_query}")

        # If the query is not about weather, return a message
        if not is_weather_query:
            logger.info("Query is not weather-related, returning scope limitation message")
            response = AgentResponse(message="I'm sorry, I can only answer questions about the weather at your current time and location.")
            return response

        # Generate weather request for weather-related queries using LLM
        logger.debug("Generating weather request from query")
        weather_request = generate_weather_request(request.query)
        logger.info("Weather request generated successfully")

        # Get the current weather from the weather API 
        logger.debug("Fetching current weather data")
        current_weather_response = await get_current_weather(weather_request)
        logger.info("Current weather data retrieved successfully")

        # Answer the weather query using LLM and the weather data
        logger.debug("Generating natural language answer")
        answer = answer_weather_query(current_weather_response, request.query)
        logger.info(f"Weather answer generated successfully, length: {len(answer)} characters")

        # Return the agent response
        agent_response = AgentResponse(message=answer)
        logger.debug(f"Agent response: {agent_response}")
        
        return agent_response
    
    except Exception as e:
        logger.error(f"Error in simple weather agent: {e}")
        logger.debug(f"Failed query: '{request.query}'")
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")



def main():
    """
    Run the FastAPI application
    """
    logger.info("Starting FastAPI application")
    logger.debug("Running on host=0.0.0.0, port=8000, reload=True")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
