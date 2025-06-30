import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch
from models.requests import CurrentWeatherRequest, CurrentWeatherParameters
from models.responses import CurrentWeatherResponse, CurrentWeatherData, CurrentWeatherUnits


@pytest.fixture
def sample_weather_request():
    """Fixture providing a sample CurrentWeatherRequest"""
    current_params = CurrentWeatherParameters(
        temperature_2m=True,
        wind_speed_10m=True,
        precipitation=True
    )
    return CurrentWeatherRequest(
        latitude=37.7749,
        longitude=-122.4194,
        current=current_params
    )


@pytest.fixture
def sample_weather_response():
    """Fixture providing a sample CurrentWeatherResponse"""
    weather_data = CurrentWeatherData(
        time="2024-01-01T12:00:00Z",
        temperature_2m=20.5,
        wind_speed_10m=10.0,
        precipitation=0.0
    )
    weather_units = CurrentWeatherUnits(
        temperature_2m="°C",
        wind_speed_10m="km/h",
        precipitation="mm"
    )
    
    return CurrentWeatherResponse(
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


@pytest.fixture
def temp_json_file():
    """Fixture providing a temporary JSON file"""
    test_data = {
        "test_key": "test_value",
        "nested": {
            "key": "value"
        },
        "array": [1, 2, 3]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name
    
    yield temp_path, test_data
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_openai_client():
    """Fixture providing a mocked OpenAI client"""
    with patch('agents.simple_agent.client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_httpx_client():
    """Fixture providing a mocked httpx client"""
    with patch('httpx.AsyncClient') as mock_client:
        yield mock_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Fixture to set up test environment variables"""
    # Set test environment variables
    test_env = {
        'LOG_LEVEL': 'ERROR',  # Suppress logs during testing
        'OPENAI_API_KEY': 'test-key'
    }
    
    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value 