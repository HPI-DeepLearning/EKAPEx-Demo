# app/core/visualization.py
import sys; sys.setrecursionlimit(5000)
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os
from typing import Tuple, Optional
import logging
from urllib.parse import urljoin
import threading
from app.config import settings
import cartopy.util as cutil

logger = logging.getLogger("weather_api")

# Create a lock object for thread-safe plotting
plot_lock = threading.Lock()

NATURALEARTH_URL = (
    "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
)


class WeatherVisualizer:
    """Base class for weather visualization"""

    def __init__(self):
        """Initialize base visualizer."""
        self.model_type = "graphcast"
        try:
            logger.info("Initializing WeatherVisualizer...")
            # Cache the projection
            self.projection = ccrs.LambertConformal(
                central_longitude=8,
                central_latitude=50,
                standard_parallels=(50, 50),
                globe=ccrs.Globe(semimajor_axis=6371229),
            )
            logger.info("Created Lambert Conformal projection")

            # Cache the corner coordinates and their projections
            self.corners = {
                "Upper-left": (-58.1051, 63.7695),
                "Upper-right": (74.1051, 63.7695),
                "Lower-right": (33.4859, 20.2923),
                "Lower-left": (-17.4859, 20.2923),
            }
            logger.info(f"Corner coordinates: {self.corners}")

            # Pre-compute projected corners
            self.projected_corners = {}
            for name, (lon, lat) in self.corners.items():
                x, y = self.projection.transform_point(lon, lat, ccrs.PlateCarree())
                self.projected_corners[name] = (x, y)
                logger.info(f"Projected corner {name}: ({x}, {y})")

            # Pre-compute extent with buffer
            buffer = 100000  # Changed from 100 to 100000 meters
            x_min = min(c[0] for c in self.projected_corners.values())
            x_max = max(c[0] for c in self.projected_corners.values())
            y_min = min(c[1] for c in self.projected_corners.values())
            y_max = max(c[1] for c in self.projected_corners.values())

            self.extent = [
                x_min - buffer,
                x_max + buffer,
                y_min - buffer,
                y_max + buffer,
            ]
            logger.info(f"Computed extent with buffer: {self.extent}")

            # Cache common features
            self.coastlines = cfeature.NaturalEarthFeature(
                "physical",
                "coastline",
                "50m",
                edgecolor="black",
                facecolor="none",
                linewidth=0.5,
            )
            self.borders = cfeature.NaturalEarthFeature(
                "cultural",
                "admin_0_boundary_lines_land",
                "50m",
                edgecolor="black",
                facecolor="none",
                linewidth=0.5,
            )
            self.land = cfeature.NaturalEarthFeature(
                "physical",
                "land",
                "50m",
                edgecolor="face",
                facecolor="lightgray",
                alpha=0.3,
            )
            logger.info("Cached map features")
        except Exception as e:
            logger.error(
                f"Error in WeatherVisualizer initialization: {e}", exc_info=True
            )
            raise

    def _create_base_map(
        self, figsize: Tuple[int, int] = (12, 6)
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Creates a base map for plotting."""
        fig = plt.figure(figsize=figsize)
        ax = plt.axes(projection=ccrs.PlateCarree())

        if hasattr(self, "world") and self.world is not None:
            # Use GeoPandas world map if available
            self.world.boundary.plot(
                ax=ax,
                linewidth=0.5,
                edgecolor="black",
                facecolor="none",
                transform=ccrs.PlateCarree(),
            )
        else:
            # Fallback to cartopy features
            ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor="black")
            ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="gray")
            ax.add_feature(cfeature.LAND, facecolor="lightgray", alpha=0.3)

        # Set global extent
        ax.set_global()
        return fig, ax

    def _save_plot(
        self, fig: plt.Figure, directory: str, filename: str
    ) -> Optional[str]:
        """Saves the plot to a file and returns the URL."""
        try:
            directory_path = os.path.join(
                os.path.dirname(__file__), "..", "..", directory
            )
            os.makedirs(directory_path, exist_ok=True)
            filepath = os.path.join(directory_path, filename)

            # If file exists and is accessible, return its URL immediately
            if os.path.exists(filepath) and os.access(filepath, os.R_OK):
                return urljoin(
                    f"{settings.BASE_URL}/",
                    os.path.join(os.path.basename(directory), filename),
                )

            # Optimize figure for saving
            ax = plt.gca()
            ax.set_axis_off()
            plt.subplots_adjust(0, 0, 1, 1, 0, 0)
            ax.margins(0)
            ax.xaxis.set_major_locator(plt.NullLocator())
            ax.yaxis.set_major_locator(plt.NullLocator())

            # Save with optimized settings
            temp_filepath = f"{filepath}.tmp"
            plt.savefig(
                temp_filepath,
                format="webp",
                bbox_inches="tight",
                pad_inches=0,
                facecolor="white",
                dpi=300,
            )

            # Atomic rename
            os.replace(temp_filepath, filepath)
            logger.info(f"Saved plot to {filepath}")
            return urljoin(
                f"{settings.BASE_URL}/",
                os.path.join(os.path.basename(directory), filename),
            )

        except Exception as e:
            logger.error(f"Error saving plot: {e}")
            if "temp_filepath" in locals() and os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except Exception:
                    pass
            return None
        finally:
            plt.close(fig)

    def _create_cerra_map(self) -> Tuple[plt.Figure, plt.Axes]:
        """Creates a base map with CERRA projection and boundaries."""
        try:
            logger.info("Creating CERRA map...")
            # Create figure with the correct projection
            fig = plt.figure(figsize=(12, 12))
            ax = plt.axes(projection=self.projection)
            logger.info("Created figure and axes with projection")

            # Set map extent with a small buffer
            logger.info(f"Setting extent to: {self.extent}")
            ax.set_extent(self.extent, crs=self.projection)
            logger.info("Set map extent")

            # Add coastlines and borders
            ax.add_feature(self.coastlines)
            ax.add_feature(self.borders)
            ax.add_feature(self.land)
            logger.info("Added map features")

            return fig, ax
        except Exception as e:
            logger.error(f"Error creating CERRA map: {e}", exc_info=True)
            raise

    def _prepare_data(self, data, lon):
        """Prepare data for plotting by adding cyclic point."""
        try:
            logger.info("Preparing data for plotting...")
            # Convert xarray DataArray to numpy array
            if hasattr(data, "values"):
                data = data.values
                logger.info("Converted xarray DataArray to numpy array")

            # Add cyclic point
            cyclic_data, cyclic_lons = cutil.add_cyclic_point(data, coord=lon)
            logger.info(
                f"Added cyclic point. Data shape: {cyclic_data.shape}, Lons shape: {cyclic_lons.shape}"
            )

            return cyclic_data, cyclic_lons
        except Exception as e:
            logger.error(f"Error preparing data: {e}", exc_info=True)
            raise


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
                    levels=np.linspace(-50, 50, 41),
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


class CerroraVisualizer(WeatherVisualizer):
    """Cerrora weather visualization with enhanced graphics and additional features"""

    def __init__(self):
        super().__init__()
        self.model_type = "cerrora"

    def create_temp_wind_plot(
        self, temp_data, wind_u, wind_v, timestamp_base, timestamp_valid
    ) -> Optional[str]:
        """Creates temperature visualization matching GraphCast format."""
        with plot_lock:
            try:
                # Create base map
                fig, ax = self._create_cerra_map()

                # Plot temperature contours using direct position information
                ax.contourf(
                    temp_data["lon"].values,
                    temp_data["lat"].values,
                    temp_data.values,
                    levels=np.linspace(-50, 50, 41),
                    cmap="RdBu_r",
                    transform=self.projection,
                    extend="both",
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "cerrora", "tempWind"),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating temperature plot: {e}")
                return None

    def create_geo_plot(
        self, geo_data, timestamp_base, timestamp_valid
    ) -> Optional[str]:
        """Creates geopotential visualization matching GraphCast format."""
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()

                # If the data is 3D, select the first level/time
                if len(geo_data.shape) == 3:
                    logger.info(
                        f"Received 3D data with shape {geo_data.shape}, selecting first level"
                    )
                    geo_data = geo_data.isel(
                        level=0
                    )  # Or time=0 depending on the dimension name

                # Plot filled contours using direct position information
                geo_contour = ax.contourf(
                    geo_data["longitude"].values,
                    geo_data["latitude"].values,
                    geo_data.values,
                    levels=np.linspace(4800, 5800, 41),  # Match GraphCast levels
                    cmap="viridis",
                    transform=self.projection,
                    extend="both",
                )

                # Add colorbar with consistent style
                plt.colorbar(
                    geo_contour,
                    ax=ax,
                    label="Geopotential Height (m)",
                    orientation="horizontal",
                    pad=0.05,
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "cerrora", "geopotential"),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating cerrora geopotential plot: {e}")
                return None

    def create_rain_plot(
        self, rain_data, timestamp_base, timestamp_valid
    ) -> Optional[str]:
        """Creates precipitation visualization matching GraphCast format."""
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
                values = -rain_data.values / 1000

                # Plot precipitation using seismic colormap to match GraphCast
                vmin, vmax = 0, min(0.15, float(np.max(values)))

                # Use the data directly with its position information
                ax.contourf(
                    rain_data["longitude"].values,
                    rain_data["latitude"].values,
                    values,
                    levels=np.linspace(vmin, vmax, 20),  # Match GraphCast levels
                    cmap="seismic",
                    transform=self.projection,
                    extend="both",
                )

                filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
                return self._save_plot(
                    fig,
                    os.path.join(settings.IMAGE_OUTPUT_DIR, "cerrora", "rain"),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating cerrora precipitation plot: {e}")
                return None

    def create_sea_level_plot(
        self, slp_data, timestamp_base, timestamp_valid
    ) -> Optional[str]:
        """Creates sea level pressure visualization matching GraphCast format."""
        with plot_lock:
            try:
                fig, ax = self._create_cerra_map()
                lon, lat = np.meshgrid(
                    slp_data["longitude"].values, slp_data["latitude"].values
                )

                # Convert to hPa and prepare data in one go
                data_hpa = slp_data.values / 100.0
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
                        settings.IMAGE_OUTPUT_DIR, "cerrora", "seaLevelPressure"
                    ),
                    filename,
                )

            except Exception as e:
                logger.error(f"Error creating cerrora sea level pressure plot: {e}")
                return None


class ExperimentalVisualizer(WeatherVisualizer):
    """Experimental weather visualization with cutting-edge features and ML-enhanced graphics"""

    def __init__(self):
        super().__init__()
        self.model_type = "experimental"

    def create_temp_wind_plot(
        self, temp_data, wind_u, wind_v, timestamp_base, timestamp_valid
    ):
        # Experimental temperature and wind visualization with ML-enhanced features
        # Add features like predictive wind patterns, anomaly detection, etc.
        pass

    def create_geo_plot(self, geo_data, timestamp_base, timestamp_valid):
        # Experimental geopotential visualization with ML-based pattern recognition
        pass

    def create_rain_plot(self, rain_data, timestamp_base, timestamp_valid):
        # Experimental precipitation visualization with precipitation type prediction
        pass

    def create_sea_level_plot(self, slp_data, timestamp_base, timestamp_valid):
        # Experimental sea level pressure visualization with weather system identification
        pass
