import json
import logging
import os
import dotenv

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

def load_json(file_path: str):
    """Load JSON data from a file"""
    logger.debug(f"Loading JSON file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded JSON file: {file_path}")
            logger.debug(f"JSON data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict data'}")
            logger.debug(f"JSON data size: {len(str(data))} characters")
            return data
    except FileNotFoundError as e:
        logger.error(f"JSON file not found: {file_path}")
        raise FileNotFoundError(f"{file_path} not found")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in file {file_path}: {e}")
        raise json.JSONDecodeError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading JSON file {file_path}: {e}")
        raise Exception(f"Error loading {file_path}: {e}")


def ensure_strict_schema(schema: dict) -> dict:
    """
    Recursively ensure a schema is compatible with OpenAI's strict mode by:
    1. Setting additionalProperties to false for all objects
    2. Ensuring all properties are listed in required array
    """
    logger.debug("Starting schema strict mode conversion")
    logger.debug(f"Input schema keys: {list(schema.keys()) if isinstance(schema, dict) else 'Non-dict schema'}")
    
    original_schema_size = len(str(schema))
    
    if isinstance(schema, dict):
        # Handle object types
        if schema.get('type') == 'object':
            logger.debug("Processing object type schema")
            # Set additionalProperties to false
            schema['additionalProperties'] = False
            
            # Ensure all properties are required
            if 'properties' in schema:
                property_count = len(schema['properties'])
                schema['required'] = list(schema['properties'].keys())
                logger.debug(f"Set {property_count} properties as required: {schema['required']}")
                
                # Recursively process nested properties
                for prop_name, prop_schema in schema['properties'].items():
                    logger.debug(f"Processing nested property: {prop_name}")
                    schema['properties'][prop_name] = ensure_strict_schema(prop_schema)
        
        # Handle arrays with items
        elif schema.get('type') == 'array' and 'items' in schema:
            logger.debug("Processing array type schema")
            schema['items'] = ensure_strict_schema(schema['items'])
        
        # Handle anyOf, oneOf, allOf
        for key in ['anyOf', 'oneOf', 'allOf']:
            if key in schema:
                logger.debug(f"Processing {key} schema variations")
                schema[key] = [ensure_strict_schema(s) for s in schema[key]]
        
        # Handle $ref (though Pydantic's model_json_schema should resolve these)
        if '$defs' in schema:
            def_count = len(schema['$defs'])
            logger.debug(f"Processing {def_count} schema definitions")
            for def_name, def_schema in schema['$defs'].items():
                logger.debug(f"Processing schema definition: {def_name}")
                schema['$defs'][def_name] = ensure_strict_schema(def_schema)
    
    final_schema_size = len(str(schema))
    logger.debug(f"Schema strict mode conversion completed. Size: {original_schema_size} -> {final_schema_size} characters")
    
    return schema