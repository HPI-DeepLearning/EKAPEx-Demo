import logging
import logging.handlers
from datetime import datetime
from pathlib import Path


def setup_logger(log_level: str = "INFO"):
    """
    Setup application logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = log_dir / f'weather_api_{timestamp}.log'

    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configure file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)

    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    # Get root logger
    root_logger = logging.getLogger()

    # Remove existing handlers
    root_logger.handlers = []

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Set log level
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Create app logger
    logger = logging.getLogger('weather_api')
    logger.info(f'Logger initialized. Log file: {log_file}')

    return logger