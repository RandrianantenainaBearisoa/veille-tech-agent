from datetime import datetime
from typing import Any, TypedDict, cast
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from src.agent.node import item_filter as item_filter_module
from src.agent.node.item_filter import (
    CheckFormat,
    check_if_posted_before,
    get_last_publication,
    get_previous_post,
)
from src.database.models.table import Post, Publication


class MockActuPosterState(TypedDict):
    duplicate_check_retry: int
    feed_items_base_list: list[str]
    feed_items_relevant_indexes: list[int]


def test_check_if_posted_before_01(monkeypatch):
    state = MockActuPosterState(
        duplicate_check_retry=1,
        feed_items_base_list=["item_1", "item_2", "item_3"],
        feed_items_relevant_indexes=[1, 2],
    )

    def mock_get_previous_post(session):
        return []

    class MockModel:
        def invoke(self, input):
            return []

    monkeypatch.setattr(item_filter_module, "ActuPosterState", MockActuPosterState)
    monkeypatch.setattr(item_filter_module, "get_previous_post", mock_get_previous_post)
    monkeypatch.setattr(item_filter_module, "NEWS_CHECK", MockModel())

    result = cast(Any, check_if_posted_before)(state)
    expected_result = {
        "duplicate_check_retry": 2,
        "duplicate_check_validation": True,
        "feed_items_final_list": ["item_2", "item_3"],
    }

    assert result == expected_result


def test_check_if_posted_before_02(monkeypatch):
    state = MockActuPosterState(
        duplicate_check_retry=1,
        feed_items_base_list=["item_1", "item_2", "item_3"],
        feed_items_relevant_indexes=[1, 2],
    )

    def mock_get_previous_post(session):
        return ["prev_01", "item_2"]

    class MockModel:
        def invoke(self, input):
            return CheckFormat(check_list=[True, False])

    monkeypatch.setattr(item_filter_module, "ActuPosterState", MockActuPosterState)
    monkeypatch.setattr(item_filter_module, "get_previous_post", mock_get_previous_post)
    monkeypatch.setattr(item_filter_module, "NEWS_CHECK", MockModel())

    result = cast(Any, check_if_posted_before)(state)
    expected_result = {
        "duplicate_check_retry": 2,
        "duplicate_check_validation": True,
        "feed_items_final_list": ["item_3"],
    }

    assert result == expected_result


def test_check_if_posted_before_03(monkeypatch):
    state = MockActuPosterState(
        duplicate_check_retry=1,
        feed_items_base_list=["item_1", "item_2", "item_3"],
        feed_items_relevant_indexes=[1, 2],
    )

    def mock_get_previous_post():
        return ["prev_01", "item_2"]

    class MockModel:
        def invoke(self, input):
            return [True, False]  # not instance of CheckFormat

    monkeypatch.setattr(item_filter_module, "ActuPosterState", MockActuPosterState)
    monkeypatch.setattr(item_filter_module, "get_previous_post", mock_get_previous_post)
    monkeypatch.setattr(item_filter_module, "NEWS_CHECK", MockModel())

    result = cast(Any, check_if_posted_before)(state)
    expected_result = {
        "duplicate_check_retry": 2,
        "duplicate_check_validation": False,
    }

    assert result == expected_result


def test_check_if_posted_before_04(monkeypatch):
    state = MockActuPosterState(
        duplicate_check_retry=1,
        feed_items_base_list=["item_1", "item_2", "item_3"],
        feed_items_relevant_indexes=[1, 2],
    )

    def mock_get_previous_post():
        return ["prev_01", "item_2"]

    class MockModel:
        def invoke(self, input):
            return CheckFormat(
                check_list=[True]
            )  # len is != of len(feed_items_relevant_indexes)

    monkeypatch.setattr(item_filter_module, "ActuPosterState", MockActuPosterState)
    monkeypatch.setattr(item_filter_module, "get_previous_post", mock_get_previous_post)
    monkeypatch.setattr(item_filter_module, "NEWS_CHECK", MockModel())

    result = cast(Any, check_if_posted_before)(state)
    expected_result = {
        "duplicate_check_retry": 2,
        "duplicate_check_validation": False,
    }

    assert result == expected_result


def test_get_previous_post(monkeypatch):
    last_post_date = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))
    post = Post(
        title="Post title",
        source="this is a source",
        subtitle="Post subtitle",
        content="Post content",
        created_at=last_post_date,
        publication_id=1,
    )
    last_pub = Publication(
        id=404,
        accroche="Ceci est une accroche",
        status=True,
        posted_at=None,
        posts=[post],
    )

    def mock_get_last_publication(session):
        return last_pub

    monkeypatch.setattr(
        item_filter_module, "get_last_publication", mock_get_last_publication
    )

    result = cast(Any, get_previous_post)("session")

    assert result == [
        {
            "title": "Post title",
            "subtitle": "Post subtitle",
            "content": "Post content",
        }
    ]


def test_get_previous_post_returns_empty_list_when_no_posts(monkeypatch):
    last_pub = Publication(
        id=404,
        accroche="Ceci est une accroche",
        status=True,
        posted_at=None,
        posts=[],
    )

    def mock_get_last_publication(session):
        return last_pub

    monkeypatch.setattr(
        item_filter_module, "get_last_publication", mock_get_last_publication
    )

    result = cast(Any, get_previous_post)("session")

    assert result == []


def test_get_last_publication():
    last_pub = Publication(
        id=404,
        accroche="Ceci est une accroche",
        status=True,
        posted_at=None,
        posts=[],
    )

    session = MagicMock()
    session.exec.return_value.first.return_value = last_pub

    result = get_last_publication(session)

    assert result == last_pub


def test_get_last_publication_returns_none_when_no_prev_pub():
    session = MagicMock()
    session.exec.return_value.first.return_value = None

    result = get_last_publication(session)

    assert result is None
