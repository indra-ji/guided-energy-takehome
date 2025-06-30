from models.requests import CurrentWeatherRequest
from typing import Dict, Any


def build_openmeteo_params(request: CurrentWeatherRequest) -> Dict[str, Any]:
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
