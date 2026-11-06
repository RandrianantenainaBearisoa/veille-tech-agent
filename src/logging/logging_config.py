import logging

from src.utils.helpers import generate_random_str, get_now_datetime

now_datetime = get_now_datetime()

logging.basicConfig(
    filename=f"logs/app_{now_datetime.date() if now_datetime is not None else generate_random_str()}.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
