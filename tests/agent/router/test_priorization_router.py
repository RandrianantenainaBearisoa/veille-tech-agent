from copy import deepcopy

from src.agent.router.priorization_router import route_after_priorization_process
from tests.agent.state.test_actu_poster_state import example_state


def test_route_after_priorization_process_01():
    state = deepcopy(example_state)
    state["priority_list_validation"] = False
    next_step = route_after_priorization_process(state)
    expected_step = "item_priorization"
    assert next_step == expected_step


def test_route_after_priorization_process_02():
    state = deepcopy(example_state)
    state["priority_list_validation"] = False
    state["item_priorization_retry"] = 6
    next_step = route_after_priorization_process(state)
    expected_step = "end_graph"
    assert next_step == expected_step


def test_route_after_priorization_process_03():
    state = deepcopy(example_state)
    state["priority_list_validation"] = True
    next_step = route_after_priorization_process(state)
    expected_step = "check_if_posted_before"
    assert next_step == expected_step
