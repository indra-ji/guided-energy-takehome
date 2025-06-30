import pytest
from pydantic import ValidationError
from models.requests import AgentRequest, CurrentWeatherParameters, CurrentWeatherRequest
from models.responses import HealthResponse, AgentResponse, CurrentWeatherResponse, CurrentWeatherData, CurrentWeatherUnits


class TestAgentRequest:
    """Test cases for AgentRequest model"""
    
    def test_agent_request_valid(self):
        """Test valid AgentRequest creation"""
        request = AgentRequest(query="What's the weather like?")
        assert request.query == "What's the weather like?"
    
    def test_agent_request_missing_query(self):
        """Test AgentRequest validation error for missing query"""
        with pytest.raises(ValidationError):
            AgentRequest()


class TestCurrentWeatherParameters:
    """Test cases for CurrentWeatherParameters model"""
    
    def test_current_weather_parameters_defaults(self):
        """Test CurrentWeatherParameters with default values"""
        params = CurrentWeatherParameters()
        assert params.temperature_2m is False
        assert params.wind_speed_10m is False
        assert params.precipitation is False
    
    def test_current_weather_parameters_custom(self):
        """Test CurrentWeatherParameters with custom values"""
        params = CurrentWeatherParameters(
            temperature_2m=True,
            wind_speed_10m=True,
            precipitation=True
        )
        assert params.temperature_2m is True
        assert params.wind_speed_10m is True
        assert params.precipitation is True
    
    def test_get_selected_parameters(self):
        """Test get_selected_parameters method"""
        params = CurrentWeatherParameters(
            temperature_2m=True,
            wind_speed_10m=True,
            relative_humidity_2m=False
        )
        selected = params.get_selected_parameters()
        assert "temperature_2m" in selected
        assert "wind_speed_10m" in selected
        assert "relative_humidity_2m" not in selected


class TestCurrentWeatherRequest:
    """Test cases for CurrentWeatherRequest model"""
    
    def test_current_weather_request_minimal(self):
        """Test CurrentWeatherRequest with minimal required fields"""
        request = CurrentWeatherRequest(latitude=37.7749, longitude=-122.4194)
        assert request.latitude == 37.7749
        assert request.longitude == -122.4194
        assert request.temperature_unit == "celsius"  # default
        assert request.wind_speed_unit == "kmh"  # default
    
    def test_current_weather_request_full(self):
        """Test CurrentWeatherRequest with all fields"""
        current_params = CurrentWeatherParameters(temperature_2m=True)
        request = CurrentWeatherRequest(
            latitude=40.7128,
            longitude=-74.0060,
            elevation=100.0,
            current=current_params,
            temperature_unit="fahrenheit",
            wind_speed_unit="mph"
        )
        assert request.latitude == 40.7128
        assert request.longitude == -74.0060
        assert request.elevation == 100.0
        assert request.temperature_unit == "fahrenheit"
        assert request.wind_speed_unit == "mph"
    
    def test_current_weather_request_invalid_coordinates(self):
        """Test CurrentWeatherRequest validation for invalid coordinates"""
        with pytest.raises(ValidationError):
            CurrentWeatherRequest(latitude="invalid", longitude=-122.4194)


class TestHealthResponse:
    """Test cases for HealthResponse model"""
    
    def test_health_response_valid(self):
        """Test valid HealthResponse creation"""
        response = HealthResponse(status="healthy", message="API is running")
        assert response.status == "healthy"
        assert response.message == "API is running"


class TestAgentResponse:
    """Test cases for AgentResponse model"""
    
    def test_agent_response_valid(self):
        """Test valid AgentResponse creation"""
        response = AgentResponse(message="The weather is sunny today.")
        assert response.message == "The weather is sunny today."
    
    def test_agent_response_missing_message(self):
        """Test AgentResponse validation error for missing message"""
        with pytest.raises(ValidationError):
            AgentResponse()


class TestCurrentWeatherResponse:
    """Test cases for CurrentWeatherResponse model"""
    
    def test_current_weather_response_minimal(self):
        """Test CurrentWeatherResponse with minimal required fields"""
        response = CurrentWeatherResponse(
            latitude=37.7749,
            longitude=-122.4194,
            generationtime_ms=1.5,
            utc_offset_seconds=0,
            timezone="GMT",
            timezone_abbreviation="GMT",
            elevation=0.0
        )
        assert response.latitude == 37.7749
        assert response.longitude == -122.4194
        assert response.generationtime_ms == 1.5
        assert response.timezone == "GMT"
    
    def test_current_weather_response_with_data(self):
        """Test CurrentWeatherResponse with weather data"""
        weather_data = CurrentWeatherData(
            time="2024-01-01T12:00:00Z",
            temperature_2m=20.5,
            wind_speed_10m=10.0
        )
        weather_units = CurrentWeatherUnits(
            temperature_2m="°C",
            wind_speed_10m="km/h"
        )
        
        response = CurrentWeatherResponse(
            latitude=37.7749,
            longitude=-122.4194,
            generationtime_ms=1.5,
            utc_offset_seconds=0,
            timezone="GMT",
            timezone_abbreviation="GMT",
            elevation=0.0,
            current=weather_data,
            current_units=weather_units
        )
        
        assert response.current.temperature_2m == 20.5
        assert response.current.wind_speed_10m == 10.0
        assert response.current_units.temperature_2m == "°C" 