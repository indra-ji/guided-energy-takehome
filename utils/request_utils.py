from models.requests import CurrentWeatherRequest, CurrentWeatherParameters
from typing import Dict, Any


def build_weather_params(request: CurrentWeatherRequest) -> Dict[str, Any]:
    """
    Build parameters dictionary for OpenMeteo API from CurrentWeatherRequest.
    
    Args:
        request: CurrentWeatherRequest object containing the request parameters
        
    Returns:
        Dictionary of parameters to be sent to the OpenMeteo API
    """
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
    
    return params

def get_weather_parameters_description() -> str:
    """
    Dynamically generate the weather parameters description from the CurrentWeatherParameters model.
    
    Returns:
        str: A formatted string describing all available weather parameters
    """
    # Get the model fields and their descriptions
    parameters = []
    for field_name, field_info in CurrentWeatherParameters.model_fields.items():
        description = field_info.description or "No description available"
        parameters.append(f"{field_name}: {description}")
    
    return ", ".join(parameters)

def get_weather_request_parameters_description() -> str:
    """
    Dynamically generate the weather request parameters description from the CurrentWeatherRequest model.
    
    Returns:
        str: A formatted string describing all available request parameters
    """
    # Get the model fields and their descriptions, excluding current, latitude, longitude
    excluded_fields = {"current", "latitude", "longitude"}
    parameters = []
    
    for field_name, field_info in CurrentWeatherRequest.model_fields.items():
        if field_name not in excluded_fields:
            description = field_info.description or "No description available"
            parameters.append(f"{field_name}: {description}")
    
    return ", ".join(parameters)
