# app/core/visualization.py
import sys;

from app.core.Visualization.WeatherVisualizer import WeatherVisualizer

sys.setrecursionlimit(5000)
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import os
from typing import Tuple, Optional
import logging
import threading
from app.config import settings

logger = logging.getLogger("weather_api")

# Create a lock object for thread-safe plotting
plot_lock = threading.Lock()


class CerroraVisualizer_graphcast(WeatherVisualizer):
    """Cerrora weather visualization with enhanced graphics and additional features"""

    def __init__(self, uni_lon, uni_lat):
        super().__init__()
        #self.model_type = "cerrora"
        self.uni_lon = uni_lon
        self.uni_lat = uni_lat

    def create_temp_wind_plot(
            self, temp_data, wind_u, wind_v, timestamp_base, timestamp_valid, reverse=True
    ) -> Optional[str]:
        """Creates temperature visualization matching GraphCast format."""
        reverse=True
        with plot_lock:
            try:
                # Create base map
                fig, ax = self._create_cerra_map()
                # Reduce data points by factor of 4 in each dimension
                step = 1
                # For Cerrora, longitude and latitude are already 2D arrays
                lon_2d = self.uni_lon[::step, ::step]
                lat_2d = self.uni_lat[::step, ::step]
                # Handle data selection - if 3D, select first level/time
                temp_values = temp_data.values  # Convert to Celsiu
                print(temp_values.shape)
                if len(temp_values.shape) == 3:
                    temp_values = temp_values[0]  # Select first level/time
                temp_values = temp_values[::step, ::step]  # Reduce data points
                if reverse:
                    temp_values = temp_values[::-1,:]
                # pad the data to the same size as the original data
                temp_values = np.pad(temp_values, ((1069-len(temp_values[0]),0),(0,1069-len(temp_values))), mode='constant', constant_values=np.nan)
                wind_u_values = wind_u.values
                if len(wind_u_values.shape) == 3:
                    wind_u_values = wind_u_values[0]
                wind_u_values = wind_u_values[::step, ::step]  # Reduce data points
                if reverse:
                    wind_u_values = wind_u_values[::-1,:]
                wind_u_values = np.pad(wind_u_values, ((1069-len(wind_u_values[0]),0),(0,1069-len(wind_u_values))), mode='constant', constant_values=np.nan)
                wind_v_values = wind_v.values  
                if len(wind_v_values.shape) == 3:
                    wind_v_values = wind_v_values[0]
                wind_v_values = wind_v_values[::step, ::step]  # Reduce data points
                if reverse:
                    wind_v_values = wind_v_values[::-1,:]
                wind_v_values = np.pad(wind_v_values, ((1069-len(wind_v_values[0]),0),(0,1069-len(wind_v_values))), mode='constant', constant_values=np.nan)
                # Plot temperature contours using reduced 2D coordinates
                ax.contourf(
                    lon_2d,
                    lat_2d,
                    temp_values,
                    levels=np.linspace(-50, 50, 41),
                    cmap='RdBu_r',
                    transform=ccrs.PlateCarree(),
                    extend='both'
                )
                # Add wind barbs with reduced stride (since data is already reduced)
                stride = 16  # Reduced from 8 since data is already subsampled
                i_slice = slice(None, None, stride)
                j_slice = slice(None, None, stride)
                ax.barbs(
                    lon_2d[i_slice, j_slice], 
                    lat_2d[i_slice, j_slice],
                    wind_u_values[i_slice, j_slice],
                    wind_v_values[i_slice, j_slice],
                    transform=ccrs.PlateCarree(),
                    length=3,
                    linewidth=0.3,
                    color='black',
                    alpha=0.5,
                    sizes=dict(spacing=0.2, height=0.3)
                )
                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "graphcast", "tempWind"),
                    filename,
                )
            except Exception as e:
                logger.error(f"Error creating temperature plot: {e}")
                return None

    def create_geo_plot(
            self, geo_data, timestamp_base, timestamp_valid, reverse=True
    ) -> Optional[str]:
        """Creates geopotential visualization matching GraphCast format."""
        reverse=True
        with plot_lock:
            try:
                print("Creating geopotential visualization matching",reverse)
                fig, ax = self._create_cerra_map()
                # Reduce data points by factor of 4
                step = 2
                # Get reduced 2D coordinate arrays
                lon_values = self.uni_lon
                lat_values = self.uni_lat
                lon_reduced = lon_values[::step,::step]
                lat_reduced = lat_values[::step,::step]
                # Handle data selection - if 3D, select the first level/time
                #geo_data = geo_data.sel(pressure_level=500) / 9.80665
                geo_values = geo_data.values
                geo_values = geo_values[::step, ::step]  # Reduce data points

                if reverse:
                    geo_values = geo_values[::-1,:]
                    geo_values = np.pad(geo_values, ((535-len(geo_values[0]),0),(0,535-len(geo_values))), mode='constant', constant_values=np.nan)
                # Plot filled contours using reduced 2D position information
                ax.contourf(
                    lon_reduced,
                    lat_reduced,
                    geo_values,
                    levels=np.linspace(4800, 5800, 41),
                    cmap='viridis',
                    transform=ccrs.PlateCarree(),
                    extend='both'
                )
                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"

                if not reverse:
                    print("✅✅✅✅✅✅✅✅✅✅✅✅✅")
                    filename = f"gt_{timestamp_base}_{timestamp_valid}_image.webp"

                print(f"FILE NAME TO BE SAVED: {filename}")
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "graphcast", "geopotential"),
                    filename,
                )
            except Exception as e:
                logger.error(f"Error creating cerrora geopotential plot.....: {e}")
                return None

    def create_rain_plot(
            self, rain_data, timestamp_base, timestamp_valid, reverse=True
    ) -> Optional[str]:
        """Creates precipitation visualization matching GraphCast format."""
        reverse=True
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
            
                # Reduce data points by factor of 4
                step = 2
                
                # Handle data selection first
                rain_values = rain_data.values
                if len(rain_values.shape) == 3:
                    rain_values = rain_values[0]  # Select first level/time
                
                # Get original coordinate arrays
                lon_values = self.uni_lon
                lat_values = self.uni_lat

                # Reduce coordinates and data consistently
                lon_reduced = lon_values[::step,::step]
                lat_reduced = lat_values[::step,::step]
                rain_values = rain_values[::step, ::step]/1000
                if reverse:
                    rain_values = rain_values[::-1,:]
                rain_values = np.pad(rain_values, ((535-len(rain_values[0]),0),(0,535-len(rain_values))), mode='constant', constant_values=np.nan)
                

                # Determine appropriate max value for precipitation
                vmax = 0.15#max(0.15, float(np.max(rain_values_reduced)))
                
                # Use the reduced data with its 2D position information
                ax.contourf(
                    lon_reduced,
                    lat_reduced,
                    rain_values,
                    levels=np.linspace(0, vmax, 20),
                    cmap='seismic',
                    transform=ccrs.PlateCarree(),
                    extend='both'
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "graphcast", "rain"),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating cerrora precipitation plot: {e}")
                return None

    def create_sea_level_plot(
            self, slp_data, timestamp_base, timestamp_valid, reverse=True
    ) -> Optional[str]:
        """Creates sea level pressure visualization matching GraphCast format."""
        reverse=True
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
            
                # Reduce data points by factor of 4
                step = 2
                
                # Get reduced 2D coordinate arrays
                lon_values = self.uni_lon
                lat_values = self.uni_lat
                lon_reduced = lon_values[::step,::step]
                lat_reduced = lat_values[::step,::step]
                
                # Handle data selection and convert to hPa
                slp_values = slp_data.values
                if len(slp_values.shape) == 3:
                    slp_values = slp_values[0]  # Select first level/time
                slp_values = slp_values[::step, ::step]  # Reduce data points
                if reverse:
                    slp_values = slp_values[::-1,:]
                slp_values = np.pad(slp_values, ((535-len(slp_values[0]),0),(0,535-len(slp_values))), mode='constant', constant_values=np.nan)
                    
                # Convert from Pa to hPa
                data_hpa = slp_values / 100.0
                
                # Plot using reduced 2D coordinates
                ax.contourf(
                    lon_reduced,
                    lat_reduced,
                    data_hpa,
                    levels=np.linspace(980, 1030, 100),
                    cmap='RdYlBu_r',
                    transform=ccrs.PlateCarree(),
                    extend='both'
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"

                if not reverse:
                    filename = f"gt_{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(
                        settings.IMAGE_OUTPUT_DIR, "graphcast", "seaLevelPressure"
                    ),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating cerrora sea level pressure plot: {e}")
                return None
