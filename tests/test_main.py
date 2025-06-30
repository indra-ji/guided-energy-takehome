import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app


class TestMainEndpoints:
    """Test cases for main FastAPI endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Simple Weather Agent API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "Weather Agents API is running"
    
    @patch('main.get_current_weather')
    def test_current_weather_endpoint(self, mock_get_weather):
        """Test current weather endpoint with mocked response"""
        # Mock the weather response
        mock_weather_response = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "generationtime_ms": 1.5,
            "utc_offset_seconds": 0,
            "timezone": "GMT",
            "timezone_abbreviation": "GMT",
            "elevation": 0.0
        }
        mock_get_weather.return_value = mock_weather_response
        
        response = self.client.post("/weather/current", params={
            "latitude": 37.7749,
            "longitude": -122.4194
        })
        
        assert response.status_code == 200
        # Note: This test would need more setup to work with the actual endpoint
        # since it involves async operations and external API calls
    
    @patch('main.classify_weather_query')
    @patch('main.get_current_weather')
    def test_simple_weather_agent_endpoint_non_weather(self, mock_get_weather, mock_classify):
        """Test simple weather agent endpoint with non-weather query"""
        # Mock classification to return False (not a weather query)
        mock_classify.return_value = False
        
        response = self.client.post("/simple_weather_agent", json={
            "query": "What's the capital of France?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "I'm sorry, I can only answer questions about the weather" in data["message"]
        
        # Should not call weather API for non-weather queries
        mock_get_weather.assert_not_called()
    
    def test_simple_weather_agent_endpoint_missing_query(self):
        """Test simple weather agent endpoint with missing query"""
        response = self.client.post("/simple_weather_agent", json={})
        
        assert response.status_code == 422  # Validation error 