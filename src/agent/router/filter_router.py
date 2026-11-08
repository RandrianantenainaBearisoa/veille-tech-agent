from typing import Literal

from src.agent.state.actu_poster_state import ActuPosterState

MAX_FILTER_RETRY = 3


def route_after_priorization_process(
    state: ActuPosterState,
) -> Literal["end_graph", "check_if_posted_before"]:
    if (
        not state["duplicate_check_validation"]
        and state["duplicate_check_retry"] <= MAX_FILTER_RETRY
    ):
        return "check_if_posted_before"
    return "end_graph"
