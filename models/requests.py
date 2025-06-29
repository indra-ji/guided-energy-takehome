from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class AgentRequest(BaseModel):
    """Request model for agent"""

    query: str = Field(..., description="The user query to answer")


class CurrentWeatherParameters(BaseModel):
    """Available current weather parameters for Open-Meteo API. Every parameter for current weather also works for hourly weather."""

    # Temperature parameters
    temperature_2m: Optional[bool] = Field(False, description="Air temperature at 2 meters above ground")
    relative_humidity_2m: Optional[bool] = Field(False, description="Relative humidity at 2 meters above ground")
    dew_point_2m: Optional[bool] = Field(False, description="Dew point temperature at 2 meters above ground")
    apparent_temperature: Optional[bool] = Field(False, description="Apparent temperature is the perceived feels-like temperature combining wind chill factor, relative humidity and solar radiation")
    
    # Pressure parameters
    pressure_msl: Optional[bool] = Field(False, description="Atmospheric air pressure reduced to mean sea level (msl)")
    surface_pressure: Optional[bool] = Field(False, description="Atmospheric air pressure at surface. Surface pressure gets lower with increasing elevation")
    
    # Cloud cover parameters
    cloud_cover: Optional[bool] = Field(False, description="Total cloud cover as an area fraction")
    cloud_cover_low: Optional[bool] = Field(False, description="Low level clouds and fog up to 3 km altitude")
    cloud_cover_mid: Optional[bool] = Field(False, description="Mid level clouds from 3 to 8 km altitude")
    cloud_cover_high: Optional[bool] = Field(False, description="High level clouds from 8 km altitude")
    
    # Wind parameters
    wind_speed_10m: Optional[bool] = Field(False, description="Wind speed at 10 meters above ground. Wind speed on 10 meters is the standard level")
    wind_speed_80m: Optional[bool] = Field(False, description="Wind speed at 80 meters above ground")
    wind_speed_120m: Optional[bool] = Field(False, description="Wind speed at 120 meters above ground")
    wind_speed_180m: Optional[bool] = Field(False, description="Wind speed at 180 meters above ground")
    wind_direction_10m: Optional[bool] = Field(False, description="Wind direction at 10 meters above ground")
    wind_direction_80m: Optional[bool] = Field(False, description="Wind direction at 80 meters above ground")
    wind_direction_120m: Optional[bool] = Field(False, description="Wind direction at 120 meters above ground")
    wind_direction_180m: Optional[bool] = Field(False, description="Wind direction at 180 meters above ground")
    wind_gusts_10m: Optional[bool] = Field(False, description="Gusts at 10 meters above ground as a maximum of the preceding hour")
    
    # Solar radiation parameters
    shortwave_radiation: Optional[bool] = Field(False, description="Shortwave solar radiation as average of the preceding hour. This is equal to the total global horizontal irradiation")
    direct_radiation: Optional[bool] = Field(False, description="Direct solar radiation as average of the preceding hour on the horizontal plane")
    direct_normal_irradiance: Optional[bool] = Field(False, description="Direct solar radiation as average of the preceding hour on the normal plane (perpendicular to the sun)")
    diffuse_radiation: Optional[bool] = Field(False, description="Diffuse solar radiation as average of the preceding hour")
    global_tilted_irradiance: Optional[bool] = Field(False, description="Total radiation received on a tilted pane as average of the preceding hour")
    
    # Atmospheric parameters
    vapour_pressure_deficit: Optional[bool] = Field(False, description="Vapour Pressure Deficit (VPD) in kilopascal (kPa). For high VPD (>1.6), water transpiration of plants increases. For low VPD (<0.4), transpiration decreases")
    cape: Optional[bool] = Field(False, description="Convective available potential energy")
    
    # Evapotranspiration parameters
    evapotranspiration: Optional[bool] = Field(False, description="Evapotranspration from land surface and plants that weather models assumes for this location. Available soil water is considered")
    et0_fao_evapotranspiration: Optional[bool] = Field(False, description="ET₀ Reference Evapotranspiration of a well watered grass field. Based on FAO-56 Penman-Monteith equations")
    
    # Precipitation parameters
    precipitation: Optional[bool] = Field(False, description="Total precipitation (rain, showers, snow) sum of the preceding hour")
    snowfall: Optional[bool] = Field(False, description="Snowfall amount of the preceding hour in centimeters. For the water equivalent in millimeter, divide by 7")
    precipitation_probability: Optional[bool] = Field(False, description="Probability of precipitation with more than 0.1 mm of the preceding hour")
    rain: Optional[bool] = Field(False, description="Rain from large scale weather systems of the preceding hour in millimeter")
    showers: Optional[bool] = Field(False, description="Showers from convective precipitation in millimeters from the preceding hour")
    
    # Weather condition and environment
    weather_code: Optional[bool] = Field(False, description="Weather condition as a numeric code. Follow WMO weather interpretation codes")
    snow_depth: Optional[bool] = Field(False, description="Snow depth on the ground")
    freezing_level_height: Optional[bool] = Field(False, description="Altitude above sea level of the 0°C level")
    visibility: Optional[bool] = Field(False, description="Viewing distance in meters. Influenced by low clouds, humidity and aerosols")
    
    # Soil temperature parameters
    soil_temperature_0cm: Optional[bool] = Field(False, description="Temperature in the soil at 0 cm depth. 0 cm is the surface temperature on land or water surface temperature on water")
    soil_temperature_6cm: Optional[bool] = Field(False, description="Temperature in the soil at 6 cm depth")
    soil_temperature_18cm: Optional[bool] = Field(False, description="Temperature in the soil at 18 cm depth")
    soil_temperature_54cm: Optional[bool] = Field(False, description="Temperature in the soil at 54 cm depth")
    
    # Soil moisture parameters
    soil_moisture_0_to_1cm: Optional[bool] = Field(False, description="Average soil water content as volumetric mixing ratio at 0-1 cm depth")
    soil_moisture_1_to_3cm: Optional[bool] = Field(False, description="Average soil water content as volumetric mixing ratio at 1-3 cm depth")
    soil_moisture_3_to_9cm: Optional[bool] = Field(False, description="Average soil water content as volumetric mixing ratio at 3-9 cm depth")
    soil_moisture_9_to_27cm: Optional[bool] = Field(False, description="Average soil water content as volumetric mixing ratio at 9-27 cm depth")
    soil_moisture_27_to_81cm: Optional[bool] = Field(False, description="Average soil water content as volumetric mixing ratio at 27-81 cm depth")
    
    # Day/night indicator
    is_day: Optional[bool] = Field(False, description="1 if the current time step has daylight, 0 at night")
    
    def get_selected_parameters(self) -> List[str]:
        """Returns a list of selected parameter names for API request"""
        return [field_name for field_name, value in self.__dict__.items() if value is True]

class CurrentWeatherRequest(BaseModel):
    """Request model for forecasted weather data using the new API provider"""
    
    latitude: float = Field(..., description="Geographical WGS84 coordinate of the location (latitude). Multiple coordinates can be comma separated.")
    longitude: float = Field(..., description="Geographical WGS84 coordinate of the location (longitude). Multiple coordinates can be comma separated.")
    elevation: Optional[float] = Field(None, description="The elevation used for statistical downscaling. Per default, a 90 meter digital elevation model is used. You can manually set the elevation to correctly match mountain peaks. If elevation=nan is specified, downscaling will be disabled and the API uses the average grid-cell height. For multiple locations, elevation can also be comma separated.")
    current: Optional[CurrentWeatherParameters] = Field(None, description="A list of weather variables to get current conditions.")
    temperature_unit: Optional[Literal["celsius", "fahrenheit"]] = Field("celsius", description="If fahrenheit is set, all temperature values are converted to Fahrenheit.")
    wind_speed_unit: Optional[Literal["kmh", "ms", "mph", "kn"]] = Field("kmh", description="Wind speed units: kmh (default), ms, mph and kn")
    precipitation_unit: Optional[Literal["mm", "inch"]] = Field("mm", description="Precipitation amount units: mm (default) or inch")
    timeformat: Optional[Literal["iso8601", "unixtime"]] = Field("iso8601", description="If format unixtime is selected, all time values are returned in UNIX epoch time in seconds. Please note that all timestamp are in GMT+0! For daily values with unix timestamps, please apply utc_offset_seconds again to get the correct date.")
    timezone: Optional[str] = Field("GMT", description="If timezone is set, all timestamps are returned as local-time and data is returned starting at 00:00 local-time. Any time zone name from the time zone database is supported. If auto is set as a time zone, the coordinates will be automatically resolved to the local time zone. For multiple coordinates, a comma separated list of timezones can be specified.")
    models: Optional[List[str]] = Field(None, description="Manually select one or more weather models. Per default, the best suitable weather models will be combined.")
    cell_selection: Optional[Literal["land", "sea", "nearest"]] = Field("land", description="Set a preference how grid-cells are selected. The default land finds a suitable grid-cell on land with similar elevation to the requested coordinates using a 90-meter digital elevation model. sea prefers grid-cells on sea. nearest selects the nearest possible grid-cell.")

