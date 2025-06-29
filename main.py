from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import dotenv
import httpx

from models.responses import HealthResponse, AgentResponse, CurrentWeatherResponse
from models.requests import CurrentWeatherRequest

dotenv.load_dotenv()

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


@app.get("/weather/current", response_model=CurrentWeatherResponse)
async def get_current_weather(request: CurrentWeatherRequest = Depends()):
    """
    Get current weather information for a given location using OpenMeteo API.
    """
    
    # Weather.com Current Conditions API endpoint
    base_url = "https://api.weather.com"
    api_url = "/v3/wx/observations/current"
    url = f"{base_url}{api_url}"
    
    params = {
        "geocode": request.geocode,
        "units": request.units,
        "language": request.language,
        "format": request.format,
        "apikey": request.apiKey
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            # The API returns an array with one observation object
            if not weather_data or len(weather_data) == 0:
                raise HTTPException(status_code=404, detail="No weather data found for the specified location")
            
            obs = weather_data[0]  # Get the first (and only) observation
            
            # Map the API response to your CurrentWeatherResponse model
            return CurrentWeatherResponse(
                cloud_ceiling=obs.get("cloudCeiling"),
                cloud_cover_phrase=obs["cloudCoverPhrase"],
                day_of_week=obs["dayOfWeek"],
                day_or_night=obs["dayOrNight"],
                expiration_time_utc=obs["expirationTimeUtc"],
                icon_code=obs["iconCode"],
                icon_code_extend=obs["iconCodeExtend"],
                obs_qualifier_code=obs.get("obsQualifierCode"),
                obs_qualifier_severity=obs.get("obsQualifierSeverity"),
                precip_1_hour=obs.get("precip1Hour"),
                precip_6_hour=obs.get("precip6Hour"),
                precip_24_hour=obs.get("precip24Hour"),
                pressure_altimeter=obs.get("pressureAltimeter"),
                pressure_change=obs["pressureChange"],
                pressure_mean_sea_level=obs["pressureMeanSeaLevel"],
                pressure_tendency_code=obs["pressureTendencyCode"],
                pressure_tendency_trend=obs["pressureTendencyTrend"],
                relative_humidity=obs["relativeHumidity"],
                snow_1_hour=obs.get("snow1Hour"),
                snow_6_hour=obs.get("snow6Hour"),
                snow_24_hour=obs.get("snow24Hour"),
                sunrise_time_local=obs.get("sunriseTimeLocal"),
                sunrise_time_utc=obs.get("sunriseTimeUtc"),
                sunset_time_local=obs.get("sunsetTimeLocal"),
                sunset_time_utc=obs.get("sunsetTimeUtc"),
                temperature=obs["temperature"],
                temperature_change_24_hour=obs["temperatureChange24Hour"],
                temperature_dew_point=obs["temperatureDewPoint"],
                temperature_feels_like=obs["temperatureFeelsLike"],
                temperature_heat_index=obs["temperatureHeatIndex"],
                temperature_max_24_hour=obs["temperatureMax24Hour"],
                temperature_max_since_7_am=obs["temperatureMaxSince7Am"],
                temperature_min_24_hour=obs["temperatureMin24Hour"],
                temperature_wind_chill=obs["temperatureWindChill"],
                uv_description=obs.get("uvDescription"),
                uv_index=obs.get("uvIndex"),
                valid_time_local=obs["validTimeLocal"],
                valid_time_utc=obs["validTimeUtc"],
                visibility=obs["visibility"],
                wind_direction=obs["windDirection"],
                wind_direction_cardinal=obs["windDirectionCardinal"],
                wind_gust=obs.get("windGust"),
                wind_speed=obs["windSpeed"],
                wx_phrase_long=obs["wxPhraseShort"],
                wx_phrase_medium=obs.get("wxPhraseMedium"),
                wx_phrase_short=obs.get("wxPhraseShort")
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise HTTPException(status_code=400, detail="Invalid request parameters")
            elif e.response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid API key")
            elif e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Location not found")
            else:
                raise HTTPException(status_code=e.response.status_code, detail=f"Weather API error: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Unable to connect to weather service: {str(e)}")
        except KeyError as e:
            raise HTTPException(status_code=502, detail=f"Unexpected response format from weather API: missing field {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/simple_weather_agent", response_model=AgentResponse)
async def simple_weather_agent():
    """
    A simple weather agent that uses the weather API to get the weather for a given location.
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
