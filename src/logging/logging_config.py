import logging

from src.utils.utils import generate_random_str, get_now_datetime

now_datetime = get_now_datetime()

file_handler_warnings = logging.FileHandler(
    f"logs/error/error_{now_datetime.date() if now_datetime is not None else generate_random_str()}.log",
    encoding="utf-8",
)
file_handler_warnings.setLevel(level=logging.WARNING)

file_handler_logs = logging.FileHandler(
    f"logs/debug/app_{now_datetime.date() if now_datetime is not None else generate_random_str()}.log",
    encoding="utf-8",
)


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[file_handler_logs, file_handler_warnings],
)
