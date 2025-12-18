# EKAPEx Weather API

The backend service of the EKAPEx Weather Demo application. A FastAPI-based API for weather data processing and visualization, supporting multiple AI weather forecasting models.

## Overview

This is the backend component of the EKAPEx Weather Demo project. It provides a RESTful API for accessing weather forecast data from multiple models (GraphCast, Cerrora), processes weather datasets, and generates high-quality map visualizations.

## Features

- **Weather Data Processing**: Loads and processes weather data from Zarr datasets
- **Multiple Model Support**: Supports GraphCast and Cerrora weather forecasting models
- **Visualization Generation**: Creates weather map visualizations using Cartopy
- **RESTful API**: Provides endpoints for weather data access and retrieval
- **Static File Serving**: Serves generated visualization images
- **Weather Parameters**:
  - Temperature & Wind
  - Geopotential Height
  - Sea Level Pressure

## Project Structure

```
weather_api/
│
├── app/                    # Main application package 
│   ├── __init__.py
│   ├── main.py            # FastAPI application instance and configuration
│   ├── config.py          # Configuration settings
│   ├── api/               # API endpoints and models
│   │   ├── __init__.py
│   │   ├── routes.py      # API route definitions
│   │   └── models.py      # Pydantic models for request/response
│   ├── core/              # Core business logic
│   │   ├── __init__.py
│   │   ├── visualization.py    # Data visualization logic
│   │   └── data_loader.py     # Data loading and processing
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── helpers.py     # Helper functions
│
├── streaming/             # Generated visualization images
├── tests/                 # Test directory
│   └── __init__.py
│
├── requirements.txt       # Project dependencies
├── README.md             # This documentation
└── run.py                # Application entry point
```

## Installation

### Prerequisites

- Python 3.9+
- Conda (recommended for environment management)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/HPI-DeepLearning/EKAPEx-Demo.git
cd EKAPEx-Demo/weather_api
```

2. Create and activate a conda environment:
```bash
conda create --name ekapex python=3.9
conda activate ekapex
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Create a `.env` file in the project root
   - Add your configuration based on the project Wiki

## Usage

### Starting the Server

Start the server using the run script:
```bash
python run.py --host 0.0.0.0 --port 8999
```

Optional command line arguments:
- `--host`: Server host (default: 0.0.0.0)
- `--port`: Server port (default: 8999)
- `--reload`: Enable auto-reload for development
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Example with options:
```bash
python run.py --host 0.0.0.0 --port 8999 --reload --log-level DEBUG
```

### API Endpoints

The API will be available at `http://localhost:8999/api/v1`

Key endpoints:
- `GET /api/v1/base-times`: Get available base times for a variable type
- `POST /api/v1/data/{variable_type}`: Get weather data for specific time ranges
- Static files served at `/backend-fast-api/streaming/`

### Example Requests

#### Using Python
```python
import requests
import json

# Get temperature and wind data
url = "http://localhost:8999/api/v1/data/temp_wind"
payload = {
    "baseTime": 1609459200,
    "validTime": [1609459200, 1609462800]
}
headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())
```

#### Using cURL
```bash
# Get base times
curl -X GET "http://localhost:8999/api/v1/base-times?variableType=temp_wind"

# Get temperature and wind data
curl -X POST "http://localhost:8999/api/v1/data/temp_wind" \
     -H "Content-Type: application/json" \
     -d '{
           "baseTime": 1609459200,
           "validTime": [1609459200, 1609462800]
         }'
```

## Integration

This backend service is designed to work with the frontend application located in `weather_ui/`. For full application setup, see the [main project README](../README.md).

The frontend connects to this API using:
- `NEXT_PUBLIC_API_BASE_URL`: API endpoint base URL (e.g., `http://localhost:8999/api/v1`)
- `NEXT_PUBLIC_IMAGE_BASE_URL`: Image serving base URL (e.g., `http://localhost:8999/backend-fast-api/streaming`)

## Supported Weather Models

- **GraphCast**: Google's graph neural network weather model
- **Cerrora**: Model created by the HPI EKAPEx team

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## License

See the main project README for license information.

## Acknowledgments

- Weather data provided by [WeatherBench2](https://github.com/google-research/weatherbench2)
- Map visualizations powered by [Cartopy](https://scitools.org.uk/cartopy/docs/latest/)
- Built with [FastAPI](https://fastapi.tiangolo.com/)