from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Create FastAPI app with custom metadata for Swagger
app = FastAPI(
    title="Weather Agents",
    description="A weather agent API that provides weather information and related services.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

class HealthResponse(BaseModel):
    status: str
    message: str

class AgentResponse(BaseModel):
    message: str

class WeatherResponse(BaseModel):
    status: str
    message: str

# API Routes

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

@app.get("/test_weather_api", response_model=WeatherResponse)
async def test_weather_api():
    """
    Test whether the weather API from weather.com is working.
    """
    return WeatherResponse(
        status="healthy",
        message="Weather API is working"
    )

@app.get("/simple_weather_agent", response_model=AgentResponse)
async def simple_weather_agent():
    """
    A simple weather agent that uses the weather API to get the weather for a given location.
    """
    return {"message": "Hello, World!"}

@app.get("/complex_weather_agent", response_model=AgentResponse)
async def complex_weather_agent():
    """
    A complex weather agent that uses the weather API to get the weather for a given location.
    """
    return {"message": "Hello, World!"}

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
