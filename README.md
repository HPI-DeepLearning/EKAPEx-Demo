# EKAPEx Weather Demo

A web application for visualizing and comparing weather forecasting models, featuring interactive maps, model comparison dashboards, and weather data visualization.

## Overview

This application provides a comprehensive platform for exploring weather forecast data from two AI models (GraphCast, Cerrora). It enables users to visualize weather patterns, compare model predictions, and analyze forecast accuracy through an intuitive web interface.

## Architecture

The application consists of two main components:

### Backend (`weather_api/`)
- **Technology**: FastAPI (Python)
- **Purpose**: Weather data processing and visualization API
- **Features**:
  - Loads weather data from Zarr datasets
  - Generates weather map visualizations
  - Supports multiple weather models (GraphCast, Cerrora)
  - Provides RESTful API endpoints for weather data access
  - Serves static visualization images

### Frontend (`weather_ui/`)
- **Technology**: Next.js 15 with React 19 and TypeScript
- **Purpose**: Interactive user interface for weather visualization
- **Features**:
  - Interactive weather maps with zoom and pan
  - Model comparison dashboard
  - Time-based forecast selection
  - Metrics reporting and charts

## Key Features

- **Weather Visualization**: Interactive maps displaying temperature, wind, geopotential height, and sea level pressure
- **Model Comparison**: Side-by-side comparison of different weather forecasting models
- **Time-based Analysis**: Select and compare forecasts across different time ranges
- **Inference Comparison**: Compare model predictions with ground truth data
- **Metrics Dashboard**: Visualize model performance metrics and accuracy statistics

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Conda (for backend environment)

### Backend Setup

```bash
cd weather_api
conda create --name ekapex python=3.9
conda activate ekapex
pip install -r requirements.txt
python run.py --host 0.0.0.0 --port 8999
```

### Frontend Setup

```bash
cd weather_ui
npm install
# Create .env.local with:
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8999/api/v1
# NEXT_PUBLIC_IMAGE_BASE_URL=http://localhost:8999/backend-fast-api/streaming
npm run dev
```

The application will be available at `http://localhost:3000`.

## Project Structure

```
web-demo/
├── weather_api/          # FastAPI backend service
│   ├── app/              # Application code
│   │   ├── api/          # API routes and models
│   │   ├── core/         # Business logic and visualization
│   │   └── utils/        # Utility functions
│   ├── streaming/        # Generated visualization images
│   └── requirements.txt  # Python dependencies
│
├── weather_ui/           # Next.js frontend application
│   ├── app/              # Next.js app router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── package.json      # Node.js dependencies
│
└── README.md            # This file
```

## Supported Weather Models

- **GraphCast**: Google's graph neural network weather model
- **Cerrora**: Model created by the HPI EKAPEx team 

## Weather Parameters

- Temperature & Wind
- Geopotential Height
- Sea Level Pressure

## Documentation

For detailed setup and API documentation, see:
- [Backend README](weather_api/README.md)
- [Frontend README](weather_ui/README.md)

## License

See the license file.