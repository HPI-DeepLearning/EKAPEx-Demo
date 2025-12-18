import argparse
import uvicorn
from app.config import settings
import logging
from app.utils.logger import setup_logger
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Weather Visualization API Server")
    parser.add_argument(
        "--host", type=str, default=settings.HOST, help="Host to run the server on"
    )
    parser.add_argument(
        "--port", type=int, default=settings.PORT, help="Port to run the server on"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.RELOAD,
        help="Enable auto-reload",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )
    return parser.parse_args()


def setup_logging(log_level: str):
    """Configure logging."""
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def main():
    """Main entry point for the application."""
    args = parse_args()

    # Setup logger
    logger = setup_logger(args.log_level)
    logger.info(f"Starting server on {args.host}:{args.port}")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
