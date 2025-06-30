import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from agents.simple_agent import classify_weather_query


class TestClassifyWeatherQuery:
    """Test cases for classify_weather_query function"""
    
    @patch('agents.simple_agent.load_json')
    @patch('agents.simple_agent.client')
    def test_classify_weather_query_positive(self, mock_client, mock_load_json):
        """Test classification of weather-related query"""
        # Mock configuration and prompts
        mock_load_json.side_effect = [
            {"weather_classification": {"system": "Test prompt"}},  # prompts
            {"openai": {"weather_classification": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 100,
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }}}  # config
        ]
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"is_weather_query": true}'
        mock_client.chat.completions.create.return_value = mock_response
        
        result = classify_weather_query("What's the weather like today?")
        
        assert result is True
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('agents.simple_agent.load_json')
    @patch('agents.simple_agent.client')
    def test_classify_weather_query_negative(self, mock_client, mock_load_json):
        """Test classification of non-weather query"""
        # Mock configuration and prompts
        mock_load_json.side_effect = [
            {"weather_classification": {"system": "Test prompt"}},  # prompts
            {"openai": {"weather_classification": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 100,
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }}}  # config
        ]
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"is_weather_query": false}'
        mock_client.chat.completions.create.return_value = mock_response
        
        result = classify_weather_query("What's the capital of France?")
        
        assert result is False
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('agents.simple_agent.load_json')
    @patch('agents.simple_agent.client')
    def test_classify_weather_query_api_error(self, mock_client, mock_load_json):
        """Test classification when OpenAI API fails"""
        # Mock configuration and prompts
        mock_load_json.side_effect = [
            {"weather_classification": {"system": "Test prompt"}},  # prompts
            {"openai": {"weather_classification": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 100,
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }}}  # config
        ]
        
        # Mock OpenAI API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = classify_weather_query("What's the weather like?")
        
        # Should return False on API error
        assert result is False
    
    @patch('agents.simple_agent.load_json')
    @patch('agents.simple_agent.client')
    def test_classify_weather_query_invalid_json_response(self, mock_client, mock_load_json):
        """Test classification with invalid JSON response"""
        # Mock configuration and prompts
        mock_load_json.side_effect = [
            {"weather_classification": {"system": "Test prompt"}},  # prompts
            {"openai": {"weather_classification": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 100,
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }}}  # config
        ]
        
        # Mock OpenAI response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'invalid json'
        mock_client.chat.completions.create.return_value = mock_response
        
        result = classify_weather_query("What's the weather like?")
        
        # Should return False on JSON parsing error
        assert result is False 