# app/core/visualization.py
import sys;

from app.core.Visualization.WeatherVisualizer import WeatherVisualizer

sys.setrecursionlimit(5000)
import cartopy.crs as ccrs
import numpy as np
import os
from typing import Optional
import logging
import threading
from app.config import settings

logger = logging.getLogger("weather_api")
# Create a lock object for thread-safe plotting
plot_lock = threading.Lock()


class GraphCastVisualizer(WeatherVisualizer):
    """GraphCast weather visualization implementation"""

    def __init__(self):
        super().__init__()
        self.model_type = "graphcast"

    def create_temp_wind_plot(
            self,
            data_temp,
            data_wind_u,
            data_wind_v,
            timestamp_base: int,
            timestamp_valid: int,
    ) -> Optional[str]:
        """Creates temperature and wind visualization."""
        with plot_lock:
            try:
                # Create base map
                fig, ax = self._create_cerra_map()

                # Create meshgrid once and reuse
                lon, lat = np.meshgrid(data_temp["lon"].values, data_temp["lat"].values)

                # Plot temperature contours
                cyclic_temp, cyclic_lons = self._prepare_data(data_temp, lon[0])
                ax.contourf(
                    cyclic_lons,
                    lat[:, 0],
                    cyclic_temp,
                    levels=np.linspace(-50, 50, 100),
                    cmap="RdBu_r",
                    transform=ccrs.PlateCarree(),
                    extend="both",
                )

                # Optimize wind barbs plotting
                stride = 8
                # Pre-compute indices for slicing
                i_slice = slice(None, None, stride)
                # Use numpy's advanced indexing for better performance
                ax.barbs(
                    lon[i_slice, i_slice],
                    lat[i_slice, i_slice],
                    data_wind_u.values[i_slice, i_slice],
                    data_wind_v.values[i_slice, i_slice],
                    transform=ccrs.PlateCarree(),
                    length=3,
                    linewidth=0.3,
                    color="black",
                    alpha=0.5,
                    sizes=dict(spacing=0.2, height=0.3),
                )

                # Save plot
                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "graphcast", "tempWind"),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating temperature and wind plot: {e}")
                return None

    def create_geo_plot(
            self, data_geo, timestamp_base: int, timestamp_valid: int
    ) -> Optional[str]:
        """Creates geopotential visualization."""
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
                lon, lat = np.meshgrid(data_geo["lon"].values, data_geo["lat"].values)
                cyclic_geo, cyclic_lons = self._prepare_data(data_geo, lon[0])

                ax.contourf(
                    cyclic_lons,
                    lat[:, 0],
                    cyclic_geo,
                    levels=np.linspace(4800, 5800, 41),
                    cmap="viridis",
                    transform=ccrs.PlateCarree(),
                    extend="both",
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(
                        settings.IMAGE_OUTPUT_DIR, "graphcast", "geopotential"
                    ),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating geopotential plot: {e}")
                return None

    def create_rain_plot(
            self, data_rain, timestamp_base: int, timestamp_valid: int
    ) -> Optional[str]:
        """Creates precipitation visualization."""
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
                lon, lat = np.meshgrid(data_rain["lon"].values, data_rain["lat"].values)

                vmin, vmax = 0, min(0.15, float(np.max(data_rain)))
                cyclic_data, cyclic_lons = self._prepare_data(data_rain, lon[0])

                ax.contourf(
                    cyclic_lons,
                    lat[:, 0],
                    cyclic_data,
                    levels=np.linspace(vmin, vmax, 20),
                    cmap="seismic",
                    transform=ccrs.PlateCarree(),
                    extend="both",
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "graphcast", "rain"),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating precipitation plot: {e}")
                return None

    def create_sea_level_plot(
            self, data_sea_level, timestamp_base: int, timestamp_valid: int
    ) -> Optional[str]:
        """Creates sea level pressure visualization."""
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
                lon, lat = np.meshgrid(
                    data_sea_level["lon"].values, data_sea_level["lat"].values
                )

                # Convert to hPa and prepare data in one go
                data_hpa = data_sea_level / 100.0
                cyclic_data, cyclic_lons = self._prepare_data(data_hpa, lon[0])

                ax.contourf(
                    cyclic_lons,
                    lat[:, 0],
                    cyclic_data,
                    levels=np.linspace(980, 1030, 41),
                    cmap="RdYlBu_r",
                    transform=ccrs.PlateCarree(),
                    extend="both",
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(
                        settings.IMAGE_OUTPUT_DIR, "graphcast", "seaLevelPressure"
                    ),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating sea level pressure plot: {e}")
                return None
