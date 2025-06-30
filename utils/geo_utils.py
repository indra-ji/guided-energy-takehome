import httpx
import logging
import os
import dotenv
from typing import Tuple

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

def get_location_from_ip() -> Tuple[float, float]:
    """
    Get latitude and longitude from the current public IP address.
    
    Returns:
        Tuple[float, float]: A tuple containing (latitude, longitude)
        
    Raises:
        Exception: If unable to determine location from IP
    """
    logger.info("Starting location determination from IP address")
    
    try:
        with httpx.Client() as client:
            # First, get the public IP address
            logger.debug("Fetching public IP address from ipify.org")
            ip_response = client.get("https://api.ipify.org?format=json", timeout=5.0)
            ip_response.raise_for_status()
            ip_data = ip_response.json()
            public_ip = ip_data.get("ip")
            
            logger.debug(f"IP API response: {ip_data}")
            
            if not public_ip:
                logger.error("Unable to determine public IP address from API response")
                raise Exception("Unable to determine public IP address")
            
            logger.info(f"Public IP address determined: {public_ip}")
            
            # Get geolocation data from the IP
            logger.debug(f"Fetching geolocation data for IP: {public_ip}")
            geo_response = client.get(
                f"https://ipapi.co/{public_ip}/json/",
                timeout=10.0
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            logger.debug(f"Geolocation API response: {geo_data}")
            
            # Check if we got valid coordinates
            latitude = geo_data.get("latitude")
            longitude = geo_data.get("longitude")
            
            if latitude is None or longitude is None:
                logger.error(f"Unable to get coordinates for IP {public_ip}. Latitude: {latitude}, Longitude: {longitude}")
                logger.debug(f"Full geolocation response: {geo_data}")
                raise Exception(f"Unable to get coordinates for IP {public_ip}")
            
            logger.info(f"Location successfully determined: latitude={latitude}, longitude={longitude}")
            logger.debug(f"Additional location data: city={geo_data.get('city')}, region={geo_data.get('region')}, country={geo_data.get('country_name')}")
            
            return float(latitude), float(longitude)
            
    except httpx.TimeoutException as e:
        logger.error(f"Timeout while getting location from IP address: {e}")
        raise Exception("Timeout while getting location from IP address")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while getting location: {e}")
        logger.debug(f"HTTP status code: {e.response.status_code}")
        raise Exception(f"HTTP error while getting location: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting location from IP: {e}")
        raise Exception(f"Error getting location from IP: {e}")
