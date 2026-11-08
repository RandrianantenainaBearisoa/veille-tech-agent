from typing import Literal

from src.agent.state.actu_poster_state import ActuPosterState

MAX_FILTER_RETRY = 3


def route_after_priorization_process(
    state: ActuPosterState,
) -> Literal["end_graph", "check_if_posted_before", "synthetize_content"]:
    if not state["duplicate_check_validation"]:
        if state["duplicate_check_retry"] <= MAX_FILTER_RETRY:
            return "check_if_posted_before"
        else:
            return "end_graph"
    return "synthetize_content"
