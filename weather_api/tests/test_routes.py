import pandas as pd
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import numpy as np
import xarray as xr
from unittest.mock import patch

from app.main import app
from app.core.data_loader import DataLoader

client = TestClient(app)


@pytest.fixture
def mock_dataset():
    """Create a simple mock dataset with required variables."""
    # Create time and predict time increments
    base_time = pd.Timestamp('2021-01-01')
    times = pd.date_range(base_time, periods=15, freq='12h')
    deltas = pd.timedelta_range(start='0h', periods=15, freq='12h')

    lats = np.linspace(-90, 90, 37)
    lons = np.linspace(-180, 180, 73)

    # Create dimensions and coordinates
    dims = ('time', 'prediction_timedelta', 'lat', 'lon')
    coords = {
        'time': times.to_numpy(),
        'prediction_timedelta': deltas.to_numpy(),
        'lat': lats,
        'lon': lons
    }

    # Create data
    shape = (len(times), len(deltas), len(lats), len(lons))
    temp_data = np.random.rand(*shape) * 30
    wind_u_data = np.random.rand(*shape) * 10
    wind_v_data = np.random.rand(*shape) * 10

    # Create a dataset
    ds = xr.Dataset(
        data_vars={
            '2m_temperature': (dims, temp_data),
            '10m_u_component_of_wind': (dims, wind_u_data),
            '10m_v_component_of_wind': (dims, wind_v_data)
        },
        coords=coords
    )
    return ds


@pytest.fixture
def mock_zarr_mapper():
    """Mock the zarr mapper."""
    return {}


@pytest.fixture
def mock_gcs():
    """Mock GCS filesystem."""
    with patch('gcsfs.GCSFileSystem') as mock:
        instance = mock.return_value
        instance.get_mapper.return_value = {}
        yield instance

@pytest.fixture
def mock_data_loader(mock_dataset, monkeypatch):
    """Create a mock data loader that returns our test dataset."""

    def mock_init(self):
        self._dataset = mock_dataset
        self._fs = None

    def mock_get_variable_data(self, variable_name):
        return self._dataset[variable_name]

    # Patch the DataLoader class
    monkeypatch.setattr(DataLoader, "__init__", mock_init)
    monkeypatch.setattr(DataLoader, "get_variable_data", mock_get_variable_data)
    monkeypatch.setattr(DataLoader, "dataset", property(lambda self: self._dataset))

    return DataLoader()

@pytest.fixture(autouse=True)
def setup_app(mock_data_loader):
    """Setup app with mocked dependencies."""
    with patch('app.api.routes.data_loader', mock_data_loader):
        yield


def test_get_base_times():
    """Test the base-times endpoint."""
    response = client.get("/api/v1/base-times?variableType=temp_wind")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0, "Base times list should not be empty"

    for item in data:
        assert "label" in item, "Each item should have a label"
        assert "value" in item, "Each item should have a value"
        assert isinstance(item["value"], str), "Value should be a string"
        # Validate timestamp format
        timestamp = int(item["value"])
        assert isinstance(timestamp, int), "Value should be convertible to integer"
        # Validate label format (e.g., "Mon 01 Jan 2021 00 UTC")
        assert len(item["label"].split()) == 6, "Label should be in correct format"


def test_get_valid_times():
    """Test the valid-times endpoint."""
    response = client.get("/api/v1/valid-times")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    for item in data:
        assert "label" in item
        assert "value" in item
        timestamp = int(item["value"])
        assert isinstance(timestamp, int)


def test_temp_wind_data(mock_data_loader):
    """Test the temperature and wind data endpoint."""
    base_time = pd.Timestamp('2021-01-01')
    valid_time = base_time + pd.Timedelta(hours=12)

    payload = {
        "baseTime": int(base_time.timestamp()),
        "validTime": [
            int(base_time.timestamp()),
            int(valid_time.timestamp())
        ]
    }

    with patch('app.core.visualization.WeatherVisualizer.create_temp_wind_plot',
               return_value="http://example.com/test.webp"):
        response = client.post("/api/v1/data/temp_wind", json=payload)
        assert response.status_code == 200, f"Response: {response.json()}"
        data = response.json()
        assert "images" in data
        assert isinstance(data["images"], list)
        assert len(data["images"]) == 2


def test_future_time_range(mock_data_loader):
    """Test endpoint with future time range."""
    base_time = pd.Timestamp('2021-01-01')
    future_time = base_time + pd.Timedelta(hours=12)

    payload = {
        "baseTime": int(base_time.timestamp()),
        "validTime": [int(future_time.timestamp())]
    }

    with patch('app.core.visualization.WeatherVisualizer.create_temp_wind_plot',
               return_value="http://example.com/test.webp"):
        response = client.post("/api/v1/data/temp_wind", json=payload)
        assert response.status_code == 200, f"Response: {response.json()}"


def test_invalid_time_range():
    """Test endpoint with invalid time range."""
    payload = {
        "baseTime": "invalid",
        "validTime": [1609459200]
    }

    response = client.post("/api/v1/data/temp_wind", json=payload)
    assert response.status_code == 422


def test_empty_valid_times():
    """Test endpoint with empty valid times list."""
    payload = {
        "baseTime": int(datetime(2021, 1, 1).timestamp()),
        "validTime": []
    }

    response = client.post("/api/v1/data/temp_wind", json=payload)
    assert response.status_code == 200
    assert response.json()["images"] == []