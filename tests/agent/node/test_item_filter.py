from datetime import datetime
from typing import Any, TypedDict, cast
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from src.agent.node import item_filter as item_filter_module
from src.agent.node.item_filter import (
    CheckFormat,
    check_if_posted_before,
    get_last_post_date,
    get_previous_post,
)
from src.database.models.table import Post


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

    def mock_get_last_post_date(session):
        return last_post_date

    monkeypatch.setattr(
        item_filter_module, "get_last_post_date", mock_get_last_post_date
    )

    post = Post(
        title="Post title",
        source="this is a source",
        subtitle="Post subtitle",
        content="Post content",
        created_at=last_post_date,
    )
    session = MagicMock()
    session.exec.return_value.all.return_value = [post]

    result = get_previous_post(session)

    assert result == [
        {
            "title": "Post title",
            "subtitle": "Post subtitle",
            "content": "Post content",
        }
    ]


def test_get_previous_post_returns_empty_list_when_no_posts(monkeypatch):
    monkeypatch.setattr(item_filter_module, "get_last_post_date", lambda session: None)
    session = MagicMock()
    session.exec.return_value.all.return_value = []

    assert get_previous_post(session) == []


def test_get_last_post_date():
    expected_date = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))
    post = Post(
        title="Post title",
        source="this is a source",
        subtitle="Post subtitle",
        content="Post content",
        created_at=expected_date,
    )
    session = MagicMock()
    session.exec.return_value.first.return_value = post

    assert get_last_post_date(session) == expected_date
    statement = session.exec.call_args.args[0]
    assert "ORDER BY post.created_at DESC" in str(statement)
    assert "LIMIT" in str(statement)


def test_get_last_post_date_returns_none_when_no_posts():
    session = MagicMock()
    session.exec.return_value.first.return_value = None

    assert get_last_post_date(session) is None
