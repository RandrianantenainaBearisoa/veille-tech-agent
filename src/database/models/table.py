from datetime import datetime

from sqlalchemy import JSON
from sqlmodel import TIMESTAMP, Field, Relationship, SQLModel, text

from src.utils.utils import get_now_datetime


class TimeStampsBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=get_now_datetime)
    updated_at: datetime = Field(
        default_factory=get_now_datetime,
        sa_type=TIMESTAMP(timezone=True),
        nullable=False,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "server_onupdate": text("CURRENT_TIMESTAMP"),
        },
    )


class FeedBase(SQLModel):
    name: str = Field(max_length=100)
    url: str = Field(max_length=3000)


class Feed(FeedBase, TimeStampsBase, table=True):
    posts: list[Post] | None = Relationship(back_populates="feed")


class PostBase(SQLModel):
    title: str = Field(max_length=34)
    subtitle: str = Field(max_length=90)
    icon_suggestions: list[str] | None = Field(default=None, sa_type=JSON)
    content: str = Field(max_length=1000)
    source: str = Field(max_length=3000)


class PostPrompt(SQLModel):
    title: str = Field(max_length=34)
    subtitle: str = Field(max_length=90)
    content: str = Field(max_length=1000)


class PostCategory(TimeStampsBase, table=True):
    post_id: int | None = Field(default=None, foreign_key="post.id")
    category_id: int | None = Field(default=None, foreign_key="category.id")


class CategoryBase(SQLModel):
    code: str = Field(max_length=20)
    fr_label: str = Field(max_length=50)


class Category(CategoryBase, TimeStampsBase, table=True):
    posts: list[Post] | None = Relationship(
        back_populates="categories", link_model=PostCategory
    )


class Publication(TimeStampsBase, table=True):
    accroche: str = Field(max_length=100)
    status: bool | None = Field(
        default=None
    )  # None = pending | False = publication not posted / rejected | True = posted
    posted_at: datetime | None = Field(default=None)
    posts: list[Post] | None = Relationship(back_populates="publication")


class Post(PostBase, TimeStampsBase, table=True):
    feed_id: int | None = Field(default=None, foreign_key="feed.id")
    publication_id: int = Field(foreign_key="publication.id")
    feed: Feed = Relationship(back_populates="posts")
    categories: list[Category] | None = Relationship(
        back_populates="posts", link_model=PostCategory
    )
    publication: Publication | None = Relationship(back_populates="posts")
