from lxml import etree
from sqlmodel import Session, select

from src.data.extract.extract_from_feeds import (
    fetch_from_url,
    get_feeds,
)
from src.database.database import get_session
from src.database.models.table import Category, Feed
from src.logging.logging_config import logging
from src.utils.helpers import get_rss_categories

logger = logging.getLogger(__name__)


def get_stored_category_codes(session: Session) -> set[str]:
    try:
        statement = select(Category.code)
        result = session.exec(statement).all()
        return set(result)
    except Exception:
        logger.exception("An error occured")
    return set()


def ingest_rss_categories():
    try:
        with get_session() as session:
            stored_categories = get_stored_category_codes(session)
            categories = get_rss_categories()
            codes_sets = set(categories.keys())
            unstored_categories = codes_sets - stored_categories
            codes, fr_labels = list(categories.keys()), list(categories.values())
            categories_to_store = [
                Category.model_validate({"code": code, "fr_label": fr_label})
                for code, fr_label in zip(codes, fr_labels)
                if code in unstored_categories
            ]
            if len(categories_to_store) > 0:
                session.add_all(categories_to_store)
                session.commit()
    except Exception:
        logger.exception("An error occured")


def get_stored_feeds(session: Session) -> set[str]:
    try:
        statement = select(Feed.url)
        result = session.exec(statement).all()
        return set(result)
    except Exception:
        logger.exception("An error occured")
    return set()


def get_feed_title(xml: str) -> str:
    try:
        root = etree.fromstring(
            xml.encode("utf-8"),
            parser=etree.XMLParser(encoding="utf-8"),
        )
        title = root.find("channel/title")
        if title is None:
            title = root[0]
        return (str(title.text)).strip()[0:100] if title is not None else ""
    except Exception:
        logger.exception("An error occured")
    return "MISSING_TITLE"


def get_feed_data(feed_url: str, session: Session) -> dict | None:
    try:
        stored_feeds = get_stored_feeds(session)
        if feed_url in stored_feeds:
            return None
        xml = fetch_from_url(feed_url)
        title = "MISSING_TITLE"
        if xml is not None:
            title = get_feed_title(xml)
        return {"name": title, "url": feed_url}
    except Exception:
        logger.exception("An error occured")
    return None


def ingest_rss_feeds():
    try:
        with get_session() as session:
            feeds_list = get_feeds()
            feeds_to_store = []
            for feed in feeds_list:
                try:
                    feed_data = get_feed_data(feed, session)
                    if feed_data is not None:
                        feed_data = Feed.model_validate(feed_data)
                        feeds_to_store.append(feed_data)
                except Exception:
                    logger.exception(f"An error occured for the feed: {feed}")
            if len(feeds_to_store) > 0:
                session.add_all(feeds_to_store)
                session.commit()
    except Exception:
        logger.exception("An error occured")
