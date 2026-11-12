from typing import TypedDict

from src.data.extract.extract_from_feeds import FeedItem


class ContentType(TypedDict):
    title: str
    subtitle: str
    icon_suggestions: list[str]
    content: str
    categories: list[str]
    feed: str


class ActuPosterState(TypedDict):
    feed_items_base_list: list[
        FeedItem
    ]  # the list of items extracted from extract_from_feeds.py

    feed_items_relevant_indexes: list[
        int
    ]  # the indexes of the 10 relevant items candidates to post: 10 mosts relevants feeds items to post
    priority_list_validation: bool  # true if the lis
    item_priorization_retry: (
        int  # init to 0 : increment +1 in each item_priorization passage
    )

    duplicate_check_retry: int
    duplicate_check_validation: bool
    feed_items_final_list: list[FeedItem]  # the 5 items to post

    contents_to_post: list[ContentType]
    post_store_validation: bool
