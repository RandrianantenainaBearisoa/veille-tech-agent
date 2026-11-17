import random
import string
from datetime import datetime
from zoneinfo import ZoneInfo


def get_now_datetime() -> datetime | None:
    local_tz = ZoneInfo("localtime")
    return datetime.now(local_tz)


def generate_random_str(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    random_string = "".join(random.choices(alphabet, k=length))
    return random_string
