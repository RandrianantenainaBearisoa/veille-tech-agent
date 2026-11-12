from sqlmodel import Session, select

from src.agent.state.actu_poster_state import ActuPosterState, ContentType
from src.database.database import get_session
from src.database.models.table import Category, Feed, Post, PostCategory
from src.logging.logging_config import logging

logger = logging.getLogger(__name__)


def get_feed_id(feed_url: str, session: Session) -> int | None:
    try:
        feed_select_statement = select(Feed).where(Feed.url == feed_url).limit(1)
        related_feed = session.exec(feed_select_statement).first()
        if related_feed is not None:
            return related_feed.id
    except Exception:
        logger.exception("An error occured")
    return None


def get_category_id(cat_code: str, session: Session) -> int | None:
    try:
        cat_select_statement = (
            select(Category).where(Category.code == cat_code).limit(1)
        )
        related_cat = session.exec(cat_select_statement).first()
        if related_cat is not None:
            return related_cat.id
    except Exception:
        logger.exception("An error occured")
    return None


def store_post_from_content(content: ContentType, session: Session) -> Post | None:
    try:
        with session.begin_nested():
            related_feed_id = get_feed_id(content["feed"], session)
            post = Post.model_validate(
                {
                    "title": content["title"],
                    "subtitle": content["subtitle"],
                    "icon_suggestions": content["icon_suggestions"],
                    "content": content["content"],
                    "feed_id": related_feed_id,
                }
            )
            session.add(post)
            session.flush()
        return post
    except Exception:
        logger.exception("An error occured")
    return None


def store_post_categories(
    post_id: int, categories: list[str], session: Session
) -> bool:
    try:
        with session.begin_nested():
            post_categories = []
            for cat_code in categories:
                cat_id = get_category_id(cat_code, session)
                if cat_id is not None:
                    post_categories.append(
                        PostCategory.model_validate(
                            {
                                "post_id": post_id,
                                "category_id": cat_id,
                            }
                        )
                    )
            session.add_all(post_categories)
            session.flush()
        return True
    except Exception:
        logger.exception("An error occured")
    return False


def content_to_post(content: ContentType, session: Session) -> bool:
    """
    Get a ContentType and return a Post class
    """
    try:
        post = store_post_from_content(content, session)
        if post is None:
            return False
        if post.id is not None:
            are_post_categories_stored = store_post_categories(
                post.id, content["categories"], session
            )
            return are_post_categories_stored
        else:
            return False
    except Exception:
        logger.exception("An error occured")
    return False


def store_the_contents(state: ActuPosterState) -> dict:
    try:
        store_validation: list[bool] = []
        with get_session() as session:
            for content in state["contents_to_post"]:
                is_post_stored = content_to_post(content, session)
                store_validation.append(is_post_stored)
            if any(store_validation):
                session.commit()
                return {"post_store_validation": True}
            else:
                return {"post_store_validation": False}
    except Exception:
        logger.exception("An error occured")
    return {"post_store_validation": False}
