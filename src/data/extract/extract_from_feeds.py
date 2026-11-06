import logging
from datetime import datetime
from typing import TypedDict

import trafilatura
from lxml import etree
from lxml.etree import _Element

from src.data.extract.feed_filters import (
    filter_tech_item,
    get_feed_item_pub_date,
    is_feed_date_valid,
)
from src.utils.helpers import get_feed_topics

logger = logging.getLogger(__name__)


def get_feeds() -> list:
    # get feeds urls from the config file
    try:
        topics = get_feed_topics()
        feeds = []
        for topic in topics:
            topic_feeds = topic.get("feeds", [])
            feeds.extend(topic_feeds)
        return feeds
    except Exception:
        logger.exception("An error occured")
    return []


def fetch_from_url(url) -> str | None:
    try:
        if url:
            html_or_xml = trafilatura.fetch_url(url)
            return html_or_xml
    except Exception:
        logger.exception("An error occured")
    return None


def extract_from_html(html: str) -> str:
    try:
        text = trafilatura.extract(html) or ""
        return text
    except Exception:
        logger.exception("An error occured")
    return ""


def get_feed_items(xml: str) -> list[_Element]:
    try:
        root = etree.fromstring(
            xml.encode("utf-8"),
            parser=etree.XMLParser(encoding="utf-8"),
        )
        items = root.findall("channel/item")
        return items
    except Exception:
        logger.exception("An error occured")
    return []


class FeedItem(TypedDict):
    title: str
    pub_date: datetime
    description: str
    link: str


def get_feed_item_data(item: _Element) -> FeedItem | None:
    try:
        item_title = item.find("title")
        item_pub_date = get_feed_item_pub_date(item)
        item_description = item.find("description")
        item_link = item.find("link")
        if (
            item_title is not None
            and item_pub_date is not None
            and item_description is not None
            and item_link is not None
        ):
            return FeedItem(
                title=str(item_title.text),
                pub_date=item_pub_date,
                description=extract_from_html(f"<html>{item_description.text}</html>"),
                link=str(item_link.text),
            )
    except Exception:
        logger.exception("An error occured")

    return None


def get_feeds_data(feeds: list) -> list[FeedItem]:
    feed_items_list: list[FeedItem] = []
    try:
        for i, feed_url in enumerate(feeds):
            xml = fetch_from_url(feed_url)
            if xml is not None:
                items = get_feed_items(xml)
                for item in items:
                    date_is_valid = is_feed_date_valid(item)
                    if date_is_valid:
                        # check if the the item is related to tech
                        tech_valid = filter_tech_item(item)
                        item_data = get_feed_item_data(item)
                        if tech_valid and item_data is not None:
                            feed_items_list.append(item_data)
                    else:
                        break
        return feed_items_list
    except Exception:
        logger.exception("An error occured")
    return []
