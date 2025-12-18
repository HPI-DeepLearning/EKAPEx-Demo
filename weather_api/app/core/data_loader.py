
import xarray as xr
import gcsfs
from app.config import settings
import logging
import zarr

# import dask
import pandas as pd
import numpy as np
import typing as t


logger = logging.getLogger("weather_api")


class DataLoader:
    """Handles loading and processing of weather data."""

    def __init__(self, model_type: str = "cerrora"):
        """Initialize the data loader with model type."""
        self.model_type = model_type
        self._initialize_model_settings()
        self._dataset = None
        self._fs = None

    def _initialize_model_settings(self):
        """Initialize settings based on model type."""
        if self.model_type == "graphcast":
            self.data_resolution = 1.0  # 1.0 degree resolution
            self.interpolation_method = "linear"
            self.use_cache = True
            self.zarr_path = settings.GRAPHCAST_ZARR_PATH
            self.lead_time = None
            self.fixed_time_slice = None
        elif self.model_type == "cerrora":
            self.data_resolution = 0.5  # 0.5 degree resolution
            self.interpolation_method = "cubic"
            self.use_cache = True
            self.zarr_path = settings.CERRORA_ZARR_PATH
            self.lead_time = [
                np.timedelta64(24, "h")
            ]  # Fixed 24-hour lead time for Cerrora
            self.fixed_time_slice = slice(
                "2008-07-01T06:00:00.000000000", "2008-07-05T06:00:00.000000000"
            )  # Fixed time slice for Cerrora at 6 AM
        elif self.model_type == "experimental":
            self.data_resolution = 0.25  # 0.25 degree resolution
            self.interpolation_method = "quintic"
            self.use_cache = False  # Disable cache for experimental features
            self.zarr_path = settings.EXPERIMENTAL_ZARR_PATH
            self.lead_time = None
            self.fixed_time_slice = None
        else:
            raise ValueError(f"Invalid model type: {self.model_type}")

    def _is_gcs_path(self, path: str) -> bool:
        """Check if the path is a Google Cloud Storage path."""
        return path.startswith("gs://")

    @property
    def dataset(self):
        """Lazy loading of the dataset."""
        if self._dataset is None:
            try:
                if self._is_gcs_path(self.zarr_path):
                    self._fs = gcsfs.GCSFileSystem()
                    store = self._fs.get_mapper(self.zarr_path)
                    self._dataset = xr.open_zarr(store, consolidated=True)
                    logger.info("Using Google Cloud Storage backend")
                else:
                    store = zarr.DirectoryStore(self.zarr_path)
                    logger.info("Using local storage backend")
                    self._dataset = xr.open_zarr(store, chunks="auto")
                logger.info(f"Dataset loaded successfully from {self.zarr_path}")
            except Exception as e:
                logger.error(f"Failed to load dataset from {self.zarr_path}: {e}")
                raise
        return self._dataset

    def get_variable_data(self, variable_name: str):
        """Get data for a specific variable with model-specific processing."""

        data = self._load_raw_data(variable_name)

        if self.model_type == "advanced":
            # Apply advanced processing
            data = self._apply_advanced_processing(data)
        elif self.model_type == "experimental":
            # Apply experimental processing with ML enhancements
            data = self._apply_experimental_processing(data)

        return data

    def _apply_advanced_processing(self, data):
        """Apply advanced data processing techniques."""
        # Add implementation for advanced processing
        # Example: Higher resolution interpolation, additional filtering
        return data

    def _apply_experimental_processing(self, data):
        """Apply experimental processing with ML enhancements."""
        # Add implementation for experimental processing
        # Example: ML-based data enhancement, pattern recognition
        return data

    def get_zarr_subset(self, time_slice, variables, lead_time=None, freq="12h"): # freq should be 24 h cerrora 12 hrs for graphcast
        """Get a subset of data with model-specific processing."""
        # Only use fixed settings if no parameters are provided
        if self.model_type == "cerrora" and (time_slice is None or lead_time is None):
            time_slice = self.fixed_time_slice if time_slice is None else time_slice
            lead_time = self.lead_time if lead_time is None else lead_time

        data = self._load_zarr_subset(time_slice, variables, lead_time, freq=freq)

        if self.model_type == "advanced":
            # Apply advanced processing to the subset
            data = self._apply_advanced_processing(data)
        elif self.model_type == "experimental":
            # Apply experimental processing to the subset
            data = self._apply_experimental_processing(data)

        return data

    def _load_raw_data(self, variable_name: str):
        """Load raw data with model-specific settings."""
        # Implementation for loading raw data
        return self.dataset[variable_name]

    def _load_zarr_subset(
        self,
        time_slice: slice,
        variables: t.List[str],
        lead_time: t.Optional[t.List[np.timedelta64]] = None,
        levels: t.Optional[t.List[int]] = None,
        freq: str = "12h",
    ) -> xr.Dataset:
        """
        Load a subset of data from the Zarr store with model-specific settings.

        Args:
            time_slice: Time period to select
            variables: List of variables to include
            lead_time: Optional list of lead times
            levels: Optional list of levels to select
            freq: Frequency string for date range generation

        Returns:
            xr.Dataset: Subset of the dataset
        """
        # if lead_time:
        #    time_slice = self.change_timeslice(time_slice, (-lead_time[-1], -lead_time[-1]))

        # Handle case where time_slice start and stop are the same (single time point)
        if time_slice.start == time_slice.stop:
            if (
                isinstance(time_slice.start, (int, str))
                and str(time_slice.start).isdigit()
            ):
                # Convert unix timestamp to datetime
                dt = pd.Timestamp(int(time_slice.start), unit="s")
            else:
                dt = pd.Timestamp(time_slice.start)
            date_range = pd.DatetimeIndex([dt])
        else:
            # Normal date range case
            if (
                isinstance(time_slice.start, (int, str))
                and str(time_slice.start).isdigit()
            ):
                start_dt = pd.Timestamp(int(time_slice.start), unit="s")
                end_dt = pd.Timestamp(int(time_slice.stop), unit="s")
            else:
                start_dt = pd.Timestamp(time_slice.start)
                end_dt = pd.Timestamp(time_slice.stop)
            date_range = pd.date_range(start=start_dt, end=end_dt, freq=freq)
        ds_subset = self.dataset[variables]

        if levels:
            ds_subset = ds_subset.sel(level=levels)

        if lead_time:
            ds_subset = ds_subset.sel(time=date_range, prediction_timedelta=lead_time)
        else:
            ds_subset = ds_subset.sel(time=date_range)

        return ds_subset

    @staticmethod
    def change_timeslice(
        time_slice: slice, timedelta: t.Tuple[np.timedelta64, np.timedelta64]
    ) -> slice:
        """
        Adjust a time slice by the given timedelta values.

        Args:
            time_slice: Input time slice to adjust
            timedelta: Tuple of (start_adjustment, end_adjustment) as np.timedelta64

        Returns:
            slice: Adjusted time slice
        """
        new_start_time = pd.Timestamp(time_slice.start) + timedelta[0]
        new_end_time = pd.Timestamp(time_slice.stop) + timedelta[1]
        new_timeslice = slice(
            new_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            new_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        return new_timeslice

    def align_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Align and standardize dataset coordinate names and ordering.

        Args:
            ds: Input xarray Dataset

        Returns:
            xr.Dataset: Aligned and standardized dataset
        """
        # Rename FuXi precipitation variable
        if "total_precipitation_24hr_from_6hr" in ds.data_vars:
            ds = ds.rename(
                {"total_precipitation_24hr_from_6hr": "total_precipitation_24hr"}
            )

        # Rename lat->latitude and lon->longitude axes
        if "lat" in ds.coords:
            ds = ds.rename({"lat": "latitude"})
        if "lon" in ds.coords:
            ds = ds.rename({"lon": "longitude"})
        ds = ds.set_index(
            longitude="longitude", latitude="latitude"
        )  # Make renamed coordinates indexed

        # Order latitude coordinates by descending order
        if ds.latitude.values[0] < ds.latitude.values[-1]:
            ds = ds.isel(latitude=ds["latitude"].argsort()[::-1])

        return ds
