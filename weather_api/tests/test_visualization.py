import pytest
import numpy as np
import xarray as xr
from datetime import datetime
from unittest.mock import patch
import os

from app.core.visualization import WeatherVisualizer
from app.config import settings


@pytest.fixture
def sample_data():
    """Create sample weather data for testing."""
    # Create a simple grid
    lats = np.linspace(-90, 90, 37)
    lons = np.linspace(-180, 180, 73)

    # Create sample data arrays
    temp_data = np.random.rand(len(lats), len(lons)) * 30 + 273.15  # Temperature in Kelvin
    wind_u = np.random.rand(len(lats), len(lons)) * 10
    wind_v = np.random.rand(len(lats), len(lons)) * 10

    # Create xarray DataArrays
    temp = xr.DataArray(
        data=temp_data,
        dims=['lat', 'lon'],
        coords={'lat': lats, 'lon': lons},
        name='2m_temperature'
    )

    wind_u = xr.DataArray(
        data=wind_u,
        dims=['lat', 'lon'],
        coords={'lat': lats, 'lon': lons},
        name='10m_u_component_of_wind'
    )

    wind_v = xr.DataArray(
        data=wind_v,
        dims=['lat', 'lon'],
        coords={'lat': lats, 'lon': lons},
        name='10m_v_component_of_wind'
    )

    return temp, wind_u, wind_v


@pytest.fixture
def visualizer():
    """Create WeatherVisualizer instance."""
    return WeatherVisualizer()


def test_visualizer_initialization(visualizer):
    """Test WeatherVisualizer initialization."""
    assert visualizer is not None
    assert hasattr(visualizer, 'world')


@patch('matplotlib.pyplot.savefig')
def test_create_temp_wind_plot(mock_savefig, visualizer, sample_data):
    """Test temperature and wind plot creation."""
    temp, wind_u, wind_v = sample_data
    timestamp_base = int(datetime.now().timestamp())
    timestamp_valid = timestamp_base + 3600

    # Create the plot
    url = visualizer.create_temp_wind_plot(
        temp,
        wind_u,
        wind_v,
        timestamp_base,
        timestamp_valid
    )

    # Check that savefig was called
    assert mock_savefig.called
    # Verify URL format
    assert url is not None
    assert 'tempWind' in url
    assert '.webp' in url


@patch('matplotlib.pyplot.savefig')
def test_create_geo_plot(mock_savefig, visualizer, sample_data):
    """Test geopotential plot creation."""
    geo_data = sample_data[0] * 100  # Use temperature data scaled as mock geopotential
    timestamp_base = int(datetime.now().timestamp())
    timestamp_valid = timestamp_base + 3600

    url = visualizer.create_geo_plot(
        geo_data,
        timestamp_base,
        timestamp_valid
    )

    assert mock_savefig.called
    assert url is not None
    assert 'geopotential' in url
    assert '.webp' in url


def test_plot_save_directory_creation(visualizer, sample_data):
    """Test that plot directories are created if they don't exist."""
    temp, wind_u, wind_v = sample_data
    timestamp_base = int(datetime.now().timestamp())
    timestamp_valid = timestamp_base + 3600

    # Try to create a plot
    visualizer.create_temp_wind_plot(
        temp,
        wind_u,
        wind_v,
        timestamp_base,
        timestamp_valid
    )

    # Check that directories exist
    expected_dir = os.path.join(os.path.dirname(__file__), '..', settings.IMAGE_OUTPUT_DIR, 'tempWind')
    assert os.path.exists(expected_dir)


def test_plot_error_handling(visualizer):
    """Test error handling in plot creation."""
    # Test with invalid data
    invalid_data = xr.DataArray(np.nan * np.ones((2, 2)))
    timestamp_base = int(datetime.now().timestamp())
    timestamp_valid = timestamp_base + 3600

    # Should handle error gracefully and return None
    url = visualizer.create_temp_wind_plot(
        invalid_data,
        invalid_data,
        invalid_data,
        timestamp_base,
        timestamp_valid
    )
    assert url is None


@pytest.mark.parametrize("plot_method,folder_name", [
    ('create_temp_wind_plot', 'tempWind'),
    ('create_geo_plot', 'geopotential'),
])
def test_plot_methods_output(visualizer, sample_data, plot_method, folder_name):
    """Test various plot methods output."""
    timestamp_base = int(datetime.now().timestamp())
    timestamp_valid = timestamp_base + 3600

    if plot_method == 'create_temp_wind_plot':
        temp, wind_u, wind_v = sample_data
        url = getattr(visualizer, plot_method)(temp, wind_u, wind_v, timestamp_base, timestamp_valid)
    else:
        url = getattr(visualizer, plot_method)(sample_data[0], timestamp_base, timestamp_valid)

    assert url is not None
    assert folder_name in url
    assert '.webp' in url
    assert str(timestamp_base) in url
    assert str(timestamp_valid) in url
