import pytest
from unittest.mock import patch, Mock
import httpx
from utils.geo_utils import get_location_from_ip


class TestGetLocationFromIp:
    """Test cases for get_location_from_ip function"""
    
    @patch('httpx.Client')
    def test_get_location_from_ip_success(self, mock_client):
        """Test successful location retrieval from IP"""
        # Mock the HTTP client and responses
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock IP response
        ip_response = Mock()
        ip_response.json.return_value = {"ip": "203.0.113.1"}
        ip_response.raise_for_status.return_value = None
        
        # Mock geolocation response
        geo_response = Mock()
        geo_response.json.return_value = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "city": "San Francisco",
            "region": "California",
            "country_name": "United States"
        }
        geo_response.raise_for_status.return_value = None
        
        # Configure the mock to return different responses for different URLs
        mock_client_instance.get.side_effect = [ip_response, geo_response]
        
        result = get_location_from_ip()
        
        assert result == (37.7749, -122.4194)
        assert mock_client_instance.get.call_count == 2
    
    @patch('httpx.Client')
    def test_get_location_from_ip_no_public_ip(self, mock_client):
        """Test exception when IP API returns no IP"""
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        ip_response = Mock()
        ip_response.json.return_value = {}  # No IP in response
        ip_response.raise_for_status.return_value = None
        
        mock_client_instance.get.return_value = ip_response
        
        with pytest.raises(Exception, match="Unable to determine public IP address"):
            get_location_from_ip()
    
    @patch('httpx.Client')
    def test_get_location_from_ip_no_coordinates(self, mock_client):
        """Test exception when geolocation API returns no coordinates"""
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        ip_response = Mock()
        ip_response.json.return_value = {"ip": "203.0.113.1"}
        ip_response.raise_for_status.return_value = None
        
        geo_response = Mock()
        geo_response.json.return_value = {"city": "Unknown"}  # No coordinates
        geo_response.raise_for_status.return_value = None
        
        mock_client_instance.get.side_effect = [ip_response, geo_response]
        
        with pytest.raises(Exception, match="Unable to get coordinates"):
            get_location_from_ip()
    
    @patch('httpx.Client')
    def test_get_location_from_ip_timeout(self, mock_client):
        """Test timeout exception handling"""
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(Exception, match="Timeout while getting location from IP address"):
            get_location_from_ip()
    
    @patch('httpx.Client')
    def test_get_location_from_ip_http_error(self, mock_client):
        """Test HTTP error exception handling"""
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Create a mock response for the HTTPStatusError
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_client_instance.get.side_effect = httpx.HTTPStatusError(
            "Not found", request=Mock(), response=mock_response
        )
        
        with pytest.raises(Exception, match="HTTP error while getting location"):
            get_location_from_ip() 