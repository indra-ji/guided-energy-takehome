from openai import OpenAI
import os
import json
import dotenv
import logging
from models.requests import CurrentWeatherParameters, CurrentWeatherRequest
from models.responses import CurrentWeatherResponse
from utils.json_utils import load_json, ensure_strict_schema
from utils.geo_utils import get_location_from_ip, get_lat_lon_from_location
from utils.request_utils import get_weather_parameters_description, get_weather_request_parameters_description
from typing import Optional

dotenv.load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

logger.info(f"Simple agent initialized with log level: {log_level}")

def classify_weather_query(query: str) -> bool:
    """
    Classify if a query is related to current weather in current location.
    
    Args:
        query (str): The input query to classify
        
    Returns:
        bool: True if the query is related to current weather in current location, False otherwise
    """
    logger.info(f"Starting weather query classification for query: '{query}'")
    
    try:
        # Load prompts and config
        logger.debug("Loading prompts and configuration files")
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Get configuration for weather classification
        openai_config = config["openai"]["weather_classification"]
        weather_prompt = prompts["weather_classification"]["system"]
        
        logger.debug(f"Using OpenAI model: {openai_config['model']}")
        logger.debug(f"Classification prompt loaded, length: {len(weather_prompt)} characters")
        
        response = client.chat.completions.create(
            model=openai_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": weather_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=openai_config["max_tokens"],
            temperature=openai_config["temperature"],
            response_format=openai_config["response_format"]
        )
        
        logger.debug("OpenAI API call completed successfully for classification")
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content.strip())
        is_weather_query = result.get("is_weather_query", False)
        
        logger.info(f"Query classification result: {is_weather_query}")
        logger.debug(f"Full classification response: {result}")
        
        return is_weather_query
        
    except Exception as e:
        # In case of API error, default to False
        logger.error(f"Error classifying query: {e}")
        logger.debug(f"Query that failed classification: '{query}'")
        return False
    
def classify_weather_query_location(query: str) -> bool:
    """
    Classify if a query is related to current weather in a given location or set of locations..
    
    Args:
        query (str): The input query to classify
        
    Returns:
        bool: True if the query is related to current weather in current location, False otherwise
    """
    
    try:
        # Load prompts and config
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Get configuration for weather classification
        openai_config = config["openai"]["weather_classification"]
        weather_prompt = prompts["weather_classification_location"]["system"]
        
        response = client.chat.completions.create(
            model=openai_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": weather_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=openai_config["max_tokens"],
            temperature=openai_config["temperature"],
            response_format=openai_config["response_format"]
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content.strip())
        is_weather_query = result.get("is_weather_query", False)
        
        return is_weather_query
        
    except Exception as e:
        # In case of API error, default to False
        return False

def extract_location_from_query(query: str) -> str:
    """
    Extract the location from a user query.
    """

    try:
        # Load prompts and config
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Get configuration for location extraction
        openai_config = config["openai"]["location_extraction"]
        weather_prompt = prompts["location_extraction"]["system"]
        
        response = client.chat.completions.create(
            model=openai_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": weather_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=openai_config["max_tokens"],
            temperature=openai_config["temperature"],
            response_format=openai_config["response_format"]
        )
        
        # Parse JSON response
        location = json.loads(response.choices[0].message.content.strip())
        
        return location
        
    except Exception as e:
        # In case of API error, default to False
        return False

    return query

def generate_weather_request(query: str, client_ip: Optional[str] = None) -> CurrentWeatherRequest:
    """
    Generate CurrentWeatherParameters and CurrentWeatherRequest from a user query string.
    Makes two API calls: one to extract necessary parameters, and another to build the request.
    
    Args:
        query (str): The user query describing what weather information they need
        client_ip (Optional[str]): Client IP address for location detection
        
    Returns:
        CurrentWeatherRequest: Complete request object ready for the weather API
    """
    logger.info(f"Starting weather request generation for query: '{query}'")
    
    try:
        # Load prompts and config
        logger.debug("Loading prompts and configuration files")
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Generate JSON schemas from Pydantic models and make them strict-compatible
        logger.debug("Generating JSON schemas from Pydantic models")
        weather_params_schema = ensure_strict_schema(CurrentWeatherParameters.model_json_schema())
        
        # Generate base request schema without the 'current', 'latitude', and 'longitude' fields
        base_request_schema = CurrentWeatherRequest.model_json_schema()
        base_request_schema['properties'].pop('current', None)
        base_request_schema['properties'].pop('latitude', None)
        base_request_schema['properties'].pop('longitude', None)
        
        # Apply strict mode requirements recursively
        base_request_schema = ensure_strict_schema(base_request_schema)
        
        logger.debug("JSON schemas prepared successfully")
        
        # First API call: Extract necessary weather parameters
        logger.debug("Starting first API call: parameter extraction")
        param_config = config["openai"]["weather_parameter_extraction"]
        base_param_prompt = prompts["weather_parameter_extraction"]["system"]
        
        # Dynamically append the parameter list to the prompt
        parameters_description = get_weather_parameters_description()
        param_prompt = base_param_prompt.replace(
            "PLACEHOLDER_FOR_DYNAMIC_PARAMETERS",
            parameters_description
        )
        
        logger.debug(f"Using model for parameter extraction: {param_config['model']}")
        logger.debug(f"Parameter extraction prompt prepared, length: {len(param_prompt)} characters")
        
        param_response = client.chat.completions.create(
            model=param_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": param_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=param_config["max_tokens"],
            temperature=param_config["temperature"],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "weather_parameters",
                    "strict": True,
                    "schema": weather_params_schema
                }
            }
        )
        
        logger.debug("Parameter extraction API call completed successfully")
        
        # Parse parameter extraction response
        param_data = json.loads(param_response.choices[0].message.content.strip())
        logger.debug(f"Extracted parameters: {param_data}")
        
        # Create CurrentWeatherParameters object with only necessary parameters
        weather_params = CurrentWeatherParameters(**param_data)
        logger.info(f"Weather parameters created successfully: {weather_params}")
        
        # Second API call: Build the weather request (using excluded schema)
        logger.debug("Starting second API call: request building")
        request_config = config["openai"]["weather_request_building"]
        base_request_prompt = prompts["weather_request_building"]["system"]
        
        # Dynamically append the request parameters list to the prompt
        request_parameters_description = get_weather_request_parameters_description()
        request_prompt = base_request_prompt.replace(
            "PLACEHOLDER_FOR_REQUEST_PARAMETERS",
            request_parameters_description
        )
        
        logger.debug(f"Using model for request building: {request_config['model']}")
        logger.debug(f"Request building prompt prepared, length: {len(request_prompt)} characters")
        
        request_response = client.chat.completions.create(
            model=request_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": request_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=request_config["max_tokens"],
            temperature=request_config["temperature"],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "weather_request",
                    "strict": True,
                    "schema": base_request_schema
                }
            }
        )
        
        logger.debug("Request building API call completed successfully")
        
        # Parse request building response
        request_data = json.loads(request_response.choices[0].message.content.strip())
        logger.debug(f"Request building response: {request_data}")
        
        # Add the weather parameters to the request data
        request_data["current"] = weather_params

        # Get latitude and longitude from IP
        logger.debug(f"Getting location from IP address: {client_ip or 'auto-detect'}")
        latitude, longitude = get_location_from_ip(client_ip)
        request_data["latitude"] = latitude
        request_data["longitude"] = longitude
        
        logger.info(f"Location determined: latitude={latitude}, longitude={longitude}")
        
        # Create and return CurrentWeatherRequest object
        weather_request = CurrentWeatherRequest(**request_data)
        logger.info("Weather request generated successfully")
        logger.debug(f"Final weather request: {weather_request}")

        return weather_request
        
    except Exception as e:
        # In case of API error, raise the exception with context
        logger.error(f"Error generating weather request: {e}")
        logger.debug(f"Query that failed request generation: '{query}'")
        raise Exception(f"Error generating weather request: {e}")
    
def generate_weather_request_location(query: str, location: str) -> CurrentWeatherRequest:
    """
    Generate CurrentWeatherParameters and CurrentWeatherRequest from a user query string and a specific location.
    Makes two API calls: one to extract necessary parameters, and another to build the request.
    
    Args:
        query (str): The user query describing what weather information they need
        location (str): The location to get weather information for
        
    Returns:
        CurrentWeatherRequest: Complete request object ready for the weather API
    """
    
    try:
        # Load prompts and config
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Generate JSON schemas from Pydantic models and make them strict-compatible
        weather_params_schema = ensure_strict_schema(CurrentWeatherParameters.model_json_schema())
        
        # Generate base request schema without the 'current', 'latitude', and 'longitude' fields
        base_request_schema = CurrentWeatherRequest.model_json_schema()
        base_request_schema['properties'].pop('current', None)
        base_request_schema['properties'].pop('latitude', None)
        base_request_schema['properties'].pop('longitude', None)
        
        # Apply strict mode requirements recursively
        base_request_schema = ensure_strict_schema(base_request_schema)
        
        # First API call: Extract necessary weather parameters
        param_config = config["openai"]["weather_parameter_extraction"]
        base_param_prompt = prompts["weather_parameter_extraction"]["system"]
        
        # Dynamically append the parameter list to the prompt
        parameters_description = get_weather_parameters_description()
        param_prompt = base_param_prompt.replace(
            "PLACEHOLDER_FOR_DYNAMIC_PARAMETERS",
            parameters_description
        )
        
        param_response = client.chat.completions.create(
            model=param_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": param_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=param_config["max_tokens"],
            temperature=param_config["temperature"],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "weather_parameters",
                    "strict": True,
                    "schema": weather_params_schema
                }
            }
        )
        
        # Parse parameter extraction response
        param_data = json.loads(param_response.choices[0].message.content.strip())
        
        # Create CurrentWeatherParameters object with only necessary parameters
        weather_params = CurrentWeatherParameters(**param_data)
        
        # Second API call: Build the weather request (using excluded schema)
        request_config = config["openai"]["weather_request_building"]
        base_request_prompt = prompts["weather_request_building"]["system"]
        
        # Dynamically append the request parameters list to the prompt
        request_parameters_description = get_weather_request_parameters_description()
        request_prompt = base_request_prompt.replace(
            "PLACEHOLDER_FOR_REQUEST_PARAMETERS",
            request_parameters_description
        )
        
        request_response = client.chat.completions.create(
            model=request_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": request_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=request_config["max_tokens"],
            temperature=request_config["temperature"],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "weather_request",
                    "strict": True,
                    "schema": base_request_schema
                }
            }
        )
        
        # Parse request building response
        request_data = json.loads(request_response.choices[0].message.content.strip())
        
        # Add the weather parameters to the request data
        request_data["current"] = weather_params

        # Get latitude and longitude from the geocoding api in utils.geo_utils
        latitude, longitude = get_lat_lon_from_location(location)
        request_data["latitude"] = latitude
        request_data["longitude"] = longitude
        
        # Create and return CurrentWeatherRequest object
        weather_request = CurrentWeatherRequest(**request_data)

        return weather_request
        
    except Exception as e:
        # In case of API error, raise the exception with context
        raise Exception(f"Error generating weather request: {e}")

def answer_weather_query(weather_response: CurrentWeatherResponse, user_query: str) -> str:
    """
    Generate a natural language answer to a user's weather query based on the weather data.
    
    Args:
        weather_response (CurrentWeatherResponse): The weather data response from the API
        user_query (str): The original user query asking about weather
        
    Returns:
        str: A natural language answer to the user's weather query
    """
    logger.info(f"Starting weather answer generation for query: '{user_query}'")
    logger.debug(f"Weather response data available: {len(str(weather_response))} characters")
    
    try:
        # Load prompts and config
        logger.debug("Loading prompts and configuration files")
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Get configuration for weather answer generation
        openai_config = config["openai"]["weather_answer_generation"]
        base_answer_prompt = prompts["weather_answer_generation"]["system"]
        
        logger.debug(f"Using model for answer generation: {openai_config['model']}")
        
        # Dynamically inject parameter information into the prompt
        logger.debug("Preparing dynamic parameter descriptions")
        weather_parameters_description = get_weather_parameters_description()
        request_parameters_description = get_weather_request_parameters_description()
        
        answer_prompt = base_answer_prompt.replace(
            "PLACEHOLDER_FOR_WEATHER_PARAMETERS", 
            weather_parameters_description
        ).replace(
            "PLACEHOLDER_FOR_REQUEST_PARAMETERS", 
            request_parameters_description
        )
        
        logger.debug(f"Answer generation prompt prepared, length: {len(answer_prompt)} characters")
        
        # Convert weather response to a clean JSON string for the prompt
        weather_data = weather_response.model_dump_json(indent=2)
        logger.debug(f"Weather data serialized, length: {len(weather_data)} characters")
        
        # Create the user message combining the query and weather data
        user_message = f"User Query: {user_query}\n\nWeather Data:\n{weather_data}"
        logger.debug(f"User message prepared, total length: {len(user_message)} characters")
        
        response = client.chat.completions.create(
            model=openai_config["model"],
            messages=[
                {
                    "role": "system",
                    "content": answer_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=openai_config["max_tokens"],
            temperature=openai_config["temperature"]
        )
        
        logger.debug("Answer generation API call completed successfully")
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"Weather answer generated successfully, length: {len(answer)} characters")
        logger.debug(f"Generated answer: {answer}")
        
        return answer
        
    except Exception as e:
        # In case of API error, raise the exception with context
        logger.error(f"Error generating weather answer: {e}")
        logger.debug(f"Query that failed answer generation: '{user_query}'")
        logger.debug(f"Weather response that failed: {weather_response}")
        raise Exception(f"Error generating weather answer: {e}")



