from src.agent.content_creator_agent import content_creator_graph
from src.agent.state.actu_poster_state import ActuPosterState
from src.data.extract.extract_from_feeds import get_feeds, get_feeds_data
from src.utils.utils import generate_random_str

feeds_urls = get_feeds()
feeds_data = get_feeds_data(feeds_urls)

init_state: ActuPosterState = {
    "feed_items_base_list": feeds_data,
    "feed_items_relevant_indexes": [],
    "priority_list_validation": False,
    "item_priorization_retry": 0,
    "duplicate_check_retry": 0,
    "duplicate_check_validation": False,
    "feed_items_final_list": [],
    "contents_to_post": [],
    "post_store_validation": False,
}

content_creator_graph.invoke(
    init_state,
    config={"configurable": {"thread_id": f"content_create_{generate_random_str()}"}},
)
