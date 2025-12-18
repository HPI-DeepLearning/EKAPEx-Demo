from typing import Callable, TypedDict
from urllib.parse import urljoin
import logging
from fastapi import HTTPException
import pandas as pd
import logging
from typing import List,Optional
import numpy as np
import xarray as xr
from app.api.models import TimeRange
import os
from app.config import settings
import httpx
import requests
import random
import pdb
import json

from datetime import datetime, timezone
from app.core.d_loader import DataLoader

logger = logging.getLogger("weather_api")

class VariableMap(TypedDict):
    temp_wind: str
    geo: str
    rain: str
    sea_level: str


variable_map_graphcast: VariableMap = {
    "temp_wind": "2m_temperature",
    "geo": "geopotential",
    "rain": "total_precipitation_6hr",
    "sea_level": "mean_sea_level_pressure",
}
variable_map_cerrora: VariableMap = {
    "temp_wind": "t",  # "2t",
    "geo": "z",
    "rain": "tp",
    "sea_level": "msl",
}


async def get_images(var_type: str, base_time: str):  # sort out the mane issue...
    base_api_url = "http://127.0.0.1:8000/api/v1"  # better name configuration
    valid_times = [];
    image_list = [];
    async with httpx.AsyncClient() as client:  # 1609761600
        response_valid_times = await client.get(
            f"{base_api_url}/valid-times?variableType={var_type}&queryTime={base_time}")
        res_valid_times = response_valid_times.json()
        for cur_time in res_valid_times[0]:
            valid_times.append(cur_time["value"])
        prep_req_body = {"baseTime": base_time, "validTime": valid_times};

        response_post_variable_type = await client.post(f"{base_api_url}/data/{var_type}", json=prep_req_body)
        res_base_time_data = response_post_variable_type.json()
        for i in res_base_time_data["images"]:
            image_list.append(i["url"].split("/")[-1])
    return image_list;


def process_url(url: str, model_type: str):
    split_url = url.split("streaming")
    return split_url[0] + "streaming/" + model_type + split_url[1]


def filter_images(images, base_time, ground_truth_generate=False):
    base_time = str(base_time)
    if ground_truth_generate:
        filtered_img = [
            img for img in images
            if img.split("_")[0] == "gt" and img.split("_")[1] == base_time
        ]
    else:
        filtered_img = [
            img for img in images
            if img.split("_")[0] == base_time
        ]
    return filtered_img


async def process_data(
        time_range: TimeRange,
        loaders: tuple,
        plot_type: str,
        descriptive_logger_info: str,
        graph_cast_variable_type: str,
        cerrora_variable_type,
        get_existing_images: Callable,
        get_cached_image_path: Callable
):
    logger = logging.getLogger("weather_api")
    """Generate geopotential visualization for specified time range."""
    data_loader, visualizer, model_type = loaders
    try:
        # First check for existing images
        existing_images = get_existing_images(
            time_range, plot_type, model_type
        )  # define plot type as param

        # Check if all images exist
        if len(existing_images) == len(time_range.validTime):
            logger.info(descriptive_logger_info)
            return {
                "images": [
                    {
                        "timestamp": img["timestamp"],
                        "url": urljoin(f"{settings.BASE_URL}/", img["url"]),
                    }
                    for img in existing_images
                ]
            }

        # If not all images exist, generate missing ones
        images_info = []
        base_datetime = pd.to_datetime(time_range.baseTime, unit="s")
        base_datetime = pd.Timestamp(base_datetime).to_datetime64()

        # Load data once for all images
        if model_type == "graphcast":
            ds_variable_data = data_loader.get_variable_data(
                graph_cast_variable_type
            )  # define as parameter
        elif model_type == "cerrora":
            ds_variable_data = data_loader.get_variable_data(
                cerrora_variable_type
            )  # define as parameter
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        for valid_time in time_range.validTime:
            valid_datetime = pd.to_datetime(valid_time, unit="s")
            timestamp_base = int(pd.Timestamp(base_datetime).timestamp())
            timestamp_valid = int(valid_datetime.timestamp())

            # Check for cached image
            cached_url = get_cached_image_path(
                timestamp_base,
                timestamp_valid,
                plot_type,
                model_type,  # define plot type as param
            )
            if cached_url:
                images_info.append(
                    {
                        "timestamp": f"{timestamp_base}_{timestamp_valid}",
                        "url": urljoin(f"{settings.BASE_URL}/", cached_url),
                    }
                )
                continue

            # Generate new image
            time_difference = pd.Timedelta(valid_datetime - base_datetime)
            ds_variable_data = ds_variable_data.sel(
                time=base_datetime, method="nearest"
            )
            ds_variable_data = ds_variable_data.sel(
                prediction_timedelta=time_difference, method="nearest"
            )

            if plot_type == "geo":
                if "level" in ds_variable_data.dims:
                    ds_variable_data = ds_variable_data.sel(level=500) / 9.80665

            url = visualizer.create_geo_plot(
                ds_variable_data, timestamp_base, timestamp_valid
            )

            if url:
                images_info.append(
                    {"timestamp": f"{timestamp_base}_{timestamp_valid}", "url": url}
                )

        return {"images": images_info}

    except Exception as e:
        logger.error(f"Error generating {plot_type} visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))





async def fetch_valid_times(variableType: Optional[str], query_time: Optional[str], loaders: tuple) -> List[List[dict]]:
    """Get available valid times for predictions."""
    data_loader, _, model_type = loaders
    try:
        # Use query_time if provided, otherwise use default
        if query_time:
            # query_time = pd.Timestamp(int(query_time), unit="s").isoformat()
            # query_time = query_time.split("T")[0]
            # time_slice = slice(query_time, query_time)
            try:
                parsed_query_time = int(query_time)
                query_time = pd.Timestamp(int(parsed_query_time), unit="s").isoformat()
                if model_type == "graphcast":
                    query_time = query_time.split("T")[0]  # Splitting it base on T works fine for graphcast
                time_slice = slice(query_time, query_time)
            except:
                time_slice = slice(query_time, query_time)
        else:
            time_slice = (
                # slice("2021-01-01", "2021-01-05") # line right before the immediate one below.
                slice("2021-01-01", "2021-01-12")
                if model_type == "graphcast"
                else slice(
                    # "2008-07-01T06:00:00.000000000", "2008-07-05T06:00:00.000000000"
                    # "2001-07-01T06:00:00.000000000", "2001-07-05T06:00:00.000000000"
                    #"2020-01-04T06:00:00.000000000", "2020-01-09T06:00:00.000000000"  # line right before the immediate one below.
                    "2021-01-01T06:00:00.000000000", "2021-01-12T06:00:00.000000000"
                )
            )
        logger.info(
            f"Getting valid times for model_type: {model_type}, variableType: {variableType}, query_time: {query_time}"
        )

        # Handle Cerrora model differently
        if model_type == "cerrora":
            """make it dynamic fetching."""
            #LEAD_TIMES = [np.timedelta64(24, "h")]  # 24 # inspect this line....!!!!! note it was 12
            LEAD_TIMES = [np.timedelta64(hours, "h") for hours in range(6, 31, 6)]
            freq = "6h"
            if query_time is None:
                # Use a default time for Cerrora if none provided
                #query_time = "2008-07-01T06:00:00.000000000"  # line right before the immediate one below.
                query_time = "2021-01-01T06:00:00.000000000"
        else:
            LEAD_TIMES = [np.timedelta64(hours, "h") for hours in range(6, 31, 6)]
            freq = "6h"
            if query_time is None:
                # Use a default time for GraphCast if none provided
                #query_time = "2020-01-01"  # line right before the immediate one below.
                query_time = "2021-01-01"
        if model_type == "graphcast":
            variable_map = variable_map_cerrora
            # time_slice = slice('2020-01-01', '2020-01-05')
        elif model_type == "cerrora":
            variable_map = variable_map_cerrora
            # time_slice = slice('2008-07-01T06:00:00.000000000', '2008-07-05T06:00:00.000000000')
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        # Validate input
        if variableType == "tempWind": variableType = "temp_wind"
        variable = variable_map.get(variableType)
        if not variable:
            raise HTTPException(
                status_code=400, detail=f"Invalid variable type: {variableType}"
            )

        # Convert query_time to datetime if it's a timestamp
        if query_time and query_time.isdigit():
            query_time = pd.Timestamp(int(query_time), unit="s").isoformat()
            query_time = query_time.split("T")[0]
            logger.info(f"Converted timestamp query_time to: {query_time}")

        # Prepare time slice

        logger.info(f"Initial time_slice: {time_slice}")

        # Get data subset
        try:
            ds = data_loader.get_zarr_subset(
                time_slice=time_slice,
                variables=[variable],
                lead_time=LEAD_TIMES,
                freq=freq,
            )
            logger.info(f"Successfully loaded zarr subset with dimensions: {ds.dims}")
        except Exception as e:
            logger.error(f"Error loading zarr subset: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

        # Process times efficiently using vectorized operations
        base_times = [query_time]
        logger.info(f"Retrieved base_times: {base_times}")

        if len(base_times) == 0:
            logger.warning("No base times found in dataset")
            return []

        valid_times = []
        for base_time in base_times:
            time_list = []
            base_timestamp = pd.Timestamp(base_time)

            for lead_time in LEAD_TIMES:
                try:
                    # Calculate valid time by adding lead time to base time
                    valid_timestamp = base_timestamp + lead_time

                    time_entry = {
                        "label": valid_timestamp.strftime("%a %d %b %Y %H UTC"),
                        "value": str(int(valid_timestamp.timestamp())),
                    }
                    time_list.append(time_entry)
                    logger.debug(f"Processed time entry: {time_entry}")
                except (ValueError, TypeError) as e:
                    logger.error(
                        f"Error processing timestamp: {base_time} + {lead_time}, Error: {e}"
                    )
                    continue

            if time_list:  # Only append if we have valid times
                valid_times.append(time_list)

        logger.info(f"Returning {len(valid_times)} sets of valid times")
        return valid_times

    except Exception as e:
        logger.error(f"Error getting valid times: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def get_cached_image_path(
        timestamp_base: int, timestamp_valid: int, plot_type: str, model_type: str
) -> Optional[str]:
    """Check if an image already exists for the given timestamps and plot type."""
    # Map plot types to their directories
    try:
        plot_dir_map: VariableMap = {
            "temp_wind": "tempWind",
            "geo": "geopotential",
            "rain": "rain",
            "sea_level": "seaLevelPressure",
        }

        if (directory := plot_dir_map.get(plot_type)) is None:
            return None

        # Construct the full path including model type
        image_dir = os.path.join(settings.IMAGE_OUTPUT_DIR, model_type, directory)
        filename = f"{timestamp_base}_{timestamp_valid}_image.webp"
        filepath = os.path.join(image_dir, filename)
        # Check if file exists and is readable
        if os.path.exists(filepath) and os.access(filepath, os.R_OK):
            logger.info(f"Found existing image: {filepath}")
            # Return path that includes model type
            return os.path.join(model_type, directory, filename)

        return None
    except Exception as e:
        logger.error(f"Error checking cached image: {e}")
        return None

def get_existing_images(time_range: TimeRange, plot_type: str, model_type: str) -> List[dict]:
    """Get all existing images for a given time range and plot type."""
    images_info = []
    base_datetime = pd.to_datetime(time_range.baseTime, unit="s")
    base_timestamp = int(pd.Timestamp(base_datetime).timestamp())

    for valid_time in time_range.validTime:
        valid_timestamp = int(valid_time)
        cached_url = get_cached_image_path(
            base_timestamp, valid_timestamp, plot_type, model_type
        )
        if cached_url:
            images_info.append(
                {"timestamp": f"{base_timestamp}_{valid_timestamp}", "url": cached_url}
            )

    return images_info
async def fetch_temp_wind_data(
        time_range: TimeRange, loaders: tuple
):
    """Get temperature and wind data visualization for the specified time range."""
    data_loader, visualizer, model_type = loaders
    gt_data_loader = None
    gt_ds_temp = None
    gt_ds_wind_u = None
    gt_ds_wind_v = None

    try:
        # First check for existing images
        existing_images = get_existing_images(time_range, "temp_wind", model_type)
        # Check if all images exist
        if len(existing_images) == len(time_range.validTime):
            logger.info("All temp_wind images found in cache")
            return {
                "images": [
                    {
                        "timestamp": img["timestamp"],
                        "url": urljoin(f"{settings.BASE_URL}/", img["url"]),
                    }
                    for img in existing_images
                ]
            }
        # If not all images exist, generate missing ones
        images_info = []
        base_datetime = pd.to_datetime(time_range.baseTime, unit="s")
        base_datetime = pd.Timestamp(base_datetime).to_datetime64()

        # Load data once for all images
        if model_type == "cerrora":
            gt_data_loader = DataLoader(model_type="cerrora_gt")

            ds_temp = data_loader.get_variable_data("t2m")  # ("2t")
            ds_wind_u = data_loader.get_variable_data("10u")
            ds_wind_v = data_loader.get_variable_data("10v")

            gt_ds_temp = gt_data_loader.get_variable_data("t2m")
            gt_ds_wind_u = gt_data_loader.get_variable_data("10u")
            gt_ds_wind_v = gt_data_loader.get_variable_data("10v")
            # pass
        else:
            #ds_temp = data_loader.get_variable_data("2m_temperature")
            #ds_wind_u = data_loader.get_variable_data("10m_u_component_of_wind")
            #ds_wind_v = data_loader.get_variable_data("10m_v_component_of_wind")
            ds_temp = data_loader.get_variable_data("t2m") 
            ds_wind_u = data_loader.get_variable_data("10u")
            ds_wind_v = data_loader.get_variable_data("10v")

        track = 0
        for valid_time in time_range.validTime:
            valid_datetime = pd.to_datetime(valid_time, unit="s")
            timestamp_base = int(pd.Timestamp(base_datetime).timestamp())
            timestamp_valid = int(valid_datetime.timestamp())

            # Check for cached image
            cached_url = get_cached_image_path(
                timestamp_base, timestamp_valid, "temp_wind", model_type
            )
            if cached_url:
                images_info.append(
                    {
                        "timestamp": f"{timestamp_base}_{timestamp_valid}",
                        "url": urljoin(f"{settings.BASE_URL}/", cached_url),
                    }
                )
                continue
            time_difference = pd.Timedelta(valid_datetime - base_datetime)
            if gt_data_loader is not None:
                gt_data_temp = gt_ds_temp.sel(time=valid_datetime, method="nearest") - 273.15
                gt_data_wind_u = gt_ds_wind_u.sel(time=valid_datetime, method="nearest")
                gt_data_wind_v = gt_ds_wind_v.sel(time=valid_datetime, method="nearest")

                visualizer.create_temp_wind_plot(gt_data_temp, gt_data_wind_u, gt_data_wind_v, timestamp_base, timestamp_valid,reverse=False)

            # Generate new image
            data_temp = ds_temp.sel(time=base_datetime, method="nearest")
            data_wind_u = ds_wind_u.sel(time=base_datetime, method="nearest")
            data_wind_v = ds_wind_v.sel(time=base_datetime, method="nearest")

            data_temp = (data_temp.sel(prediction_timedelta=time_difference, method="nearest") - 273.15)
            data_wind_u = data_wind_u.sel(prediction_timedelta=time_difference, method="nearest")
            data_wind_v = data_wind_v.sel(prediction_timedelta=time_difference, method="nearest")
            url = visualizer.create_temp_wind_plot(
                data_temp, data_wind_u, data_wind_v, timestamp_base, timestamp_valid
            )
            if url:
                images_info.append(
                    {
                        "timestamp": f"{timestamp_base}_{timestamp_valid}",
                        "url": process_url(url, model_type)  # url
                    }
                )
            track = track +1
        return {"images": images_info}

    except Exception as e:
        logger.error(
            f"Error generating temp_wind visualization: {str(e)}"
        )  # ERROR CONTENT: module 'zarr' has no attribute 'DirectoryStore'
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



async def fetch_geo_data(time_range: TimeRange,loaders: tuple):
    """Generate geopotential visualization for specified time range."""
    data_loader, visualizer, model_type = loaders

    gt_data_loader = None
    gt_ds_geo = None;
    try:
        # First check for existing images
        existing_images = get_existing_images(time_range, "geo", model_type)
        # Check if all images exist
        if len(existing_images) == len(time_range.validTime):
            logger.info("All geopotential images found in cache")
            return {"images": [
                {"timestamp": img["timestamp"],
                 "url": urljoin(f"{settings.BASE_URL}/", img["url"])}
                for img in existing_images
            ]}
        # If not all images exist, generate missing ones
        images_info = []
        base_datetime = pd.to_datetime(time_range.baseTime, unit='s')
        base_datetime = pd.Timestamp(base_datetime).to_datetime64()
        # Load data once for all images
        if model_type == 'graphcast':
            #ds_geo = data_loader.get_variable_data('geopotential')
            ds_geo = data_loader.get_variable_data('z')
        elif model_type == 'cerrora':
            ds_geo = data_loader.get_variable_data('z')
            gt_data_loader = DataLoader(model_type="cerrora_gt")
            gt_ds_geo = gt_data_loader.get_variable_data("z")
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        for valid_time in time_range.validTime:
            valid_datetime = pd.to_datetime(valid_time, unit='s')
            timestamp_base = int(pd.Timestamp(base_datetime).timestamp())
            timestamp_valid = int(valid_datetime.timestamp())
            # Check for cached image
            cached_url = get_cached_image_path(timestamp_base, timestamp_valid, "geo", model_type)
            if cached_url:
                images_info.append({
                    "timestamp": f"{timestamp_base}_{timestamp_valid}",
                    "url": urljoin(f"{settings.BASE_URL}/", cached_url)
                })
                continue
            # Generate new image
            time_difference = pd.Timedelta(valid_datetime - base_datetime)
            data_geo = ds_geo.sel(time=base_datetime, method="nearest")
            data_geo = data_geo.sel(
                prediction_timedelta=time_difference,
                method="nearest"
            )
            if model_type == "cerrora":
                gt_data_geo = gt_ds_geo.sel(time=valid_datetime,method="nearest")

            if 'level' in data_geo.dims:
                data_geo = data_geo.sel(level=500) / 9.80665
                if model_type == "cerrora":
                    gt_data_geo = gt_data_geo.sel(pressure_level=500) / 9.80665
            if gt_data_loader is not None:
                visualizer.create_geo_plot(
                    gt_data_geo,
                    timestamp_base,
                    timestamp_valid,
                    reverse = False
                )
                #pass

            url = visualizer.create_geo_plot(
                data_geo,
                timestamp_base,
                timestamp_valid
            )
            if url:
                split_url = url.split("streaming")
                images_info.append({
                    "timestamp": f"{timestamp_base}_{timestamp_valid}",
                    "url": process_url(url, model_type)  # split_url[0]+"streaming/"+model_type+split_url[1]
                })
        return {"images": images_info}
    except Exception as e:
        logger.error(f"Error generating geo visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def fetch_sea_level_data(time_range: TimeRange,loaders: tuple):
    """Generate mean sea level pressure visualization for specified time range."""
    data_loader, visualizer, model_type = loaders
    gt_data_loader = None
    gt_ds_slp = None
    gt_data_slp = None
    try:
        # First check for existing images
        existing_images = get_existing_images(time_range, "sea_level", model_type)

        # Check if all images exist
        if len(existing_images) == len(time_range.validTime):
            logger.info("All sea level pressure images found in cache")
            return {"images": [
                {"timestamp": img["timestamp"],
                 "url": urljoin(f"{settings.BASE_URL}/", img["url"])}
                for img in existing_images
            ]}

        # If not all images exist, generate missing ones
        images_info = []
        base_datetime = pd.to_datetime(time_range.baseTime, unit='s')
        base_datetime = pd.Timestamp(base_datetime).to_datetime64()

        # Load data once for all images
        if model_type == 'graphcast':
            #ds_slp = data_loader.get_variable_data('mean_sea_level_pressure')
            ds_slp = data_loader.get_variable_data('msl')
        elif model_type == 'cerrora':

            ds_slp = data_loader.get_variable_data('msl')
            gt_data_loader = DataLoader(model_type="cerrora_gt")
            gt_ds_slp = gt_data_loader.get_variable_data("msl")
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        for valid_time in time_range.validTime:
            valid_datetime = pd.to_datetime(valid_time, unit='s')
            timestamp_base = int(pd.Timestamp(base_datetime).timestamp())
            timestamp_valid = int(valid_datetime.timestamp())

            # Check for cached image
            cached_url = get_cached_image_path(timestamp_base, timestamp_valid, "sea_level", model_type)
            if cached_url:
                images_info.append({
                    "timestamp": f"{timestamp_base}_{timestamp_valid}",
                    "url": urljoin(f"{settings.BASE_URL}/", cached_url)
                })
                continue
            if gt_data_loader is not None:
                gt_data_slp = gt_ds_slp.sel(time=valid_datetime,method="nearest")
                visualizer.create_sea_level_plot(gt_data_slp, timestamp_base, timestamp_valid,reverse=False)

            # Generate new image
            time_difference = pd.Timedelta(valid_datetime - base_datetime)
            data_slp = ds_slp.sel(time=base_datetime, method="nearest")
            data_slp = data_slp.sel(
                prediction_timedelta=time_difference,
                method="nearest"
            )

            url = visualizer.create_sea_level_plot(data_slp,timestamp_base,timestamp_valid)

            if url:
                images_info.append({
                    "timestamp": f"{timestamp_base}_{timestamp_valid}",
                    "url": process_url(url, model_type)  # url
                })

        return {"images": images_info}

    except Exception as e:
        logger.error(f"Error generating sea level pressure visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_country_code(country_name:str):
    response = requests.get(f"https://www.apicountries.com/name/{country_name}",timeout=10)
    return response.json()[0]["alpha2Code"]

def get_country_polygon_from_osm(country_name):
    country_code = get_country_code(country_name)
    query = f"""
    [out:json];
    relation["admin_level"="2"]["ISO3166-1"="{country_code}"];
    out geom;
    """
    r = requests.get("https://overpass-api.de/api/interpreter", params={"data": query})
    data = r.json()

    if not data["elements"]:
        return None

    # First match
    return data["elements"][0]["bounds"]
    
def get_city_coordinates(city_name):
    """
    Get coordinates for a European capital city from the JSON file.
    
    Args:
        city_name: Name of the city
        
    Returns:
        List [latitude, longitude] or None if city not found
    """
    json_file_path = os.path.join(os.path.dirname(__file__), "../../../european_capitals_coordinates.json")
    
    try:
        with open(json_file_path, 'r') as f:
            coordinates_data = json.load(f)
        
        return coordinates_data.get(city_name)
    except FileNotFoundError:
        logger.error(f"European capitals coordinates file not found at {json_file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {json_file_path}")
        return None

# def pred_data_sort_lat_long(data_source,start_lat=47.0,end_lat=55.0,start_lon=5.0, end_lon=15.0,start_date="2021-01-05",end_date="2021-01-05",usr_lat=0,usr_lon=0,temp_var='t2m',base_time=None): #2021-01-05T01:00:00
#     # Select data by base_time if provided, otherwise use date range
#     if base_time is not None:
#         base_time_dt = pd.Timestamp(base_time, unit='s')
#         dataset_by_tiime_range_specific_time_range = data_source.sel(time=base_time_dt, method='nearest')
#     else:
#         dataset_by_tiime_range_specific_time_range = data_source.sel(time=slice(start_date,end_date)) # this selects and returns a new dataset based on the filtered time range.
#     sorted_ds_by_longitude = dataset_by_tiime_range_specific_time_range.sortby('longitude')
#     dataset_by_time_latitude_longitude_sorted_ds_by_longitude = sorted_ds_by_longitude.sel(latitude=slice(end_lat, start_lat),longitude=slice(start_lon,end_lon ))
#     temp_data = dataset_by_time_latitude_longitude_sorted_ds_by_longitude[temp_var].sel(latitude=usr_lat,longitude=usr_lon,method='nearest')
#     df = temp_data.to_dataframe(name='temperature_2m').reset_index()
#     if len(df) > 0 and 'prediction_timedelta' in df.columns:
#         if hasattr(df['prediction_timedelta'].iloc[0], 'total_seconds'):
#             df['forecast_time'] = df['time'] + df['prediction_timedelta']
#         else:
#             df['forecast_time'] = df['time'] + pd.to_timedelta(df['prediction_timedelta'], unit='h')
#     else:
#         df['forecast_time'] = df['time']
#     
#     # Filter for specific forecast times: base_time + [6h, 12h, 18h, 24h, 30h]
#     if base_time is not None:
#         base_time_dt = pd.Timestamp(base_time, unit='s')
#         target_times = [base_time_dt + pd.Timedelta(hours=h) for h in [6, 12, 18, 24, 30]]
#         # Filter dataframe to only include rows where forecast_time matches target times
#         df['forecast_time_dt'] = pd.to_datetime(df['forecast_time'])
#         # Use nearest matching approach with tolerance
#         mask = df['forecast_time_dt'].apply(lambda x: any(abs((x - target).total_seconds()) < 3600 for target in target_times))
#         df = df[mask].copy()
#         df = df.drop(columns=['forecast_time_dt'])
#     
#     return df[['time','forecast_time','temperature_2m']]

def pred_data_sort_lat_long(data_source, xy, temp_var='t2m', base_time=None):
    """
    Get prediction data for specific xy indices.
    
    Args:
        data_source: xarray dataset with prediction data
        xy: tuple of (y, x) indices for the grid point
        temp_var: temperature variable name (default: 't2m')
        base_time: base time in seconds since epoch
        
    Returns:
        DataFrame with columns: time, forecast_time, temperature_2m
    """
    if base_time is not None:
        base_time_dt = pd.Timestamp(base_time, unit='s')
        target_times = [base_time_dt + pd.Timedelta(hours=h) for h in [6, 12, 18, 24, 30]]
        
        results = []
        for target_time in target_times:
            try:
                # Select base time (time when forecast was made)
                time_data = data_source.sel(time=base_time_dt, method='nearest')
                # Calculate prediction timedelta
                timedelta = (target_time - base_time_dt).total_seconds() / 3600  # hours
                timedelta_str = f"{int(timedelta)} hours"
                
                # Get temperature value at xy for this prediction timedelta
                temp_value = time_data.sel(prediction_timedelta=timedelta_str, method='nearest')[temp_var].values[::-1,:][xy]
                
                results.append({
                    'time': base_time_dt,
                    'forecast_time': target_time,
                    'temperature_2m': float(temp_value)
                })
            except (KeyError, ValueError, IndexError) as e:
                logger.warning(f"Could not get prediction for {target_time}: {e}")
                continue
        
        df = pd.DataFrame(results)
    else:
        # If no base_time provided, get all available data at xy
        temp_data = data_source[temp_var].isel(y=xy[0], x=xy[1])
        df = temp_data.to_dataframe(name='temperature_2m').reset_index()
        
        # Calculate forecast_time from prediction_timedelta
        if len(df) > 0 and 'prediction_timedelta' in df.columns:
            if hasattr(df['prediction_timedelta'].iloc[0], 'total_seconds'):
                df['forecast_time'] = df['time'] + df['prediction_timedelta']
            else:
                df['forecast_time'] = df['time'] + pd.to_timedelta(df['prediction_timedelta'], unit='h')
        else:
            df['forecast_time'] = df['time']
        
        df = df[['time', 'forecast_time', 'temperature_2m']]
    
    return df


# def gt_data_sort_lat_long(data_source,start_lat=47,end_lat=55,start_lon=5, end_lon=15,start_date="2021-01-05",end_date="2021-01-05",usr_lat=0,usr_lon=0,temp_var='t2m',base_time=None):
#     # Select data for specific times: base_time + [6h, 12h, 18h, 24h, 30h]
#     if base_time is not None:
#         base_time_dt = pd.Timestamp(base_time, unit='s')
#         # Calculate target times: base_time + [6h, 12h, 18h, 24h, 30h]
#         target_times = [base_time_dt + pd.Timedelta(hours=h) for h in [6, 12, 18, 24, 30]]
#         # Select each target time individually using nearest neighbor, then concatenate
#         # This ensures we get exactly 5 time points
#         time_slices = []
#         for target_time in target_times:
#             try:
#                 time_slice = data_source.sel(time=target_time, method='nearest')
#                 time_slices.append(time_slice)
#             except (KeyError, ValueError):
#                 # If exact time not found, skip (shouldn't happen with method='nearest')
#                 continue
#         if len(time_slices) == 0:
#             raise ValueError(f"No data found for target times around base_time {base_time_dt}")
#         # Concatenate along time dimension
#         dataset_by_tiime_range_specific_time_range = xr.concat(time_slices, dim='time')
#     else:
#         dataset_by_tiime_range_specific_time_range = data_source.sel(time=slice(start_date,end_date)) # this selects and returns a new dataset based on the filtered time range.
#     sorted_ds_by_longitude = dataset_by_tiime_range_specific_time_range.sortby ("x")
#     
#     # Filter by latitude and longitude coordinate values
#     # Find indices where latitude and longitude are within the specified bounds
#     lat_coords = sorted_ds_by_longitude.latitude
#     lon_coords = sorted_ds_by_longitude.longitude
#     
#     # Create masks for latitude and longitude bounds
#     lat_mask = (lat_coords >= start_lat) & (lat_coords <= end_lat)
#     lon_mask = (lon_coords >= start_lon) & (lon_coords <= end_lon)
#     combined_mask = lat_mask & lon_mask
#     
#     # Find the y and x indices that match the mask
#     # Compute the mask to get actual indices (works with dask arrays)
#     mask_computed = combined_mask.compute() if hasattr(combined_mask, 'compute') else combined_mask
#     
#     # Get indices where mask is True
#     # If latitude/longitude are 2D arrays indexed by (y, x)
#     if 'y' in mask_computed.dims and 'x' in mask_computed.dims:
#         # Find all (y, x) pairs where mask is True
#         y_idx, x_idx = np.where(mask_computed.values)
#         if len(y_idx) == 0:
#             raise ValueError(f"No data found in the specified bounds: lat=[{start_lat}, {end_lat}], lon=[{start_lon}, {end_lon}]")
#         
#         # Get unique indices to create a rectangular subset (more efficient than selecting individual pairs)
#         y_indices = np.unique(y_idx)
#         x_indices = np.unique(x_idx)
#         
#         # Select data using the indices
#         sorted_dataset = sorted_ds_by_longitude.isel(y=y_indices, x=x_indices)
#         
#         # Check if the filtered dataset is empty
#         if sorted_dataset.sizes.get('y', 0) == 0 or sorted_dataset.sizes.get('x', 0) == 0:
#             raise ValueError(f"No data found in the specified bounds: lat=[{start_lat}, {end_lat}], lon=[{start_lon}, {end_lon}]")
#         
#         # Now find the nearest point within this subset
#         # Apply mask to ensure we only consider points within bounds
#         abs_diff = abs(sorted_dataset.latitude - usr_lat) + abs(sorted_dataset.longitude - usr_lon)
#         # Mask out points that don't match the original bounds
#         mask_subset = combined_mask.isel(y=y_indices, x=x_indices)
#         abs_diff_masked = abs_diff.where(mask_subset, np.nan)
#         
#         # Check if abs_diff is empty before calling argmin
#         # Compute if it's a dask array, otherwise use directly
#         abs_diff_values = abs_diff_masked.compute().values if hasattr(abs_diff_masked, 'compute') else abs_diff_masked.values
#         if abs_diff_masked.size == 0 or np.all(np.isnan(abs_diff_values)):
#             raise ValueError(f"Empty coordinate difference array. Dataset shape: {sorted_dataset.sizes}")
#         
#         # Find the minimum using nanargmin to handle NaN values
#         min_idx = np.nanargmin(abs_diff_values)
#         iy, ix = np.unravel_index(min_idx, abs_diff_masked.shape)
#         
#     else:
#         # If coordinates are 1D, use a different approach
#         raise ValueError("Unexpected coordinate structure in ground truth dataset")
#     
#     temp_data = sorted_dataset[temp_var].isel(y=iy, x=ix)
#     df = temp_data.to_dataframe(name='temperature_2m').reset_index()
#     
#     # For GT data, time dimension directly represents valid times, so forecast_time = time
#     if 'prediction_timedelta' in df.columns:
#         if len(df) > 0 and hasattr(df['prediction_timedelta'].iloc[0], 'total_seconds'):
#             df['forecast_time'] = df['time'] + df['prediction_timedelta']
#         elif len(df) > 0:
#             df['forecast_time'] = df['time'] + pd.to_timedelta(df['prediction_timedelta'], unit='h')
#         else:
#             df['forecast_time'] = df['time']
#     else:
#         df['forecast_time'] = df['time']
#     
#     # Filter to ensure we only have the 5 target times (6h, 12h, 18h, 24h, 30h from base_time)
#     if base_time is not None:
#         base_time_dt = pd.Timestamp(base_time, unit='s')
#         target_times = [base_time_dt + pd.Timedelta(hours=h) for h in [6, 12, 18, 24, 30]]
#         # Filter to only include times that match our target times (within 1 hour tolerance)
#         df['time_dt'] = pd.to_datetime(df['time'])
#         mask = df['time_dt'].apply(lambda x: any(abs((x - target).total_seconds()) < 3600 for target in target_times))
#         df = df[mask].copy()
#         df = df.drop(columns=['time_dt'])
# 
#     return df[['time','forecast_time','temperature_2m']]

def gt_data_sort_lat_long(data_source, xy, temp_var='t2m', base_time=None):
    """
    Get ground truth data for specific xy indices.
    
    Args:
        data_source: xarray dataset with ground truth data
        xy: tuple of (y, x) indices for the grid point
        temp_var: temperature variable name (default: 't2m')
        base_time: base time in seconds since epoch
        
    Returns:
        DataFrame with columns: time, forecast_time, temperature_2m
    """
    if base_time is not None:
        base_time_dt = pd.Timestamp(base_time, unit='s')
        # Calculate target times: base_time + [6h, 12h, 18h, 24h, 30h]
        target_times = [base_time_dt + pd.Timedelta(hours=h) for h in [6, 12, 18, 24, 30]]
        
        results = []
        for target_time in target_times:
            try:
                # For ground truth, time represents the actual observation time
                time_data = data_source.sel(time=target_time, method='nearest')
                # Get temperature value at xy
                temp_value = time_data[temp_var].values[xy]
                
                results.append({
                    'time': target_time,
                    'forecast_time': target_time,
                    'temperature_2m': float(temp_value)
                })
            except (KeyError, ValueError, IndexError) as e:
                logger.warning(f"Could not get ground truth for {target_time}: {e}")
                continue
        
        df = pd.DataFrame(results)
    else:
        # If no base_time provided, get all available data at xy
        temp_data = data_source[temp_var].isel(y=xy[0], x=xy[1])
        df = temp_data.to_dataframe(name='temperature_2m').reset_index()
        
        # For GT data, time dimension directly represents valid times
        if 'prediction_timedelta' in df.columns:
            if len(df) > 0 and hasattr(df['prediction_timedelta'].iloc[0], 'total_seconds'):
                df['forecast_time'] = df['time'] + df['prediction_timedelta']
            elif len(df) > 0:
                df['forecast_time'] = df['time'] + pd.to_timedelta(df['prediction_timedelta'], unit='h')
            else:
                df['forecast_time'] = df['time']
        else:
            df['forecast_time'] = df['time']
        
        df = df[['time', 'forecast_time', 'temperature_2m']]
    
    return df

def temp_compare(graphcast_ds,pred_ds,gt_ds,country_name,base_time):
    # Get city coordinates from the JSON file
    res_metadata = get_city_coordinates(country_name)
    if res_metadata is None:
        raise ValueError(f"Could not retrieve coordinates for city: {country_name}")
    
    # Get exact coordinates from the city
    lat = res_metadata[0]
    lon = res_metadata[1]
    # Find xy indices from ground truth dataset
    xy = np.unravel_index((np.abs(gt_ds.longitude.values - lon) + np.abs(gt_ds.latitude.values - lat)).argmin(), gt_ds.longitude.values.shape)
    
    # Get data for all three models using the same xy indices
    ground_truth_res = gt_data_sort_lat_long(data_source=gt_ds, xy=xy, base_time=base_time)
    cerrora_res = pred_data_sort_lat_long(pred_ds, xy=xy, base_time=base_time)
    graphcast_res = pred_data_sort_lat_long(graphcast_ds, xy=xy, base_time=base_time)

    return (graphcast_res,cerrora_res,ground_truth_res)