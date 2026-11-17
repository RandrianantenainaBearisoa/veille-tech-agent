from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, ValidationError
from sqlmodel import Session, select

from src.agent.state.actu_poster_state import ActuPosterState
from src.ai_model.used_llm import LLM
from src.database.database import get_session
from src.database.models.table import PostPrompt, Publication
from src.logging.logging_config import logging

logger = logging.getLogger(__name__)

check_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                You are an automated deduplication agent for a technical curation pipeline. Your task is to compare a list of current tech news against a history of previously published posts to prevent posting the same topic twice.

                ### Inputs you will receive:
                1. `previous_posts`: A list of news titles and summaries that have already been published (Could be an empty list), retrieved from the Database.
                2. `tech_news_to_check`: A list of newly fetched news items to evaluate.

                ### Instructions:
                - Compare each item in `tech_news_to_check` against the items in `previous_posts`.
                - Perform semantic deduplication: Identify items that cover the exact same core event, product release, vulnerability, or announcement, even if the title, source, or phrasing is different.
                - Exclude any item from `tech_news_to_check` that matches or overlaps significantly with anything in `previous_posts`.

                ### Output Format:
                Return ONLY a valid list of booleans (e.g., [true, false, false, true]). 
                - The array length MUST exactly match the number of items in `tech_news_to_check`.
                - Each boolean corresponds positionally to the item at the exact same index in `tech_news_to_check`:
                - `true` if the item has already been posted (duplicate).
                - `false` if it is new and has never been posted before.
                - Do NOT include any markdown formatting (like ```json), explanations, or text outside of the bool list.
            """,
        ),
        ("human", "{previous_post}"),
        ("human", "{tech_news_to_check}"),
    ]
)


class CheckFormat(BaseModel):
    check_list: list[bool] = Field(
        description="List of bool for each news to check: True (has been published before) , False (Can be posted today)"
    )


check_model = LLM.with_structured_output(CheckFormat).with_retry(
    retry_if_exception_type=(ValidationError,),
    stop_after_attempt=3,
)

NEWS_CHECK = check_prompt | check_model


def check_if_posted_before(state: ActuPosterState) -> dict:
    retry = state["duplicate_check_retry"] + 1
    try:
        tech_news_to_check = [
            state["feed_items_base_list"][i]
            for i in state["feed_items_relevant_indexes"]
        ]
        with get_session() as session:
            previous_post = get_previous_post(session)
        if len(previous_post) > 0:
            checking_result = NEWS_CHECK.invoke(
                {
                    "previous_post": previous_post,
                    "tech_news_to_check": tech_news_to_check,
                }
            )
            if isinstance(checking_result, CheckFormat) and (
                len(tech_news_to_check) == len(checking_result.check_list)
            ):
                filtered_indexes = [
                    index
                    for i, index in enumerate(state["feed_items_relevant_indexes"])
                    if not checking_result.check_list[i]
                ]
                feed_items_final_list = [
                    state["feed_items_base_list"][i] for i in filtered_indexes
                ]
                return {
                    "duplicate_check_retry": retry,
                    "duplicate_check_validation": True,
                    "feed_items_final_list": feed_items_final_list,
                }
        else:
            return {
                "duplicate_check_retry": retry,
                "duplicate_check_validation": True,
                "feed_items_final_list": tech_news_to_check,
            }
    except Exception:
        logger.exception("An error occured")
    return {"duplicate_check_retry": retry, "duplicate_check_validation": False}


def get_previous_post(session: Session) -> list[dict]:
    try:
        last_publication = get_last_publication(session)
        if last_publication is not None:
            previous_posts = (
                last_publication.posts if last_publication.posts is not None else []
            )
            previous_posts = [
                PostPrompt.model_validate(previous).model_dump()
                for previous in previous_posts
            ]
            return previous_posts
    except Exception:
        logger.exception("An error occured")
    return []


def get_last_publication(session: Session) -> Publication | None:
    try:
        statement = select(Publication).order_by(Publication.created_at.desc()).limit(1)
        last_publication = session.exec(statement).first()
        if isinstance(last_publication, Publication):
            return last_publication
    except Exception:
        logger.exception("An error occured")
    return None
