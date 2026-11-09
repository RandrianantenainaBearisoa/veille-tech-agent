from src.agent.state.actu_poster_state import ActuPosterState, FeedItem
from src.utils.utils import get_now_datetime

now_datetime = get_now_datetime()

if now_datetime is not None:
    example_feed_items = FeedItem(
        title="",
        pub_date=now_datetime,
        description="",
        link="",
    )

example_state = ActuPosterState(
    feed_items_base_list=[],
    feed_items_relevant_indexes=[],
    priority_list_validation=False,
    item_priorization_retry=0,
    duplicate_check_validation=False,
    duplicate_check_retry=0,
    feed_items_final_list=[],
)
