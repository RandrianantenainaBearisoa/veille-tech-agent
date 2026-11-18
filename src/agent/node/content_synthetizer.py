from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, ValidationError

from src.agent.state.actu_poster_state import ActuPosterState, ContentType
from src.ai_model.used_llm import LLM
from src.data.extract.extract_from_feeds import (
    FeedItem,
    extract_from_html,
    fetch_from_url,
)
from src.logging.logging_config import logging
from src.utils.helpers import get_rss_categories, lang_validator

logger = logging.getLogger(__name__)

synth_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an expert technical curator and content writer. Your task is to analyze a given tech news item (title, description, and scraped web content) and generate a structured summary tailored for software engineers and developers in French.
            ### Inputs you will receive:
            - Title (raw title)
            - Description (raw description)
            - Scraped Content (the main content, from web scrapping)
            - Available Categories

            ### Instructions & Strict Constraints:
            1. **title**: A catchy, high-impact title in French. STRICTLY maximum 34 characters (spaces included).
            2. **subtitle**: A descriptive subtitle sentence in French. STRICTLY maximum 90 characters (spaces included).
            3. **icon_suggestions**: A list of 3-5 precise technical keywords (in English) to search for a matching SVG icon (e.g., "server", "shield", "database", "git", "python", "gemini", "gpt", "claude", "cloud computing", etc...).
            4. **content**: A technical summary of the situation in French (the situation or event or news, the changes, and the core engineering value). Length MUST be strictly between 500 and 1000 characters (inclusive).
            5. **categories**: Choose 1 to 3 categories from the "Available Categories" list provided in the input.

            ### Important : your main role is synthesis, and content creation so don't add your point of view anywhere.
            """,
        ),
        (
            "human",
            """
           These are the inputs:
            - Title: {raw_title}
            - Description: {raw_description}
            - Scraped Content: {raw_content}
            - Available Categories: {available_categories}
        """,
        ),
    ]
)


CONTENT_CATEGORIES = get_rss_categories()
CATEGORIES_KEYS = list(CONTENT_CATEGORIES.keys())


class ContentFormat(BaseModel):
    title: str = Field(description="title of the Content", max_length=34)
    subtitle: str = Field(description="Subtitle of the content", max_length=90)
    icon_suggestions: list[str] = Field(
        description="list of icons for Decoration", min_length=3, max_length=5
    )
    content: str = Field(
        description="the Main text content", min_length=500, max_length=1000
    )
    categories: list[str] = Field(
        description="List of related categories", max_length=3
    )


synth_model = LLM.with_structured_output(ContentFormat).with_retry(
    retry_if_exception_type=(ValidationError,),
    stop_after_attempt=3,
)

CONTENT_MAKER = synth_prompt | synth_model


def content_synthetizer(state: ActuPosterState) -> dict:
    try:
        items_to_post = state["feed_items_final_list"]
        contents_to_post: list[ContentType] = []
        for item in items_to_post:
            content = create_content(item)
            if content is not None:
                contents_to_post.append(content)
        return {"contents_to_post": contents_to_post}
    except Exception:
        logger.exception("An error occured")
    return {}


def web_scrapping(url: str) -> str:
    try:
        html = fetch_from_url(url)
        if html is not None:
            content = extract_from_html(html)
            return content
    except Exception:
        logger.exception("An error occured")
    return ""


def validate_content(content: ContentFormat) -> bool:
    try:
        content_to_validate = f"{content.title}. {content.subtitle}. {content.content}"
        are_categories_valid = set(content.categories).issubset(set(CATEGORIES_KEYS))
        # validate languages
        is_lang_valid = lang_validator(content_to_validate, "fr")
        return are_categories_valid and is_lang_valid
    except Exception:
        logger.exception("An error occured")
    return False


def try_create_content(
    raw_title: str, raw_description: str, raw_content: str, feed: str, source: str
) -> ContentType | None:
    try:
        # invoke model
        content = CONTENT_MAKER.invoke(
            {
                "raw_title": raw_title,
                "raw_description": raw_description,
                "raw_content": raw_content,
                "available_categories": CATEGORIES_KEYS,
            }
        )
        # validate content
        if isinstance(content, ContentFormat):
            is_content_valid = validate_content(content)
            if is_content_valid:
                content_to_post = ContentType(
                    title=content.title,
                    subtitle=content.subtitle,
                    icon_suggestions=content.icon_suggestions,
                    content=content.content,
                    categories=content.categories,
                    feed=feed,
                    source=source,
                )
                return content_to_post
    except Exception:
        logger.exception("An error occured")
    return None


def create_content(item: FeedItem) -> ContentType | None:
    try:
        # Get and make input
        raw_title = item["title"]
        raw_description = item["description"]
        raw_content = web_scrapping(item["link"])
        content_to_post: ContentType | None = None
        content_to_post = try_create_content(
            raw_title, raw_description, raw_content, item["feed"], item["link"]
        )
        return content_to_post
    except Exception:
        print(item["feed"])
        logger.exception("An error occured")
    return None
