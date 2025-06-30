import httpx
import logging
import os
import dotenv
from typing import Tuple, Optional

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

def get_location_from_ip(client_ip: Optional[str] = None) -> Tuple[float, float]:
    """
    Get latitude and longitude from an IP address.
    
    Args:
        client_ip: Optional client IP address. If None, will get the current public IP.
        
    Returns:
        Tuple[float, float]: A tuple containing (latitude, longitude)
        
    Raises:
        Exception: If unable to determine location from IP
    """
    logger.info(f"Starting location determination from IP address: {client_ip or 'auto-detect'}")
    
    try:
        with httpx.Client() as client:
            # If no client IP provided, get the public IP address (fallback for server-side usage)
            if client_ip is None:
                logger.debug("No client IP provided, fetching public IP address from ipify.org")
                ip_response = client.get("https://api.ipify.org?format=json", timeout=5.0)
                ip_response.raise_for_status()
                ip_data = ip_response.json()
                public_ip = ip_data.get("ip")
                
                logger.debug(f"IP API response: {ip_data}")
                
                if not public_ip:
                    logger.error("Unable to determine public IP address from API response")
                    raise Exception("Unable to determine public IP address")
                
                logger.info(f"Public IP address determined: {public_ip}")
                target_ip = public_ip
            else:
                logger.info(f"Using provided client IP: {client_ip}")
                target_ip = client_ip
            
            # Get geolocation data from the IP
            logger.debug(f"Fetching geolocation data for IP: {target_ip}")
            geo_response = client.get(
                f"https://ipapi.co/{target_ip}/json/",
                timeout=10.0
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            logger.debug(f"Geolocation API response: {geo_data}")
            
            # Check if we got valid coordinates
            latitude = geo_data.get("latitude")
            longitude = geo_data.get("longitude")
            
            if latitude is None or longitude is None:
                logger.error(f"Unable to get coordinates for IP {target_ip}. Latitude: {latitude}, Longitude: {longitude}")
                logger.debug(f"Full geolocation response: {geo_data}")
                raise Exception(f"Unable to get coordinates for IP {target_ip}")
            
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

def get_client_ip_from_request(request) -> Optional[str]:
    """
    Extract the client's real IP address from FastAPI request.
    Handles various proxy headers to get the real client IP.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Optional[str]: Client IP address or None if cannot be determined
    """
    logger.debug("Extracting client IP from request headers")
    
    # Check common proxy headers in order of preference
    proxy_headers = [
        'X-Forwarded-For',     # Most common
        'X-Real-IP',           # Nginx
        'CF-Connecting-IP',    # Cloudflare
        'X-Forwarded',         # Less common
        'Forwarded-For',       # RFC 7239
        'Forwarded'            # RFC 7239
    ]
    
    for header in proxy_headers:
        if header in request.headers:
            # X-Forwarded-For can contain multiple IPs, take the first one (original client)
            ip_value = request.headers[header].split(',')[0].strip()
            if ip_value:
                logger.debug(f"Client IP found in {header}: {ip_value}")
                return ip_value
    
    # Fallback to direct client IP
    client_ip = request.client.host if request.client else None
    logger.debug(f"Using direct client IP: {client_ip}")
    
    return client_ip
