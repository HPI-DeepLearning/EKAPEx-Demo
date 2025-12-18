import pytest
import xarray as xr
import numpy as np
from unittest.mock import patch
from datetime import datetime, timedelta

from app.core.data_loader import DataLoader


@pytest.fixture
def sample_zarr_data():
    """Create sample data that mimics the structure of our Zarr dataset."""
    times = [datetime(2021, 1, 1) + timedelta(hours=i * 12) for i in range(5)]
    lats = np.linspace(-90, 90, 37)
    lons = np.linspace(-180, 180, 73)

    # Create sample data arrays
    temp_data = np.random.rand(len(times), len(lats), len(lons)) * 30
    wind_u_data = np.random.rand(len(times), len(lats), len(lons)) * 10
    wind_v_data = np.random.rand(len(times), len(lats), len(lons)) * 10
    geo_data = np.random.rand(len(times), len(lats), len(lons)) * 1000

    # Create xarray dataset
    return xr.Dataset(
        {
            '2m_temperature': (('time', 'lat', 'lon'), temp_data),
            '10m_u_component_of_wind': (('time', 'lat', 'lon'), wind_u_data),
            '10m_v_component_of_wind': (('time', 'lat', 'lon'), wind_v_data),
            'geopotential': (('time', 'lat', 'lon'), geo_data),
        },
        coords={
            'time': times,
            'lat': lats,
            'lon': lons
        }
    )


@pytest.fixture
def mock_gcsfs():
    """Mock GCSFS filesystem."""
    with patch('gcsfs.GCSFileSystem') as mock:
        instance = mock.return_value
        instance.get_mapper.return_value = {}
        yield instance


@pytest.fixture
def mock_xarray():
    """Mock xarray open_zarr function."""
    with patch('xarray.open_zarr') as mock:
        yield mock


def test_data_loader_initialization():
    """Test DataLoader initialization."""
    loader = DataLoader()
    assert loader._dataset is None
    assert loader._fs is None


@patch('gcsfs.GCSFileSystem')
@patch('xarray.open_zarr')
def test_dataset_lazy_loading(mock_open_zarr, mock_gcsfs, sample_zarr_data):
    """Test that dataset is loaded lazily."""
    mock_open_zarr.return_value = sample_zarr_data

    loader = DataLoader()
    # Dataset should not be loaded yet
    assert loader._dataset is None

    # Access dataset property to trigger loading
    dataset = loader.dataset

    # Verify dataset is now loaded
    assert loader._dataset is not None
    assert mock_gcsfs.called
    assert mock_open_zarr.called


def test_get_variable_data(mock_gcsfs, mock_xarray, sample_zarr_data):
    """Test getting specific variable data."""
    mock_xarray.return_value = sample_zarr_data

    loader = DataLoader()
    # Get temperature data
    temp_data = loader.get_variable_data('2m_temperature')
    assert isinstance(temp_data, xr.DataArray)
    assert temp_data.dims == ('time', 'lat', 'lon')

    # Get wind data
    wind_data = loader.get_variable_data('10m_u_component_of_wind')
    assert isinstance(wind_data, xr.DataArray)
    assert wind_data.dims == ('time', 'lat', 'lon')


@pytest.mark.parametrize("variable_name", [
    '2m_temperature',
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    'geopotential'
])
def test_data_variables_exist(mock_gcsfs, mock_xarray, sample_zarr_data, variable_name):
    """Test that all required variables exist in the dataset."""
    mock_xarray.return_value = sample_zarr_data

    loader = DataLoader()
    data = loader.get_variable_data(variable_name)
    assert data is not None
    assert isinstance(data, xr.DataArray)


def test_error_handling():
    """Test error handling when loading dataset fails."""
    with patch('gcsfs.GCSFileSystem') as mock_gcsfs:
        mock_gcsfs.side_effect = Exception("Failed to connect to GCS")

        loader = DataLoader()
        with pytest.raises(Exception) as exc_info:
            _ = loader.dataset

        assert "Failed to connect to GCS" in str(exc_info.value)


def test_data_dimensions(mock_gcsfs, mock_xarray, sample_zarr_data):
    """Test that data dimensions are correct."""
    mock_xarray.return_value = sample_zarr_data

    loader = DataLoader()
    data = loader.get_variable_data('2m_temperature')

    # Check dimensions
    assert 'time' in data.dims
    assert 'lat' in data.dims
    assert 'lon' in data.dims

    # Check coordinates
    assert all(isinstance(coord, (float, np.floating)) for coord in data.lat.values)
    assert all(isinstance(coord, (float, np.floating)) for coord in data.lon.values)


def test_data_ranges(mock_gcsfs, mock_xarray, sample_zarr_data):
    """Test that data values are within expected ranges."""
    mock_xarray.return_value = sample_zarr_data

    loader = DataLoader()
    temp_data = loader.get_variable_data('2m_temperature')
    wind_u_data = loader.get_variable_data('10m_u_component_of_wind')

    # Temperature should be reasonable (in Kelvin)
    assert temp_data.min() >= -100  # Reasonable minimum temperature
    assert temp_data.max() <= 100  # Reasonable maximum temperature

    # Wind speeds should be reasonable
    assert wind_u_data.min() >= -100  # Reasonable minimum wind speed
    assert wind_u_data.max() <= 100  # Reasonable maximum wind speed