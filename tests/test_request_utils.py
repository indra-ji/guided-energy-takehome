import pytest
from models.requests import CurrentWeatherRequest, CurrentWeatherParameters
from utils.request_utils import build_weather_params, get_weather_parameters_description, get_weather_request_parameters_description


class TestBuildWeatherParams:
    """Test cases for build_weather_params function"""
    
    def test_build_weather_params_minimal(self):
        """Test building parameters with minimal required fields"""
        current_params = CurrentWeatherParameters(temperature_2m=True)
        request = CurrentWeatherRequest(
            latitude=37.7749,
            longitude=-122.4194,
            current=current_params
        )
        
        result = build_weather_params(request)
        
        assert result["latitude"] == 37.7749
        assert result["longitude"] == -122.4194
        assert result["current"] == "temperature_2m"
        assert "elevation" not in result  # Should not include None values
    
    def test_build_weather_params_with_elevation(self):
        """Test building parameters with elevation"""
        current_params = CurrentWeatherParameters(temperature_2m=True, wind_speed_10m=True)
        request = CurrentWeatherRequest(
            latitude=40.7128,
            longitude=-74.0060,
            elevation=100.0,
            current=current_params
        )
        
        result = build_weather_params(request)
        
        assert result["latitude"] == 40.7128
        assert result["longitude"] == -74.0060
        assert result["elevation"] == 100.0
        assert "temperature_2m,wind_speed_10m" == result["current"]
    
    def test_build_weather_params_custom_units(self):
        """Test building parameters with custom units"""
        current_params = CurrentWeatherParameters(temperature_2m=True)
        request = CurrentWeatherRequest(
            latitude=51.5074,
            longitude=-0.1278,
            current=current_params,
            temperature_unit="fahrenheit",
            wind_speed_unit="mph",
            precipitation_unit="inch"
        )
        
        result = build_weather_params(request)
        
        assert result["temperature_unit"] == "fahrenheit"
        assert result["wind_speed_unit"] == "mph"
        assert result["precipitation_unit"] == "inch"
    
    def test_build_weather_params_no_current(self):
        """Test building parameters without current weather parameters"""
        request = CurrentWeatherRequest(
            latitude=48.8566,
            longitude=2.3522
        )
        
        result = build_weather_params(request)
        
        assert result["latitude"] == 48.8566
        assert result["longitude"] == 2.3522
        assert "current" not in result


class TestParameterDescriptions:
    """Test cases for parameter description functions"""
    
    def test_get_weather_parameters_description(self):
        """Test weather parameters description generation"""
        result = get_weather_parameters_description()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "temperature_2m" in result
        assert "wind_speed_10m" in result
    
    def test_get_weather_request_parameters_description(self):
        """Test weather request parameters description generation"""
        result = get_weather_request_parameters_description()
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should include these parameters
        assert "elevation" in result
        assert "temperature_unit" in result
        # Should exclude these parameters
        assert "current" not in result
        assert "latitude" not in result
        assert "longitude" not in result 