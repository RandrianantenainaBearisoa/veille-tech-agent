# import logging
import random
import string
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from src.logging.logging_config import logging

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


def get_feed_topics() -> list[dict]:
    config_file = "config/sources_config.yaml"
    yaml_data = read_yaml(Path(config_file))
    try:
        return yaml_data["rss_list"]
    except KeyError:
        logger.exception("Error: the key used is not valid")
    except Exception:
        logger.exception("An error occured.")
    return []


def get_now_datetime() -> datetime | None:
    try:
        local_tz = ZoneInfo("localtime")
        return datetime.now(local_tz)
    except Exception:
        logger.exception("An error occured.")


def generate_random_str(length: int = 12) -> str:
    try:
        alphabet = string.ascii_letters + string.digits
        random_string = "".join(random.choices(alphabet, k=length))
        return random_string
    except Exception:
        logger.exception("An error occured.")
    return ""
