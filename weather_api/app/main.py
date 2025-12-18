from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import asyncio



from app.config import settings
from app.api.routes import router as api_router
from app.utils.logger import setup_logger

logger = setup_logger()
logger = logging.getLogger("weather_api")


class ImageCacheMiddleware(BaseHTTPMiddleware):
    """Middleware to handle image caching and timeouts."""

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/backend-fast-api/streaming"):
            # Set longer timeout for image requests
            timeout = 30.0  # 30 seconds timeout
            start_time = time.time()

            while time.time() - start_time < timeout:
                response = await call_next(request)
                if response.status_code != 404:
                    # Add caching headers for images
                    response.headers["Cache-Control"] = (
                        "public, max-age=31536000"  # Cache for 1 year
                    )
                    response.headers["ETag"] = (
                        f"v1_{os.path.basename(request.url.path)}"
                    )
                    return response
                # Wait a bit before retrying
                await asyncio.sleep(0.5)

            # If timeout reached, return a proper error response
            return JSONResponse(
                status_code=504,
                content={"detail": "Image generation timed out. Please try again."},
            )

        return await call_next(request)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Weather Visualization API Service",
    )

    # Use CORS origins from settings
    origins = settings.CORS_ORIGINS


    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        #allow_origins=["*"],
        allow_origins=origins,
        #allow_credentials=True,
        allow_credentials=True,
        #allow_methods=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add image cache middleware
    app.add_middleware(ImageCacheMiddleware)

    # Add routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Ensure all image directories exist for each model type
    model_types = ["graphcast", "cerrora", "experimental"]
    plot_types = ["tempWind", "geopotential", "rain", "seaLevelPressure"]

    for model_type in model_types:
        for plot_type in plot_types:
            os.makedirs(os.path.join("streaming", model_type, plot_type), exist_ok=True)

    # Mount the static files directory with custom config
    app.mount(
        "/backend-fast-api/streaming",
        StaticFiles(
            directory="streaming",
            check_dir=True,
            html=False,
        ),
        name="streaming",
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        if exc.status_code == 404 and request.url.path.startswith(
            "/backend-fast-api/streaming"
        ):
            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Image not found or still generating. Please try again."
                },
            )
        return JSONResponse(
            status_code=exc.status_code, content={"detail": str(exc.detail)}
        )

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up the application...")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down the application...")

    return app


app = create_app()
