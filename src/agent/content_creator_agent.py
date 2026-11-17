from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from src.agent.node.content_synthetizer import content_synthetizer
from src.agent.node.item_filter import check_if_posted_before
from src.agent.node.item_prioritization import item_priorization
from src.agent.node.store_content import store_the_contents
from src.agent.router.filter_router import route_after_filter_process
from src.agent.router.priorization_router import route_after_priorization_process
from src.agent.state.actu_poster_state import ActuPosterState

constructeur = StateGraph(ActuPosterState)

constructeur.add_node("item_priorization", item_priorization)
constructeur.add_node("check_if_posted_before", check_if_posted_before)
constructeur.add_node("synthetize_content", content_synthetizer)
constructeur.add_node("end_graph", store_the_contents)

constructeur.add_edge(START, "item_priorization")
constructeur.add_conditional_edges(
    "item_priorization",
    route_after_priorization_process,
    ["item_priorization", "end_graph", "check_if_posted_before"],
)
constructeur.add_conditional_edges(
    "check_if_posted_before",
    route_after_filter_process,
    ["end_graph", "check_if_posted_before", "synthetize_content"],
)
constructeur.add_edge("synthetize_content", "end_graph")
constructeur.add_edge("end_graph", END)

content_creator_graph = constructeur.compile(checkpointer=InMemorySaver())
