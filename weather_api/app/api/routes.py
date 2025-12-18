from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import logging
import os
from urllib.parse import urljoin
from pydantic import BaseModel
from typing import TypedDict
from app.api.models import TimeRange
from app.core.Utility.Utilities import process_data, process_url, filter_images, fetch_valid_times, \
    fetch_temp_wind_data, fetch_geo_data, fetch_sea_level_data, temp_compare, get_country_polygon_from_osm
from app.core.d_loader import DataLoader
from app.core.Visualization.CerroraVisualizer import CerroraVisualizer
from app.core.Visualization.ExperimentalVisualizer import ExperimentalVisualizer
from app.core.Visualization.GraphCastVisualizer import GraphCastVisualizer
from app.core.Visualization.CerroraVisualizer_graphcast import CerroraVisualizer_graphcast
from app.config import settings
import time
import xarray as xr
import httpx
import pdb
# access to datasets - lazy loaded to avoid blocking startup
gt_path_ssd = settings.CERRORA_GT_ZARR_PATH
pred_path_ssd = settings.CERRORA_ZARR_PATH
graphcast_path_ssd = settings.GRAPHCAST_INTERPOLATED_ZARR_PATH

# Lazy-loaded datasets (only opened when first accessed)
_pred_ds = None
_actual_ds = None
_graphcast_ds = None
_aug = None
_uni_lon = None
_uni_lat = None

def get_pred_ds():
    """Lazy load prediction dataset."""
    global _pred_ds
    if _pred_ds is None:
        logger.info(f"Loading prediction dataset from {pred_path_ssd}")
        _pred_ds = xr.open_zarr(pred_path_ssd)
    return _pred_ds
def get_graphcast_ds():
    global _graphcast_ds
    if _graphcast_ds is None:
        logger.info(f"Loading prediction dataset from {graphcast_path_ssd}")
        _graphcast_ds = xr.open_zarr(graphcast_path_ssd)
    return _graphcast_ds

def get_actual_ds():
    """Lazy load ground truth dataset."""
    global _actual_ds
    if _actual_ds is None:
        logger.info(f"Loading ground truth dataset from {gt_path_ssd}")
        _actual_ds = xr.open_zarr(gt_path_ssd)
    return _actual_ds

def get_aug_dataset():
    """Lazy load augmentation dataset."""
    global _aug
    if _aug is None:
        logger.info(f"Loading augmentation dataset from {settings.CERRORA_EXAMPLE_ZARR_PATH}")
        _aug = xr.open_zarr(settings.CERRORA_EXAMPLE_ZARR_PATH)
    return _aug

def get_uni_lon():
    """Lazy load longitude values."""
    global _uni_lon
    if _uni_lon is None:
        aug = get_aug_dataset()
        _uni_lon = aug['longitude'].values
    return _uni_lon

def get_uni_lat():
    """Lazy load latitude values."""
    global _uni_lat
    if _uni_lat is None:
        aug = get_aug_dataset()
        _uni_lat = aug['latitude'].values
    return _uni_lat

separator = os.sep
logger = logging.getLogger("weather_api")

graphcast_loader = DataLoader(model_type="graphcast")
graphcast_interpolated_loader = DataLoader(model_type="graphcast")
cerrora_loader = DataLoader(model_type="cerrora")
experimental_loader = DataLoader(model_type="experimental")
cerrora_gt_loader = DataLoader(model_type="cerrora_gt")

graphcast_visualizer = GraphCastVisualizer()
# Visualizers will be initialized lazily when first needed
_graphcast_interpolated_visualizer = None
_cerrora_visualizer = None

def get_graphcast_interpolated_visualizer():
    """Lazy initialize graphcast interpolated visualizer."""
    global _graphcast_interpolated_visualizer
    if _graphcast_interpolated_visualizer is None:
        _graphcast_interpolated_visualizer = CerroraVisualizer_graphcast(get_uni_lon(), get_uni_lat())
    return _graphcast_interpolated_visualizer

def get_cerrora_visualizer():
    """Lazy initialize cerrora visualizer."""
    global _cerrora_visualizer
    if _cerrora_visualizer is None:
        _cerrora_visualizer = CerroraVisualizer(get_uni_lon(), get_uni_lat())
    return _cerrora_visualizer

experimental_visualizer = ExperimentalVisualizer()


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


class ModelManager:
    def __init__(self):
        self.models = ["graphcast", "cerrora", "experimental"]
        self.current_model = "cerrora"  # "graphcast"#

    ## the method below will have to be replaced/descard
    def get_current_loaders(self):
        if self.current_model == "graphcast":
            return graphcast_interpolated_loader, get_graphcast_interpolated_visualizer(), "graphcast"
        elif self.current_model == "cerrora":
            return cerrora_loader, get_cerrora_visualizer(), "cerrora"
        elif self.current_model == "experimental":
            return experimental_loader, experimental_visualizer, "experimental"
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid model type: {self.current_model}"
            )

    # This one will also go i nthe future.
    def switch_model(self, model_type: str):
        if model_type not in self.models:
            raise HTTPException(
                status_code=400, detail=f"Invalid model type: {model_type}"
            )
        self.current_model = model_type

        return self.get_current_loaders()


model_manager = ModelManager()

router = APIRouter()


@router.get("/temp_compare/{country}/{base_time}")
async def compare_temp(country: str, base_time:int):
    #pdb.set_trace()
    df_graphcast_res,df_pred_res,df_gt_res = temp_compare(graphcast_ds=get_graphcast_ds(),pred_ds=get_pred_ds(),gt_ds=get_actual_ds(),country_name=country,base_time=base_time)

    ground_truth_metrics:dict = df_gt_res[["forecast_time","temperature_2m"]].tail(6).reset_index(drop=True).to_dict();

    cerrora_metrics:dict = df_pred_res[["forecast_time","temperature_2m"]].sort_values("forecast_time").reset_index(drop=True).to_dict()
    graphcast_metrics:dict = df_graphcast_res[["forecast_time","temperature_2m"]].sort_values("forecast_time").reset_index(drop=True).to_dict()
    #print("ground_truth_metrics",ground_truth_metrics)
    #print("predicted_metrics",predicted_metrics)
    return  {"ground_truth": ground_truth_metrics,"cerrora":cerrora_metrics,"graphcast":graphcast_metrics}

@router.get("/get_cordinates/{country_name}")
async def get_cordinates(country_name: str):
    res_metadata = get_country_polygon_from_osm(country_name)
    return res_metadata


# Dependency to get current data loader and visualizer
async def get_current_loaders():
    data_loader, visualizer, model_type = (
        model_manager.get_current_loaders()
    )  # return graphcast_loader, graphcast_visualizer, "graphcast"
    return data_loader, visualizer, model_type


def get_current_loaders_v2(model_type: str) -> tuple[DataLoader, GraphCastVisualizer, str] | tuple[DataLoader, CerroraVisualizer, str] | tuple[DataLoader, ExperimentalVisualizer, str]:
    if model_type == "graphcast":
        return graphcast_interpolated_loader, get_graphcast_interpolated_visualizer(), "graphcast"
    elif model_type == "cerrora":
        return cerrora_loader, get_cerrora_visualizer(), "cerrora"
    elif model_type == "experimental":
        return experimental_loader, experimental_visualizer, "experimental"


# Ensure image output directory exists
os.makedirs(settings.IMAGE_OUTPUT_DIR, exist_ok=True)


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


class ModelTypeRequest(BaseModel):
    model_type: str


@router.post("/switch-model")
async def switch_model(request: ModelTypeRequest):
    """Switch the current model type."""
    try:
        model_manager.switch_model(request.model_type)
        return {
            "status": "success",
            "message": f"Switched to {request.model_type} model",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
    To let the client know the current model on browser refresh
"""


@router.get("/current-model")
def get_current_model():
    return model_manager.current_model;


@router.get("/data/{model_variable}/{base_time}")
async def get_image_data(model_variable: str, base_time: int):
    variable_name = model_variable  # I will later come back to this to remove the variable. Its currently redundant.
    if model_variable == "temp_wind":
        model_variable = variable_name = "tempWind"
    elif model_variable == "geo":
        model_variable = "geopotential"
    elif model_variable == "sea_level":
        model_variable = "seaLevelPressure"
    """Get the image data."""
    current_work_dir = os.getcwd()
    inference_dir_path_cerrora = (
            current_work_dir + separator + "streaming" + separator + "cerrora" + separator + model_variable + separator);
    inference_dir_path_graphcast = (
            current_work_dir + separator + "streaming" + separator + "graphcast" + separator + model_variable + separator);
    inference_directory_contents_cerrora = os.listdir(inference_dir_path_cerrora);
    inference_directory_contents_graphcast = os.listdir(inference_dir_path_graphcast);

    print(inference_directory_contents_cerrora)
    filtered_cerrora_content = filter_images(inference_directory_contents_cerrora, base_time);
    filtered_graphcast_content = filter_images(inference_directory_contents_graphcast, base_time);
    filtered_ground_truth_content = filter_images(inference_directory_contents_cerrora, base_time,
                                                  ground_truth_generate=True)
    print("#######################################")
    print(filtered_ground_truth_content)
    if len(filtered_cerrora_content) == 0:
        print(
            "No Cerrora⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️️️️⏱️️")
        filtered_cerrora_content = await get_images("cerrora",variable_name, str(base_time))
        inference_directory_contents_cerrora = os.listdir(inference_dir_path_cerrora);
        filtered_ground_truth_content = filter_images(inference_directory_contents_cerrora, base_time,
                                                      ground_truth_generate=True)
        print(filtered_cerrora_content)
    # WHAT IF THE GRAPHCAST_CONTENT IS EMPTY BUT THE CURRENT MODEL SELCTED IS CERRORA? NEEDS A RETHINK...
    if len(filtered_graphcast_content) == 0:
        filtered_graphcast_content = await get_images("graphcast",variable_name, str(base_time))
    smallest_image_size = min(len(filtered_ground_truth_content), len(filtered_cerrora_content),
                              len(filtered_graphcast_content));
    cerrora_image_list = filtered_cerrora_content[:smallest_image_size]
    graphcast_image_list = filtered_graphcast_content[:smallest_image_size]
    ground_truth_image_list = filtered_ground_truth_content[:smallest_image_size]

    return (cerrora_image_list, " :: ", graphcast_image_list, " :: ", ground_truth_image_list);


@router.get("/data/rand/init_random_image/{model_name}")
async def get_random_image(model_name: str):
    current_work_dir = os.getcwd()
    variable_list = ["seaLevelPressure","geopotential", "rain", "tempWind"]
    affected_variable = "";
    image_name = "";
    for curr_var in variable_list:
        inference_dir_path_cerrora = (
                current_work_dir + separator + "streaming" + separator + model_name + separator + curr_var + separator);
        inference_directory_contents_cerrora = os.listdir(inference_dir_path_cerrora);
        if len(inference_directory_contents_cerrora) > 0:
            affected_variable = curr_var
            image_name = inference_directory_contents_cerrora[0]
            break;
    return f"/{model_name}/{affected_variable}/{image_name}";


@router.post("/data/temp_wind/{model_type}")
async def get_temp_wind_data(time_range: TimeRange, model_type: str):
    loaders: tuple = get_current_loaders_v2(model_type)
    imgList = await fetch_temp_wind_data(time_range=time_range, loaders=loaders)
    return imgList;


###############################################################################################################
@router.post("/data/geo/{model_type}")
async def get_geo_data(
        time_range: TimeRange, model_type: str
):
    """Generate geopotential visualization for specified time range."""
    loaders: tuple = get_current_loaders_v2(model_type)
    imgList = await fetch_geo_data(time_range=time_range, loaders=loaders)
    return imgList


###############################################################################################################
"""
@router.post("/data/geo")
async def get_geo_data(
        time_range: TimeRange, loaders: tuple = Depends(get_current_loaders)
):
    ""Generate geopotential visualization for specified time range.""
    return process_data(
        time_range=time_range,
        loaders=loaders,
        plot_type="geo",
        descriptive_logger_info="All rain images found in cache",
        graph_cast_variable_type="geopotential", cerrora_variable_type="z",
        get_existing_images=get_existing_images, get_cached_image_path=get_cached_image_path)
"""


@router.post("/data/rain")
async def get_rain_data(
        time_range: TimeRange,
        loaders: tuple = Depends(get_current_loaders)
):
    """Generate precipitation visualization for specified time range."""
    data_loader, visualizer, model_type = loaders
    try:
        # First check for existing images
        existing_images = get_existing_images(time_range, "rain", model_type)
        # Check if all images exist
        if len(existing_images) == len(time_range.validTime):
            logger.info("All rain images found in cache")
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
            ds_rain = data_loader.get_variable_data('total_precipitation_6hr')
        elif model_type == 'cerrora':
            ds_rain = data_loader.get_variable_data('tp')
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        for valid_time in time_range.validTime:
            valid_datetime = pd.to_datetime(valid_time, unit='s')
            timestamp_base = int(pd.Timestamp(base_datetime).timestamp())
            timestamp_valid = int(valid_datetime.timestamp())

            # Check for cached image
            cached_url = get_cached_image_path(timestamp_base, timestamp_valid, "rain", model_type)
            if cached_url:
                images_info.append({
                    "timestamp": f"{timestamp_base}_{timestamp_valid}",
                    "url": urljoin(f"{settings.BASE_URL}/", cached_url)
                })
                continue

            # Generate new image
            time_difference = pd.Timedelta(valid_datetime - base_datetime)
            data_rain = ds_rain.sel(time=base_datetime, method="nearest")
            data_rain = data_rain.sel(
                prediction_timedelta=time_difference,
                method="nearest"
            )

            url = visualizer.create_rain_plot(
                data_rain,
                timestamp_base,
                timestamp_valid
            )

            if url:
                images_info.append({
                    "timestamp": f"{timestamp_base}_{timestamp_valid}",
                    "url": process_url(url, model_type)  # url
                })

        return {"images": images_info}

    except Exception as e:
        logger.error(f"Error generating precipitation visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


"""
@router.post("/data/rain")
async def get_rain_data(
        time_range: TimeRange, loaders: tuple = Depends(get_current_loaders)
):
    ""Generate precipitation visualization for specified time range.""
    return process_data(
        time_range=time_range,
        loaders=loaders,
        plot_type="rain",
        descriptive_logger_info="All rain images found in cache",
        graph_cast_variable_type="total_precipitation_6hr", cerrora_variable_type="tp",
        get_existing_images=get_existing_images, get_cached_image_path=get_cached_image_path)
"""


@router.post("/data/sea_level/{model_type}")
async def get_sea_level_data(time_range: TimeRange, model_type: str, ):
    loaders: tuple = get_current_loaders_v2(model_type)
    img_list = await fetch_sea_level_data(time_range=time_range, loaders=loaders)
    return img_list
"""
@router.post("/data/sea_level")
async def get_sea_level_data(
        time_range: TimeRange, loaders: tuple = Depends(get_current_loaders)
):
    ""Generate mean sea level pressure visualization for specified time range.""
    return process_data(
        time_range=time_range,
        loaders=loaders,
        plot_type="sea_level",
        descriptive_logger_info="Error generating sea level pressure visualization",
        graph_cast_variable_type="mean_sea_level_pressure", cerrora_variable_type="msl",
        get_existing_images=get_existing_images, get_cached_image_path=get_cached_image_path)

"""
@router.get("/base-times/{model_type}")
async def get_base_times(
        model_type: str,
        variableType: Optional[str] = Query(None, alias="variableType"),
        query_time: Optional[str] = Query(None, alias="queryTime"),
) -> List[dict]:
    """Get available base times for the specified variable type."""
    loaders: tuple = get_current_loaders_v2(model_type)
    data_loader, _, model_type = loaders

    try:
        if model_type == "graphcast":
            variable_map = variable_map_cerrora
        elif model_type == "cerrora":
            variable_map = variable_map_cerrora
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        #  "detail": "Error getting base times: 'geopotential'" # When variableType is provided
        #   "detail": "Error getting base times: 400: Invalid variable type" # when no variableTpye is provided
        variable = variable_map.get(variableType)
        # "2m_temperature"
        if variable is None:
            raise HTTPException(status_code=400, detail="Invalid variable type")

        if model_type == "cerrora":
            if query_time is not None:
                query_time = (slice(query_time, query_time))
            else:
                query_time = (slice(
                    # "2008-07-01T06:00:00.000000000", "2008-07-05T06:00:00.000000000"
                    # "2021-01-04T00:00:00.000000000","2021-01-12T00:00:00.000000000"
                    # "2020-01-04","2020-01-12"
                    "2022-05-05T00:00:00.000000000", "2022-05-12T00:00:00.000000000"
                ))

            # lead_time = [np.timedelta64(6, "h")]
            # freq = "6h"

            min_range, max_range, incrementor = (6, 31, 6)
            lead_time = [np.timedelta64(h, "h") for h in range(min_range, max_range, incrementor)]
            freq = "12h"
        else:
            query_time = (
                slice(query_time, query_time)
                if query_time is not None

                # else slice("2021-01-01", "2021-01-12")
                # else slice("2020-01-01", "2020-01-12")  # right before the line below...
                else slice("2022-05-05", "2022-05-12")
            )

            min_range, max_range, incrementor = (6, 31, 6)
            lead_time = [np.timedelta64(h, "h") for h in range(min_range, max_range, incrementor)]
            freq = "12h"
        ds = data_loader.get_zarr_subset(
            query_time, [variable], lead_time=lead_time, freq=freq
        )
        if ds is None:
            logger.error(
                f"No data found for variable {variable} at query time {query_time}"
            )
            return []
        if "time" not in ds:
            logger.error(f"No time dimension found in dataset for variable {variable}")
            return []
        times = ds["time"].values
        if len(times) == 0:
            logger.warning(f"No time values found for variable {variable}")
            return []
        return [
            {
                "label": pd.to_datetime(str(time)).strftime("%a %d %b %Y %H UTC"),
                "value": str(int(pd.to_datetime(str(time)).timestamp())),
            }
            for time in times
        ]
    except Exception as e:
        logger.error(
            f"Error getting base times: {e}", exc_info=True
        )  # Added exc_info for full traceback
        raise HTTPException(
            status_code=500, detail=f"Error getting base times: {str(e)}"
        )


@router.get("/valid-times/{model_type}")
async def get_valid_times(
        model_type:str,
        variableType: Optional[str] = Query(None, alias="variableType"),
        query_time: Optional[str] = Query(None, alias="queryTime"),
) -> List[List[dict]]:
    """Get available valid times for predictions."""
    loaders: tuple = get_current_loaders_v2(model_type)
    valid_times = await fetch_valid_times(variableType, query_time, loaders)
    return valid_times



'''
        plot_dir_map: VariableMap = {
            "temp_wind": "tempWind",
            "geo": "geopotential",
            "rain": "rain",
            "sea_level": "seaLevelPressure",
        }
'''


#@router.get("/fetch-images/{model_type}/{var_type}/{base_time}")
async def get_images(model_type: str, var_type: str, base_time: str):
    loaders: tuple = get_current_loaders_v2(model_type)
    res_valid_times = await fetch_valid_times(var_type, base_time, loaders)
    valid_times = [];
    image_list = [];
    img_list = None;
    for cur_time in res_valid_times[0]:
        valid_times.append(cur_time["value"])
    prep_req_body = {"baseTime": base_time, "validTime": valid_times}
    time_range = TimeRange(**prep_req_body)

    if var_type == "tempWind":
        img_list = await fetch_temp_wind_data(time_range=time_range, loaders=loaders)
    elif var_type == "sea_level":
        img_list = await fetch_sea_level_data(time_range=time_range, loaders=loaders)
    elif var_type == "geo":
        img_list = await fetch_geo_data(time_range=time_range, loaders=loaders)

    for img in img_list["images"]:
        image_list.append(img["url"].split("/")[-1])
    return image_list
