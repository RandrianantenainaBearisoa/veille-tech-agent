from copy import deepcopy

from src.agent.node import item_prioritization as item_prioritization_module
from src.agent.node.item_prioritization import (
    PriorizationFormat,
    item_priorization,
    validate_list_len,
    validate_priorities_indexes,
)
from tests.agent.state.test_actu_poster_state import example_state


def test_validate_priorities_indexes():
    test_set = [0, 1, 5, 6, 8, 4, 5, 6, 8, 4, 5]
    len_1, len_2, len_3 = 7, 8, 9

    result_1 = validate_priorities_indexes(test_set, len_1)
    result_2 = validate_priorities_indexes(test_set, len_2)
    result_3 = validate_priorities_indexes(test_set, len_3)

    assert not result_1 and not result_2 and result_3


def test_validate_list_len():
    test_set_1 = [0, 1, 5, 6]
    test_set_2 = [0, 1, 5, 6, 8, 4, 5]
    test_set_3 = [0, 1, 5, 6, 8, 4, 5, 6, 8, 4, 5]
    result_1 = validate_list_len(test_set_1, 5, 10)
    result_2 = validate_list_len(test_set_2, 5, 10)
    result_3 = validate_list_len(test_set_3, 5, 10)

    assert not result_1 and result_2 and not result_3


def test_item_priorization_01(monkeypatch):
    state = deepcopy(example_state)

    class MockNewsEditor:
        def invoke(self, input):
            return 0

    monkeypatch.setattr(item_prioritization_module, "NEWS_EDITOR", MockNewsEditor())

    result = item_priorization(state)
    expected_result = {
        "priority_list_validation": False,
        "item_priorization_retry": 1,
    }
    assert result == expected_result


def test_item_priorization_02(monkeypatch):
    state = deepcopy(example_state)
    state["item_priorization_retry"] = 3

    class MockNewsEditor:
        def invoke(self, input):
            return PriorizationFormat(index_list=[0, 1, 5, 6, 8, 4, 5])

    def mock_validate_relevant_list(
        relevant_index_list: list[int], tech_news_len: int
    ) -> bool:
        return False

    monkeypatch.setattr(item_prioritization_module, "NEWS_EDITOR", MockNewsEditor())
    monkeypatch.setattr(
        item_prioritization_module,
        "validate_relevant_list",
        mock_validate_relevant_list,
    )

    result = item_priorization(state)
    expected_result = {
        "priority_list_validation": False,
        "item_priorization_retry": 4,
    }
    assert result == expected_result


def test_item_priorization_03(monkeypatch):
    state = deepcopy(example_state)
    state["item_priorization_retry"] = 3

    class MockNewsEditor:
        def invoke(self, input):
            return PriorizationFormat(index_list=[0, 1, 5, 6, 8, 4, 5])

    def mock_validate_relevant_list(
        relevant_index_list: list[int], tech_news_len: int
    ) -> bool:
        return True

    monkeypatch.setattr(item_prioritization_module, "NEWS_EDITOR", MockNewsEditor())
    monkeypatch.setattr(
        item_prioritization_module,
        "validate_relevant_list",
        mock_validate_relevant_list,
    )

    result = item_priorization(state)
    expected_result = {
        "feed_items_relevant_indexes": [0, 1, 5, 6, 8, 4, 5],
        "priority_list_validation": True,
        "item_priorization_retry": 4,
    }
    assert result == expected_result
