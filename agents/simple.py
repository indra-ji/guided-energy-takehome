from openai import OpenAI
import os
import json
import dotenv
from models.requests import CurrentWeatherParameters, CurrentWeatherRequest

dotenv.load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def load_prompts():
    """Load prompts from prompts.json"""
    try:
        with open('prompts/prompts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("prompts/prompts.json not found")

def load_config():
    """Load configuration from configs/config.json"""
    try:
        with open('configs/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("configs/config.json not found")

def ensure_strict_schema(schema: dict) -> dict:
    """
    Recursively ensure a schema is compatible with OpenAI's strict mode by:
    1. Setting additionalProperties to false for all objects
    2. Ensuring all properties are listed in required array
    """
    if isinstance(schema, dict):
        # Handle object types
        if schema.get('type') == 'object':
            # Set additionalProperties to false
            schema['additionalProperties'] = False
            
            # Ensure all properties are required
            if 'properties' in schema:
                schema['required'] = list(schema['properties'].keys())
                
                # Recursively process nested properties
                for prop_name, prop_schema in schema['properties'].items():
                    schema['properties'][prop_name] = ensure_strict_schema(prop_schema)
        
        # Handle arrays with items
        elif schema.get('type') == 'array' and 'items' in schema:
            schema['items'] = ensure_strict_schema(schema['items'])
        
        # Handle anyOf, oneOf, allOf
        for key in ['anyOf', 'oneOf', 'allOf']:
            if key in schema:
                schema[key] = [ensure_strict_schema(s) for s in schema[key]]
        
        # Handle $ref (though Pydantic's model_json_schema should resolve these)
        if '$defs' in schema:
            for def_name, def_schema in schema['$defs'].items():
                schema['$defs'][def_name] = ensure_strict_schema(def_schema)
    
    return schema

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
        prompts = load_prompts()
        config = load_config()
        
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
        prompts = load_prompts()
        config = load_config()
        
        # Generate JSON schemas from Pydantic models and make them strict-compatible
        weather_params_schema = ensure_strict_schema(CurrentWeatherParameters.model_json_schema())
        
        # Generate base request schema without the 'current' field
        base_request_schema = CurrentWeatherRequest.model_json_schema()
        base_request_schema['properties'].pop('current', None)
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
        
        # Create and return CurrentWeatherRequest object
        weather_request = CurrentWeatherRequest(**request_data)
        
        return weather_request
        
    except Exception as e:
        # In case of API error, raise the exception with context
        raise Exception(f"Error generating weather request: {e}")


