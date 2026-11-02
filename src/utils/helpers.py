import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def read_yaml(filepath: Path) -> dict:
    """
    Read and return the content of an YAML File
    """
    try:
        with open(filepath, "r") as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        logger.exception("Error: The specified file does not exist.")
    except PermissionError:
        logger.exception("Error: Permission required to read this file.")
    except Exception:
        logger.exception("An error occured.")
    return {}
