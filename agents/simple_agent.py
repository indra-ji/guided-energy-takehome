from openai import OpenAI
import os
import json
import dotenv
from models.requests import CurrentWeatherParameters, CurrentWeatherRequest
from models.responses import CurrentWeatherResponse
from utils.json_utils import load_json, ensure_strict_schema
from utils.geo_utils import get_location_from_ip

dotenv.load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def classify_weather_query(query: str) -> bool:
    """
    Classify if a query is related to current weather in current location.
    
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
        weather_prompt = prompts["weather_classification"]["system"]
        
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
        return result.get("is_weather_query", False)
        
    except Exception as e:
        # In case of API error, default to False
        print(f"Error classifying query: {e}")
        return False

def generate_weather_request(query: str) -> CurrentWeatherRequest:
    """
    Generate CurrentWeatherParameters and CurrentWeatherRequest from a user query string.
    Makes two API calls: one to extract necessary parameters, and another to build the request.
    
    Args:
        query (str): The user query describing what weather information they need
        
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
        param_prompt = prompts["weather_parameter_extraction"]["system"]
        
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
        request_prompt = prompts["weather_request_building"]["system"]
        
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

        # Get latitude and longitude from IP
        latitude, longitude = get_location_from_ip()
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
    try:
        # Load prompts and config
        prompts = load_json("prompts/prompts.json")
        config = load_json("configs/config.json")
        
        # Get configuration for weather answer generation
        openai_config = config["openai"]["weather_answer_generation"]
        answer_prompt = prompts["weather_answer_generation"]["system"]
        
        # Convert weather response to a clean JSON string for the prompt
        weather_data = weather_response.model_dump_json(indent=2)
        
        # Create the user message combining the query and weather data
        user_message = f"User Query: {user_query}\n\nWeather Data:\n{weather_data}"
        
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
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # In case of API error, raise the exception with context
        raise Exception(f"Error generating weather answer: {e}")



