from typing import Any, TypedDict, cast

from src.agent.router.filter_router import route_after_filter_process


class MockActuPosterState(TypedDict):
    duplicate_check_validation: bool
    duplicate_check_retry: int


def test_route_after_filter_process_01():
    state = MockActuPosterState(
        duplicate_check_validation=True, duplicate_check_retry=2
    )
    result = cast(Any, route_after_filter_process)(state)
    expected_result = "synthetize_content"

    assert result == expected_result


def test_route_after_filter_process_02():
    state = MockActuPosterState(
        duplicate_check_validation=False, duplicate_check_retry=4
    )
    result = cast(Any, route_after_filter_process)(state)
    expected_result = "end_graph"

    assert result == expected_result


def test_route_after_filter_process_03():
    state = MockActuPosterState(
        duplicate_check_validation=False, duplicate_check_retry=2
    )
    result = cast(Any, route_after_filter_process)(state)
    expected_result = "check_if_posted_before"

    assert result == expected_result
