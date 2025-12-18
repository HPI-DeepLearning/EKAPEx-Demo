from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os

class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "Weather Visualization API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # GCS Settings
    GCS_PROJECT: str = "anon"

    # Zarr paths for different models
    GRAPHCAST_ZARR_PATH: str = os.getenv(
        "GRAPHCAST_ZARR_PATH"
    )

    GRAPHCAST_INTERPOLATED_ZARR_PATH: str = os.getenv(
        "GRAPHCAST_INTERPOLATED_ZARR_PATH"
    )

    #/Volumes/Njies/WORK_BACKUP/recent_model_to_used/graphcast-prediction-2021_wb2_jan_2021.zarr


    CERRORA_EXAMPLE_ZARR_PATH: str = os.getenv(
        "CERRORA_EXAMPLE_ZARR_PATH"

    )
    CERRORA_GT_ZARR_PATH: str = os.getenv(
        "CERRORA_GT_ZARR_PATH"
    )
    CERRORA_ZARR_PATH: str = os.getenv(
        "CERRORA_ZARR_PATH"
    )

    EXPERIMENTAL_ZARR_PATH: str = os.getenv(
        "EXPERIMENTAL_ZARR_PATH"
    )

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8999
    RELOAD: bool = False


    CORS_ORIGINS: Union[List[str]] = os.getenv(
        "CORS_ORIGINS"
    )



    # Image Settings
    IMAGE_OUTPUT_DIR: str = "streaming"
    BASE_URL: str = os.getenv(
        "API_BASE_URL","http://127.0.0.1:8000/backend-fast-api/streaming",
    )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
