import logging
import os
import dotenv
from models.requests import CurrentWeatherRequest, CurrentWeatherParameters
from typing import Dict, Any

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


def build_weather_params(request: CurrentWeatherRequest) -> Dict[str, Any]:
    """
    Build parameters dictionary for OpenMeteo API from CurrentWeatherRequest.
    
    Args:
        request: CurrentWeatherRequest object containing the request parameters
        
    Returns:
        Dictionary of parameters to be sent to the OpenMeteo API
    """
    logger.info("Building weather API parameters from request")
    logger.debug(f"Input request: {request}")
    
    # Build the parameters dictionary
    params = {
        "latitude": request.latitude,
        "longitude": request.longitude,
        **({} if request.elevation is None else {"elevation": request.elevation}),
        **({} if request.current is None or not request.current.get_selected_parameters() else {"current": ",".join(request.current.get_selected_parameters())}),
        **({} if request.temperature_unit == "celsius" else {"temperature_unit": request.temperature_unit}),
        **({} if request.wind_speed_unit == "kmh" else {"wind_speed_unit": request.wind_speed_unit}),
        **({} if request.precipitation_unit == "mm" else {"precipitation_unit": request.precipitation_unit}),
        **({} if request.timeformat == "iso8601" else {"timeformat": request.timeformat}), 
        **({} if request.timezone == "GMT" else {"timezone": request.timezone}),
        **({} if request.models is None or request.models == ["string"] or not request.models else {"models": ",".join(request.models)}),
        **({} if request.cell_selection == "land" else {"cell_selection": request.cell_selection}),
    }
    
    logger.info(f"Weather API parameters built successfully with {len(params)} parameters")
    logger.debug(f"Parameters: {params}")
    
    # Log specific parameter details
    if request.current:
        selected_params = request.current.get_selected_parameters()
        logger.debug(f"Current weather parameters selected: {selected_params}")
    
    logger.debug(f"Location: lat={request.latitude}, lon={request.longitude}")
    logger.debug(f"Units: temp={request.temperature_unit}, wind={request.wind_speed_unit}, precip={request.precipitation_unit}")
    
    return params

def get_weather_parameters_description() -> str:
    """
    Dynamically generate the weather parameters description from the CurrentWeatherParameters model.
    
    Returns:
        str: A formatted string describing all available weather parameters
    """
    logger.debug("Generating weather parameters description from CurrentWeatherParameters model")
    
    # Get the model fields and their descriptions
    parameters = []
    field_count = len(CurrentWeatherParameters.model_fields)
    
    for field_name, field_info in CurrentWeatherParameters.model_fields.items():
        description = field_info.description or "No description available"
        parameters.append(f"{field_name}: {description}")
        logger.debug(f"Added parameter: {field_name}")
    
    description_text = ", ".join(parameters)
    logger.info(f"Weather parameters description generated for {field_count} parameters")
    logger.debug(f"Description length: {len(description_text)} characters")
    
    return description_text

def get_weather_request_parameters_description() -> str:
    """
    Dynamically generate the weather request parameters description from the CurrentWeatherRequest model.
    
    Returns:
        str: A formatted string describing all available request parameters
    """
    logger.debug("Generating weather request parameters description from CurrentWeatherRequest model")
    
    # Get the model fields and their descriptions, excluding current, latitude, longitude
    excluded_fields = {"current", "latitude", "longitude"}
    parameters = []
    total_fields = len(CurrentWeatherRequest.model_fields)
    
    for field_name, field_info in CurrentWeatherRequest.model_fields.items():
        if field_name not in excluded_fields:
            description = field_info.description or "No description available"
            parameters.append(f"{field_name}: {description}")
            logger.debug(f"Added request parameter: {field_name}")
        else:
            logger.debug(f"Excluded parameter: {field_name}")
    
    description_text = ", ".join(parameters)
    included_count = len(parameters)
    excluded_count = len(excluded_fields)
    
    logger.info(f"Weather request parameters description generated: {included_count} included, {excluded_count} excluded from {total_fields} total")
    logger.debug(f"Description length: {len(description_text)} characters")
    
    return description_text
