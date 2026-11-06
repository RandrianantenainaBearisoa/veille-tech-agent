# import logging
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from lxml.etree import _Element

from src.logging.logging_config import logging
from src.utils.helpers import get_now_datetime

logger = logging.getLogger(__name__)


blacklist_words = [
    "promo",
    "promo code",
    "coupon",
    "discount",
    "sale",
    "off",
    "deals",
    "price drop",
    "shopping",
    "doorDash",
    "beginner's guide",
    "for beginners",
    "how to install",
    "how to use",
    "tutorial",
    "tuto",
    "step-by-step",
    "101",
]

whitelist_words = [
    "software",
    "software engineer",
    "software engineering",
    "ai",
    "artificial intelligence",
    "machine learning",
    "llm",
    "rag",
    "agent",
    "langchain",
    "langgraph",
    "hugging face",
    "pytorch",
    "scikit-learn",
    "vector",
    "database",
    "vector database",
    "pgvector",
    "embedding",
    "python",
    "fastapi",
    "pandas",
    "numpy",
    "php",
    "laravel",
    "vue",
    "vue.js",
    "typescript",
    "javascript",
    "api",
    "rest api",
    "docker",
    "kubernetes",
    "postgresql",
    "mysql",
    "sql",
    "git",
    "github",
    "gitlab",
    "ci/cd",
    "hypervisor",
    "container",
    "vulnerability",
    "patch",
    "rce",
    "exploit",
    "breach",
    "cve",
    "malware",
    "cybersecurity",
    "hacker",
    "security",
    "security flaw",
    "data center",
]

black_pattern = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in blacklist_words) + r")\b",
    re.IGNORECASE,
)
white_pattern = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in whitelist_words) + r")\b",
    re.IGNORECASE,
)


def filter_tech_item(item: _Element) -> bool:
    try:
        # item categories -> str
        categories = item.findall("category")
        categories = [cat.text for cat in categories if cat.text is not None]
        categories = ", ".join(categories)

        # item keywords -> str
        namespaces = {"media": "http://search.yahoo.com/mrss/"}
        keywords = item.find("media:keywords", namespaces)
        keywords = keywords.text if keywords is not None else ""

        # item title
        item_title = item.find("title")
        title = item_title.text if item_title is not None else ""

        text_to_check = f"{title}, {categories}, {keywords}"

        return bool(white_pattern.search(text_to_check)) and not bool(
            black_pattern.search(text_to_check)
        )
    except Exception:
        logger.exception("An error occured")
    return False


def get_feed_item_pub_date(feed: _Element) -> datetime | None:
    try:
        pub_date = feed.find("pubDate")
        if pub_date is not None:
            pub_date = parsedate_to_datetime(str(pub_date.text))
            return pub_date
    except Exception:
        logger.exception("An error occured")
    return None


def is_feed_date_valid(feed: _Element) -> bool:
    """
    Returns Bool : true (valid) if the date is today/yesterday , False (invalid) otherwise (above, below, or no date)
    """
    try:
        pub_date = get_feed_item_pub_date(feed)
        now_datetime = get_now_datetime()
        if pub_date is not None and now_datetime is not None:
            two_days_ago = now_datetime - timedelta(days=2)
            return pub_date.date() > two_days_ago.date()
    except Exception:
        logger.exception("An error occured")
    return False