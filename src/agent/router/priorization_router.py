from typing import Literal

from src.agent.state.actu_poster_state import ActuPosterState

MAX_PRIORIZATION_RETRY = 5


def route_after_priorization_process(
    state: ActuPosterState,
) -> Literal["item_priorization", "end_graph", "check_if_posted_before"]:
    if not state["priority_list_validation"]:
        if state["item_priorization_retry"] <= MAX_PRIORIZATION_RETRY:
            return "item_priorization"
        else:
            return "end_graph"
    return "check_if_posted_before"