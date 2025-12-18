# app/core/visualization.py
import sys; sys.setrecursionlimit(5000)
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
from typing import Tuple, Optional
import logging
from urllib.parse import urljoin
from app.config import settings
import cartopy.util as cutil

logger = logging.getLogger("weather_api")

class WeatherVisualizer:
    """Base class for weather visualization"""

    def __init__(self):
        """Initialize base visualizer."""
        #self.model_type = "graphcast" # OLD_VERSION TAKE TO BE REVERSED INCASE
        self.model_type = "cerrora"
        try: #
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
            buffer = 0  # Changed from 100 to 100000 meters
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
                os.path.dirname(__file__), "..","..", "..", directory
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

