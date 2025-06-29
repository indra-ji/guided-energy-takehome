import json

def load_json(file_path: str):
    """Load JSON data from a file"""

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_path} not found")


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