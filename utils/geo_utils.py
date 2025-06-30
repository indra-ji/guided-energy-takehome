import httpx
from typing import Tuple

def get_location_from_ip() -> Tuple[float, float]:
    """
    Get latitude and longitude from the current public IP address.
    
    Returns:
        Tuple[float, float]: A tuple containing (latitude, longitude)
        
    Raises:
        Exception: If unable to determine location from IP
    """
    try:
        with httpx.Client() as client:
            # First, get the public IP address
            ip_response = client.get("https://api.ipify.org?format=json", timeout=5.0)
            ip_response.raise_for_status()
            ip_data = ip_response.json()
            public_ip = ip_data.get("ip")
            
            if not public_ip:
                raise Exception("Unable to determine public IP address")
            
            # Get geolocation data from the IP
            geo_response = client.get(
                f"https://ipapi.co/{public_ip}/json/",
                timeout=10.0
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            # Check if we got valid coordinates
            latitude = geo_data.get("latitude")
            longitude = geo_data.get("longitude")
            
            if latitude is None or longitude is None:
                raise Exception(f"Unable to get coordinates for IP {public_ip}")
            
            return float(latitude), float(longitude)
            
    except httpx.TimeoutException:
        raise Exception("Timeout while getting location from IP address")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error while getting location: {e}")
    except Exception as e:
        raise Exception(f"Error getting location from IP: {e}")
