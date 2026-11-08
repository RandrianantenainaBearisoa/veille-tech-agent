from typing import Any, TypedDict, cast

from src.agent.node import item_filter as item_filter_module
from src.agent.node.item_filter import CheckFormat, check_if_posted_before


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

    def mock_get_previous_post():
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

    def mock_get_previous_post():
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
            return CheckFormat(check_list=[True]) # len is != of len(feed_items_relevant_indexes)

    monkeypatch.setattr(item_filter_module, "ActuPosterState", MockActuPosterState)
    monkeypatch.setattr(item_filter_module, "get_previous_post", mock_get_previous_post)
    monkeypatch.setattr(item_filter_module, "NEWS_CHECK", MockModel())

    result = cast(Any, check_if_posted_before)(state)
    expected_result = {
        "duplicate_check_retry": 2,
        "duplicate_check_validation": False,
    }

    assert result == expected_result
