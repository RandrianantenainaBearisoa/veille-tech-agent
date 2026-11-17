from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, ValidationError

from src.agent.state.actu_poster_state import ActuPosterState
from src.ai_model.used_llm import LLM
from src.logging.logging_config import logging

logger = logging.getLogger(__name__)

MIN_RELEVANT_NUMBER = 5
MAX_RELEVANT_NUMBER = 10

priorization_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                You are a Lead Software Engineer and a senior tech radar curator. Your objective is to analyze a list of tech news items, eliminate noise, and select the 5 to 10 most relevant topics with high "technical signal" for a publication targeted at developers and engineers.

                ### Selection Criteria (in order of priority):
                1. **Major Technical Impact:** Major new framework releases (FastAPI, Laravel, Vue), infrastructure tool updates (Docker, Postgres, Git), concrete AI/ML breakthroughs (open-weights models, RAG architectures, agents, LangChain/LangGraph).
                2. **Critical Security:** Major vulnerabilities (high CVSS score, RCE, Linux/RedHat kernel patches) or cloud security alerts.
                3. **Novelty / Exclusivity:** Announcements from major players that reshape the development ecosystem.
                4. your selection must be based on the title and the description of each new

                ### What Must Be Strictly Rejected:
                - Beginner tutorials ("how to install", "beginner's guide").
                - Marketing or commercial press releases without underlying code or technology.
                - General news or political stories without a direct link to software engineering.

                ### The inputs are in a list of dict (the title and a description of each new is given)

                ### Output format : list of index of the relevant items from the list
            """,
        ),
        ("human", "{tech_news}"),
    ]
)


class PriorizationFormat(BaseModel):
    index_list: list[int] = Field(
        description="List of the index of the 5 to 10 relevant tech news"
    )


priorization_model = LLM.with_structured_output(PriorizationFormat).with_retry(
    retry_if_exception_type=(ValidationError,),
    stop_after_attempt=3,
)

NEWS_EDITOR = priorization_prompt | priorization_model


def item_priorization(state: ActuPosterState) -> dict:
    # list of news
    tech_news = state["feed_items_base_list"]
    retry = state["item_priorization_retry"] + 1
    try:
        # invoke
        priorities_indexes = NEWS_EDITOR.invoke({"tech_news": tech_news})
        # result validation
        if isinstance(priorities_indexes, PriorizationFormat):
            is_relevant_list_valid = validate_relevant_list(
                priorities_indexes.index_list, len(tech_news)
            )
            if is_relevant_list_valid:
                return {
                    "feed_items_relevant_indexes": priorities_indexes.index_list,
                    "priority_list_validation": True,
                    "item_priorization_retry": retry,
                }
    except Exception:
        logger.exception("An error occured")
    # default return if error or invalidity
    return {
        "priority_list_validation": False,
        "item_priorization_retry": retry,
    }


def validate_priorities_indexes(
    index_list: list[int], len_of_tech_nws_list: int
) -> bool:
    try:
        indexes_validations = [index < len_of_tech_nws_list for index in index_list]
        return all(indexes_validations)
    except Exception:
        logger.exception("An error occured")
    return False


def validate_list_len(list_to_validate: list, min_len: int, max_len: int) -> bool:
    try:
        return min_len <= len(list_to_validate) <= max_len
    except Exception:
        logger.exception("An error occured")
    return False


def validate_relevant_list(relevant_index_list: list[int], tech_news_len: int) -> bool:
    list_len_validation = validate_list_len(
        relevant_index_list, MIN_RELEVANT_NUMBER, MAX_RELEVANT_NUMBER
    )
    indexes_validation = validate_priorities_indexes(relevant_index_list, tech_news_len)
    return list_len_validation and indexes_validation
