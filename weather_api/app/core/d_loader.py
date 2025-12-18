import xarray as xr
import gcsfs
from app.config import settings
import logging
import zarr
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("weather_api")


class ModelType(str, Enum):
    """Enumeration of supported model types."""
    GRAPHCAST = "graphcast"
    CERRORA = "cerrora"
    EXPERIMENTAL = "experimental",
    CERRORA_GT = "cerrora_gt"


@dataclass
class ModelSettings:
    """Data class for model-specific settings."""
    resolution: float
    interpolation_method: str
    use_cache: bool
    zarr_path: str
    lead_time: Optional[List[np.timedelta64]]
    fixed_time_slice: Optional[slice]


class DataLoader:
    """Handles loading and processing of weather data with model-specific configurations."""

    def __init__(self, model_type: Union[str, ModelType] = ModelType.CERRORA):
        """Initialize the data loader with model type.

        Args:
            model_type: Type of weather model to use (graphcast, cerrora, or experimental)
        """
        self.model_type = ModelType(model_type)  # Ensures valid model type
        self.settings = self._get_model_settings()
        self._dataset = None
        self._fs = None

    def _get_model_settings(self) -> ModelSettings:
        settings_map = {
            ModelType.GRAPHCAST: ModelSettings(
                resolution=1.0,
                interpolation_method="cubic",
                use_cache=True,
                zarr_path=settings.GRAPHCAST_INTERPOLATED_ZARR_PATH,
                lead_time=None,
                fixed_time_slice=None
            ),
            ModelType.CERRORA: ModelSettings(
                resolution=0.5,
                interpolation_method="cubic",
                use_cache=True,
                zarr_path=settings.CERRORA_ZARR_PATH,
                lead_time=[np.timedelta64(6, "h")],
                fixed_time_slice=slice(
                    "2021-01-04T00:00:00.000000000", "2021-01-07T06:00:00.000000000"
                 #   "2008-07-01T06:00:00.000000000",
                  #  "2008-07-05T06:00:00.000000000"
                )
            ),
            ModelType.CERRORA_GT: ModelSettings(
                resolution=0.5,
                interpolation_method="cubic",
                use_cache=True,
                zarr_path=settings.CERRORA_GT_ZARR_PATH,
                lead_time=[np.timedelta64(6, "h")],
                fixed_time_slice=slice(
                    "2021-01-04T00:00:00.000000000", "2021-01-07T06:00:00.000000000"
                 #   "2008-07-01T06:00:00.000000000",
                  #  "2008-07-05T06:00:00.000000000"
                )
            ),
            ModelType.EXPERIMENTAL: ModelSettings(
                resolution=0.25,
                interpolation_method="quintic",
                use_cache=False,
                zarr_path=settings.EXPERIMENTAL_ZARR_PATH,
                lead_time=None,
                fixed_time_slice=None
            )
        }
        return settings_map[self.model_type]

    @property
    def dataset(self) -> xr.Dataset:
        if self._dataset is None:
            self._dataset = self._load_dataset()
        return self._dataset

    def _load_dataset(self) -> xr.Dataset:
        """Load the dataset from the configured storage backend.

        Returns:
            xr.Dataset: Loaded dataset

        Raises:
            RuntimeError: If dataset loading fails
        """
        try:
            if self._is_gcs_path(self.settings.zarr_path):
                logger.info("Using Google Cloud Storage backend")
                self._fs = gcsfs.GCSFileSystem()
                store = self._fs.get_mapper(self.settings.zarr_path)
                dset = xr.open_zarr(store,consolidated=True)
                return dset
                #return xr.open_zarr(store, consolidated=True)
            else:
                logger.info("Using local storage backend")
                store = zarr.DirectoryStore(self.settings.zarr_path)
                return xr.open_zarr(store, chunks="auto")
        except Exception as e:
            logger.error(f"Failed to load dataset from {self.settings.zarr_path}: {e}")
            raise RuntimeError(f"Dataset loading failed: {e}")

    @staticmethod
    def _is_gcs_path(path: str) -> bool:
        """Check if the path is a Google Cloud Storage path.

        Args:
            path: Path to check

        Returns:
            bool: True if path is a GCS path (starts with gs://)
        """
        return path.startswith("gs://")

    def get_variable_data(self, variable_name: str) -> xr.DataArray:
        """Get processed data for a specific variable.

        Args:
            variable_name: Name of the variable to retrieve

        Returns:
            xr.DataArray: Processed data for the requested variable
        """
        data = self._load_raw_data(variable_name)

        return self._apply_model_specific_processing(data)

    def _load_raw_data(self, variable_name: str) -> xr.DataArray:
        """Load raw data for a variable from the dataset.

        Args:
            variable_name: Name of the variable to load

        Returns:
            xr.DataArray: Raw data array for the variable
        """
        return self.dataset[variable_name]

    def _apply_model_specific_processing(self, data: xr.DataArray) -> xr.DataArray:
        """Apply model-specific processing to the data.

        Args:
            data: Input data to process

        Returns:
            xr.DataArray: Processed data
        """
        if self.model_type == ModelType.GRAPHCAST:
            return self._apply_standard_processing(data)
        elif self.model_type == ModelType.CERRORA:
            return self._apply_advanced_processing(data)
        elif self.model_type == ModelType.CERRORA_GT:
            return self._apply_advanced_processing(data)
        elif self.model_type == ModelType.EXPERIMENTAL:
            return self._apply_experimental_processing(data)
        return data

    @staticmethod
    def _apply_standard_processing(data: xr.DataArray) -> xr.DataArray:
        """Apply standard data processing."""
        return data

    @staticmethod
    def _apply_advanced_processing(data: xr.DataArray) -> xr.DataArray:
        """Apply advanced data processing techniques."""
        # Add implementation for advanced processing
        return data

    @staticmethod
    def _apply_experimental_processing(data: xr.DataArray) -> xr.DataArray:
        """Apply experimental processing with ML enhancements."""
        # Add implementation for experimental processing
        return data

    def get_zarr_subset(
            self,
            time_slice: Optional[slice] = None,
            variables: Optional[List[str]] = None,
            lead_time: Optional[List[np.timedelta64]] = None,
            levels: Optional[List[int]] = None,
            freq: str = "12h"
    ) -> xr.Dataset:
        """Get a subset of data with model-specific processing.

        Args:
            time_slice: Time period to select (defaults to model's fixed slice if None)
            variables: List of variables to include (defaults to all if None)
            lead_time: Optional list of lead times (defaults to model's lead_time if None)
            levels: Optional list of levels to select
            freq: Frequency string for date range generation

        Returns:
            xr.Dataset: Subset of the dataset with requested parameters
        """
        # Use model defaults if parameters are None
        time_slice = time_slice or self.settings.fixed_time_slice
        lead_time = lead_time or self.settings.lead_time
        variables = variables or list(self.dataset.data_vars.keys())

        date_range = self._create_date_range(time_slice, freq)
        ds_subset = self.dataset[variables]

        if levels:
            ds_subset = ds_subset.sel(level=levels)

        if lead_time:

            ds_subset = ds_subset.sel(time=date_range, prediction_timedelta=lead_time)
        else:
            ds_subset = ds_subset.sel(time=date_range)

        return self._apply_model_specific_processing(ds_subset)

    @staticmethod
    def _create_date_range(time_slice: slice, freq: str) -> pd.DatetimeIndex:
        """Create a date range from a time slice.

        Args:
            time_slice: Time slice to convert to date range
            freq: Frequency string for date range generation

        Returns:
            pd.DatetimeIndex: Generated date range
        """
        if time_slice.start == time_slice.stop:
            # Handle single time point
            dt = pd.Timestamp(time_slice.start)
            return pd.DatetimeIndex([dt])

        # Handle normal date range
        start_dt = pd.Timestamp(time_slice.start)
        end_dt = pd.Timestamp(time_slice.stop)
        return pd.date_range(start=start_dt, end=end_dt, freq=freq)

    @staticmethod
    def adjust_time_slice(
            time_slice: slice,
            timedelta: Tuple[np.timedelta64, np.timedelta64]
    ) -> slice:
        """Adjust a time slice by the given timedelta values.

        Args:
            time_slice: Input time slice to adjust
            timedelta: Tuple of (start_adjustment, end_adjustment) as np.timedelta64

        Returns:
            slice: Adjusted time slice
        """
        new_start = pd.Timestamp(time_slice.start) + timedelta[0]
        new_end = pd.Timestamp(time_slice.stop) + timedelta[1]
        return slice(new_start.isoformat(), new_end.isoformat())

    @staticmethod
    def align_dataset(ds: xr.Dataset) -> xr.Dataset:
        """Align and standardize dataset coordinate names and ordering.

        Args:
            ds: Input xarray Dataset

        Returns:
            xr.Dataset: Aligned and standardized dataset
        """
        # Rename precipitation variable if present
        if "total_precipitation_24hr_from_6hr" in ds.data_vars:
            ds = ds.rename(
                {"total_precipitation_24hr_from_6hr": "total_precipitation_24hr"}
            )

        # Standardize coordinate names
        coord_map = {"lat": "latitude", "lon": "longitude"}
        ds = ds.rename({k: v for k, v in coord_map.items() if k in ds.coords})

        # Ensure latitude is in descending order
        if "latitude" in ds.coords and ds.latitude.values[0] < ds.latitude.values[-1]:
            ds = ds.isel(latitude=ds["latitude"].argsort()[::-1])

        return ds

    @dataset.setter
    def dataset(self, value):
        self._dataset = value
