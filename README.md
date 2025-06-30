# Guided Energy Take-Home

Repository with working implementation for the Guided Energy take-home assignment.

A FastAPI-based weather agent that provides intelligent weather information using OpenAI's GPT models and the OpenMeteo weather API.

## Approach

This weather agent system uses a **multi-stage AI pipeline** to transform natural language weather queries into structured API calls and then back into natural language responses. The approach consists of four distinct stages:

### 1. Query Classification
- Uses OpenAI's `gpt-4.1-nano` model to determine if a user query is weather-related and within scope
- Focuses specifically on current weather at the user's current location
- Rejects queries about future weather, other locations, or non-weather topics

### 2. Parameter Extraction  
- Uses `gpt-4.1-mini` to analyze the weather query and determine which specific weather parameters are needed
- Dynamically generates parameter lists based on available OpenMeteo API options
- Only requests parameters that are directly relevant to answering the user's question

### 3. Request Building
- Uses `gpt-4.1-mini` to construct the complete API request with proper formatting
- Automatically determines user location via IP geolocation
- Builds structured requests compatible with OpenMeteo's API schema

### 4. Response Generation
- Uses `gpt-4.1-mini` to convert structured weather data back into natural language
- Provides conversational, user-friendly responses that directly answer the original query
- Focuses only on relevant information while maintaining clarity

### Architecture Benefits
- **Separation of Concerns**: Each AI model has a specific, focused task
- **Error Handling**: Graceful degradation when any stage fails
- **Extensibility**: Easy to modify individual stages without affecting others
- **Cost Optimization**: Uses smaller, faster models where appropriate (nano for simple classification)

## Features

- **Weather Agent**: Intelligent weather query classification and response generation
- **Current Weather API**: Direct access to current weather data via OpenMeteo
- **Natural Language Processing**: Uses OpenAI GPT models for query understanding and response generation
- **API Documentation**: Interactive Swagger UI and ReDoc documentation

## Prerequisites

- **Python 3.13+** (required)
- **uv** package manager (recommended) or pip
- **OpenAI API Key** (required for agent functionality)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd guided-energy-takehome
```

### 2. Install Dependencies

#### Option A: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Option B: Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Required: OpenAI API Key for agent functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set logging level (default: ERROR)
LOG_LEVEL=INFO
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key. You can get one from [OpenAI's platform](https://platform.openai.com/api-keys).

### 4. Verify Installation

Run the tests to ensure everything is set up correctly:

```bash
# Using uv
uv run pytest

# Using pip (with activated virtual environment)
pytest
```

## Running the Application Locally

### Start the Development Server

```bash
# Using uv
uv run python main.py

# Using pip (with activated virtual environment)
python main.py
```

The application will start on `http://localhost:8000`

### Local API Documentation

Once the local server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints

- `GET /` - API information and welcome message
- `GET /health` - Health check endpoint
- `POST /weather/current` - Get current weather data for a location
- `POST /simple_weather_agent` - Intelligent weather agent endpoint

### Example Usage

#### Weather Agent (Natural Language)

```bash
curl -X POST "http://localhost:8000/simple_weather_agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather like right now?"}'
```

#### Direct Weather API

```bash
curl -X POST "http://localhost:8000/weather/current" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "current": ["temperature_2m", "relative_humidity_2m", "weather_code"]
  }'
```

## Testing

### Run All Tests

```bash
# Using uv
uv run pytest

# Using pip
pytest
```

### Run Specific Test Files

```bash
# Test the main API endpoints
uv run pytest tests/test_main.py

# Test the weather agent
uv run pytest tests/test_simple_agent.py

# Test utilities
uv run pytest tests/test_geo_utils.py
uv run pytest tests/test_json_utils.py
uv run pytest tests/test_request_utils.py
```

### Run Tests with Coverage

```bash
uv run pytest --cov=. --cov-report=html
```

## Project Structure

```
guided-energy-takehome/
├── agents/
│   └── simple_agent.py          # Weather agent implementation
├── configs/
│   └── config.json              # OpenAI model configurations
├── models/
│   ├── requests.py              # Request models
│   └── responses.py             # Response models
├── prompts/
│   └── prompts.json             # AI prompts for different tasks
├── utils/
│   ├── geo_utils.py             # Geographic utilities
│   ├── json_utils.py            # JSON handling utilities
│   └── request_utils.py         # Request building utilities
├── tests/                       # Comprehensive test suite
├── main.py                      # FastAPI application entry point
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Key Product and Engineering Decisions

### Product Decisions

#### 1. **Scope Limitation Strategy**
- **Decision**: Restrict the agent to current weather at the user's current location only
- **Rationale**: Provides a focused, reliable experience rather than trying to handle all possible weather queries
- **Impact**: Reduces complexity and improves accuracy by avoiding ambiguous location/time scenarios

#### 2. **Natural Language Interface**
- **Decision**: Accept free-form natural language queries instead of structured inputs
- **Rationale**: More user-friendly and intuitive than requiring specific command formats
- **Impact**: Requires sophisticated NLP processing but provides better user experience

#### 3. **Automatic Location Detection**
- **Decision**: Use IP-based geolocation instead of requiring user to provide coordinates
- **Rationale**: Reduces friction and makes the service immediately usable
- **Impact**: May be less accurate than GPS but eliminates setup barriers

### Engineering Decisions

#### 1. **Multi-Stage AI Pipeline Architecture**
- **Decision**: Break down the AI processing into 4 distinct stages instead of one large model call
- **Rationale**: 
  - Better error handling and debugging
  - Cost optimization (use smaller models for simpler tasks)
  - Easier to test and modify individual components
  - More reliable structured output generation
- **Trade-offs**: More complex orchestration but better maintainability

#### 2. **OpenAI Model Selection**
- **Decision**: Use different GPT models for different tasks (nano, mini)
- **Rationale**: 
  - `gpt-4.1-nano` for simple classification (cost-effective)
  - `gpt-4.1-mini` for complex reasoning tasks
  - Balance between performance and cost
- **Trade-offs**: Multiple API calls vs. single expensive call

#### 3. **Structured Output with JSON Schema**
- **Decision**: Use OpenAI's structured output feature with strict JSON schemas
- **Rationale**: 
  - Ensures reliable parsing of AI responses
  - Reduces errors from malformed JSON
  - Enables type safety with Pydantic models
- **Trade-offs**: More setup complexity but much more reliable

#### 4. **FastAPI Framework Choice**
- **Decision**: Use FastAPI instead of Flask or Django
- **Rationale**: 
  - Built-in async support for external API calls
  - Automatic API documentation generation
  - Type hints and validation with Pydantic
  - High performance for API workloads
- **Trade-offs**: Learning curve but better developer experience

#### 5. **OpenMeteo API Integration**
- **Decision**: Use OpenMeteo instead of other weather APIs
- **Rationale**: 
  - Free and reliable weather data
  - Good API design with clear parameters
  - No API key required for basic usage
- **Trade-offs**: Less comprehensive than paid services but sufficient for core use case

#### 6. **Comprehensive Logging Strategy**
- **Decision**: Implement detailed logging at multiple levels throughout the application
- **Rationale**: 
  - Essential for debugging AI model interactions
  - Helps track performance and costs
  - Enables monitoring in production
- **Trade-offs**: More verbose code but much better observability

#### 7. **Pydantic Models for Type Safety**
- **Decision**: Use Pydantic models for all requests/responses
- **Rationale**: 
  - Runtime type validation
  - Automatic serialization/deserialization
  - Clear API documentation
  - IDE support and error catching
- **Trade-offs**: More boilerplate but much more robust

#### 8. **Modular Utility Functions**
- **Decision**: Separate concerns into focused utility modules (geo, json, request)
- **Rationale**: 
  - Easier testing of individual components
  - Code reusability across different parts of the system
  - Clear separation of responsibilities
- **Trade-offs**: More files to manage but better maintainability

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key for agent functionality
- `LOG_LEVEL` (optional): Logging level (DEBUG, INFO, WARNING, ERROR). Default: ERROR

### OpenAI Model Configuration

The application uses different OpenAI models for different tasks, configured in `configs/config.json`:

- **Query Classification**: gpt-4.1-nano (cost-optimized for simple decisions)
- **Parameter Extraction**: gpt-4.1-mini (balanced performance/cost for reasoning)
- **Request Building**: gpt-4.1-mini (structured output generation)
- **Answer Generation**: gpt-4.1-mini (natural language generation)

## Deployment

### Render Deployment

This application is configured for easy deployment on [Render](https://render.com), a modern cloud platform that supports automatic deployments from Git repositories.

#### Prerequisites for Deployment

- A [Render account](https://render.com) 
- Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
- An OpenAI API key

#### Deployment Steps

1. **Connect Your Repository**
   - Log into your Render dashboard
   - Click "New +" and select "Web Service"
   - Connect your Git repository containing this project
   - Select the repository and branch to deploy

2. **Configure the Web Service**
   ```
   Name: guided-energy-weather-agent (or your preferred name)
   Build Command: uv sync --frozen && uv cache prune --ci (should be set by default)
   Start Command: uv run main.py
   ```

3. **Set Environment Variables**
   In the Render dashboard, add the following environment variables:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   LOG_LEVEL=ERROR
   ```

4. **Advanced Settings (Optional)**
   ```
   Instance Type: Starter (to see docs)
   Auto-Deploy: Yes (recommended for automatic updates)
   Health Check Path: /health
   ```

#### Alternative Render Configuration

You can also create a `render.yaml` file in your repository root for infrastructure-as-code deployment:

```yaml
services:
  - type: web
    name: guided-energy-weather-agent
    env: python
    buildCommand: uv sync --frozen && uv cache prune --ci
    startCommand: uv run main.py
      - key: OPENAI_API_KEY
        sync: false  # Set this manually in Render dashboard for security
      - key: LOG_LEVEL
        value: ERROR
    healthCheckPath: /health
```

#### Post-Deployment

1. **Verify Deployment**
   - Visit your Render service URL
   - Check `/health` endpoint returns healthy status
   - Test `/docs` for API documentation
   - Access API documentation at `/redoc` for alternative documentation format

2. **Monitor Logs**
   - Use Render's log viewer to monitor application performance
   - Set `LOG_LEVEL=DEBUG` temporarily for detailed troubleshooting

3. **Custom Domain (Optional)**
   - Add a custom domain in Render dashboard if desired
   - Render provides free SSL certificates

#### Deployment Considerations

- **Environment Variables**: Never commit API keys to your repository - always use environment variables
- **Scaling**: Upgrade to paid plans for production workloads requiring guaranteed uptime
- **Database**: This application doesn't require a database, making deployment simpler

#### Troubleshooting Deployment

- **Build Failures**: Check that `pyproject.toml` includes all required dependencies
- **Runtime Errors**: Verify environment variables are set correctly
- **API Errors**: Ensure OpenAI API key is valid and has sufficient credits
- **Health Check Fails**: Confirm the application starts on port 8000 (Render's default)

## Development

### Local Development Guidelines

The project follows Python best practices. Run tests before committing:

```bash
uv run pytest
```

### Adding New Features

1. Add your implementation
2. Write corresponding tests in the `tests/` directory
3. Update documentation if needed
4. Ensure all tests pass
5. Test deployment on Render staging environment before production

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your `.env` file contains a valid `OPENAI_API_KEY`
2. **Python Version**: Ensure you're using Python 3.13 or higher
3. **Dependencies**: If using pip, make sure your virtual environment is activated
4. **Port Conflicts**: The app runs on port 8000 by default. Ensure it's available.

### Getting Help

- Check the logs for detailed error messages (set `LOG_LEVEL=DEBUG` for verbose logging)
- Review the test files for usage examples
- Consult the API documentation at `/docs` when the server is running

## License

See [LICENSE](LICENSE) file for details.

## Further Improvements

This current implementation represents a first part. The following improvements were planned but not implemented due to prioritizing a more limited version delivered quicker.

#### Historical Weather Integration
- **Implement historical weather API endpoints** using OpenMeteo's Historical Weather API
- **Extend agent to handle past weather queries** (e.g., "What was the weather like last Tuesday?")
- **Add date parsing and validation** for historical requests
- **Update prompts** to handle temporal reasoning

#### Future Weather/Forecasting
- **Implement forecast API endpoints** using OpenMeteo's Forecast API (7-16 days)
- **Add hourly and daily forecast capabilities** 
- **Extend agent for future weather queries** (e.g., "Will it rain tomorrow?", "What's the weather forecast for next week?")
- **Implement forecast confidence and uncertainty handling**

#### Location Flexibility
- **Remove current location restriction** to support any location queries
- **Add location parsing and geocoding** (city names, addresses, landmarks)
- **Implement location validation and disambiguation**
- **Support multiple location formats** (coordinates, city names, postal codes)

#### Multi-Step Reasoning
- **Implement recursive agent logic** for complex, multi-part queries
- **Add query decomposition** (e.g., "Compare weather in NYC and LA this week")
- **Implement cross-temporal analysis** (e.g., "How does today compare to last year?")
- **Add weather trend analysis and insights**

#### Evaluation Framework
- **Implement comprehensive evaluation suite** for agent responses


