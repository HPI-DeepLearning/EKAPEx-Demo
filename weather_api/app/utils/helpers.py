import os
import glob
import logging
from typing import Optional

logger = logging.getLogger('weather_api')


def clear_image_folder(folder_path: str) -> None:
    """
    Clear all files in the specified folder.

    Args:
        folder_path: Path to the folder to clear
    """
    try:
        folder_path = os.path.join(os.path.dirname(__file__), '..', '..', folder_path)
        if not os.path.exists(folder_path):
            return

        files = glob.glob(os.path.join(folder_path, '*'))
        for file in files:
            try:
                os.remove(file)
            except Exception as e:
                logger.warning(f"Failed to delete {file}. Reason: {e}")
    except Exception as e:
        logger.error(f"Error clearing image folder {folder_path}: {e}")


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that the directory exists, create if it doesn't.

    Args:
        path: Directory path to check/create
    """
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        raise


def get_file_extension(filename: str) -> Optional[str]:
    """
    Get the file extension from a filename.

    Args:
        filename: Name of the file

    Returns:
        str: File extension without the dot, or None if no extension
    """
    try:
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else None
    except Exception:
        return None