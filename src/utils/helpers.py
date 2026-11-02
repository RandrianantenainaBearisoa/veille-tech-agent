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
