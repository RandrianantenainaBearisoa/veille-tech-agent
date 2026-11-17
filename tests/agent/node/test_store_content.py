from contextlib import contextmanager
from datetime import datetime
from typing import Any, cast
from zoneinfo import ZoneInfo

from src.agent.node import store_content as store_content_module
from src.agent.node.store_content import (
    content_to_post,
    get_feed_id,
    store_post_categories,
    store_post_from_content,
    store_publication,
    store_the_contents,
)
from src.database.models.table import Feed, Post, PostCategory, Publication


def test_get_feed_id(monkeypatch):
    class MockSessionResult:
        def first(self):
            return Feed.model_validate(
                {"id": 55, "name": "Feed_name", "url": "https://my-feed.com"}
            )

    class MockSession:
        def exec(self, statement):
            return MockSessionResult()

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    session = MockSession()
    expected_result = 55
    result = cast(Any, get_feed_id)("https://my-feed.com", session)

    assert expected_result == result


def test_get_feed_id_none(monkeypatch):
    class MockSessionResult:
        def first(self):
            return None

    class MockSession:
        def exec(self, statement):
            return MockSessionResult()

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    session = MockSession()
    expected_result = None
    result = cast(Any, get_feed_id)("https://my-feed.com", session)

    assert expected_result == result


def test_get_feed_id_fail(monkeypatch):
    class MockSessionResult:
        def first(self):
            print(0 / 0)

    class MockSession:
        def exec(self, statement):
            return MockSessionResult()

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    session = MockSession()
    expected_result = None
    result = cast(Any, get_feed_id)("https://my-feed.com", session)

    assert expected_result == result


def test_store_post_from_content(monkeypatch):
    datetime_exp = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))

    class MockSession:
        def __init__(self) -> None:
            self.actions = []
            self.post = None

        @contextmanager
        def begin_nested(self):
            yield "session"

        def add(self, instance: Post):
            self.post = instance

        def flush(self):
            if self.post is not None:
                self.post.id = 106
                self.post.created_at = datetime_exp
                self.post.updated_at = datetime_exp

    def mock_get_feed_id(feed_url, session):
        return 101

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    monkeypatch.setattr(store_content_module, "get_feed_id", mock_get_feed_id)
    content_type = {
        "title": "title",
        "subtitle": "subtitle",
        "icon_suggestions": ["sug_01", "sug_02", "sug_03"],
        "content": "content",
        "categories": ["cat_01", "cat_02", "cat_03"],
        "source": "actu-source.com",
        "feed": "feed.com",
    }
    result = cast(Any, store_post_from_content)(content_type, 404, MockSession())
    expected_result = Post.model_validate(
        {
            "id": 106,
            "created_at": datetime_exp,
            "updated_at": datetime_exp,
            "title": "title",
            "subtitle": "subtitle",
            "icon_suggestions": ["sug_01", "sug_02", "sug_03"],
            "content": "content",
            "source": "actu-source.com",
            "publication_id": 404,
            "feed_id": 101,
        }
    )

    assert result == expected_result


def test_store_post_from_content_fail(monkeypatch):
    datetime_exp = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))

    class MockSession:
        def __init__(self) -> None:
            self.actions = []
            self.post = None

        @contextmanager
        def begin_nested(self):
            yield "session"

        def add(self, instance: Post):
            self.post = instance

        def flush(self):
            if self.post is not None:
                self.post.id = 106
                self.post.created_at = datetime_exp
                self.post.updated_at = datetime_exp

    def mock_get_feed_id(feed_url, session):
        print(0 / 0)
        return 101

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    monkeypatch.setattr(store_content_module, "get_feed_id", mock_get_feed_id)
    content_type = {
        "title": "title",
        "subtitle": "subtitle",
        "icon_suggestions": ["sug_01", "sug_02", "sug_03"],
        "content": "content",
        "categories": ["cat_01", "cat_02", "cat_03"],
        "feed": "feed.com",
    }
    result = cast(Any, store_post_from_content)(content_type, 404, MockSession())
    assert result is None


def test_store_post_categories(monkeypatch):
    datetime_exp = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))

    class MockSession:
        def __init__(self) -> None:
            self.actions = []
            self.categories = []

        @contextmanager
        def begin_nested(self):
            yield "session"

        def add_all(self, instances: list[PostCategory]):
            self.categories = instances

        def flush(self):
            for i in range(len(self.categories)):
                self.categories[i].id = 5
                self.categories[i].created_at = datetime_exp
                self.categories[i].updated_at = datetime_exp

    def mock_get_category_id(cat_code, session):
        if cat_code == "Toto":
            return 101
        if cat_code == "tata":
            return 103
        if cat_code == "Cat_01":
            return 105

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    monkeypatch.setattr(store_content_module, "get_category_id", mock_get_category_id)

    categories = ["Toto", "tata", "Cat_01"]
    session = MockSession()
    result = cast(Any, store_post_categories)(108, categories, session)
    expected_result = True
    expected_row = [
        PostCategory.model_validate(
            {
                "post_id": 108,
                "category_id": 101,
                "id": 5,
                "created_at": datetime_exp,
                "updated_at": datetime_exp,
            }
        ),
        PostCategory.model_validate(
            {
                "post_id": 108,
                "category_id": 103,
                "id": 5,
                "created_at": datetime_exp,
                "updated_at": datetime_exp,
            }
        ),
        PostCategory.model_validate(
            {
                "post_id": 108,
                "category_id": 105,
                "id": 5,
                "created_at": datetime_exp,
                "updated_at": datetime_exp,
            }
        ),
    ]
    assert result == expected_result
    assert expected_row == session.categories


def test_store_post_categories_none(monkeypatch):
    datetime_exp = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))

    class MockSession:
        def __init__(self) -> None:
            self.actions = []
            self.categories = []

        @contextmanager
        def begin_nested(self):
            yield "session"

        def add_all(self, instances: list[PostCategory]):
            self.categories = instances

        def flush(self):
            for i in range(len(self.categories)):
                self.categories[i].id = 5
                self.categories[i].created_at = datetime_exp
                self.categories[i].updated_at = datetime_exp

    def mock_get_category_id(cat_code, session):
        if cat_code == "Toto":
            return 101
        return None

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    monkeypatch.setattr(store_content_module, "get_category_id", mock_get_category_id)

    categories = ["Toto", "tata", "Cat_01"]
    session = MockSession()
    result = cast(Any, store_post_categories)(108, categories, session)
    expected_result = True
    expected_row = [
        PostCategory.model_validate(
            {
                "post_id": 108,
                "category_id": 101,
                "id": 5,
                "created_at": datetime_exp,
                "updated_at": datetime_exp,
            }
        )
    ]
    assert result == expected_result
    assert expected_row == session.categories


def test_store_post_categories_fail(monkeypatch):
    datetime_exp = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))

    class MockSession:
        def __init__(self) -> None:
            self.actions = []
            self.categories = []

        @contextmanager
        def begin_nested(self):
            yield "session"

        def add_all(self, instances: list[PostCategory]):
            self.categories = instances

        def flush(self):
            print(0 / 0)
            for i in range(len(self.categories)):
                self.categories[i].id = 5
                self.categories[i].created_at = datetime_exp
                self.categories[i].updated_at = datetime_exp

    def mock_get_category_id(cat_code, session):
        if cat_code == "Toto":
            return 101
        return None

    monkeypatch.setattr(store_content_module, "Session", MockSession)
    monkeypatch.setattr(store_content_module, "get_category_id", mock_get_category_id)

    categories = ["Toto", "tata", "Cat_01"]
    session = MockSession()
    result = cast(Any, store_post_categories)(108, categories, session)
    expected_result = False
    assert result == expected_result


def test_content_to_post(monkeypatch):
    class MockPost:
        def __init__(self, content) -> None:
            if content["categories"] == "id_none":
                self.id = None
            elif content["categories"] == "id_true":
                self.id = 4
            else:
                self.id = 5

    def mock_store_post_from_content(content, publication_id, session):
        if content["categories"] == "post_none":
            return None
        else:
            return MockPost(content)

    def mock_store_post_categories(post_id, categories, session):
        return post_id == 4

    monkeypatch.setattr(
        store_content_module, "store_post_from_content", mock_store_post_from_content
    )
    monkeypatch.setattr(
        store_content_module, "store_post_categories", mock_store_post_categories
    )

    example_content_01 = {"categories": "post_none"}
    example_content_02 = {"categories": "id_none"}
    example_content_03 = {"categories": "id_true"}
    example_content_04 = {"categories": "id_false"}

    result_01 = cast(Any, content_to_post)(example_content_01, 404, "session")
    result_02 = cast(Any, content_to_post)(example_content_02, 404, "session")
    result_03 = cast(Any, content_to_post)(example_content_03, 404, "session")
    result_04 = cast(Any, content_to_post)(example_content_04, 404, "session")

    assert result_01 == False
    assert result_02 == False
    assert result_03 == True
    assert result_04 == False


def test_content_to_post_fail(monkeypatch):
    def mock_store_post_from_content(content, session):
        print(0 / 0)

    monkeypatch.setattr(
        store_content_module, "store_post_from_content", mock_store_post_from_content
    )
    example_content = {"categories": "post_none"}
    result = cast(Any, content_to_post)(example_content, 404, "session")

    assert result == False


def test_store_the_contents(monkeypatch):
    def mock_content_to_post(content, publication_id, session):
        return content

    def mock_store_publication(session):
        return 404

    class MockSession:
        def __init__(self) -> None:
            self.commit_done = False

        def commit(self):
            self.commit_done = True

    session = MockSession()

    @contextmanager
    def mock_get_session():
        yield session

    monkeypatch.setattr(
        store_content_module, "store_publication", mock_store_publication
    )
    monkeypatch.setattr(store_content_module, "content_to_post", mock_content_to_post)
    monkeypatch.setattr(store_content_module, "get_session", mock_get_session)

    state_01 = {"contents_to_post": [True, False, False, True]}
    state_02 = {"contents_to_post": [False, False]}

    result_01 = cast(Any, store_the_contents)(state_01)
    result_02 = cast(Any, store_the_contents)(state_02)

    expected_01 = {"post_store_validation": True}
    expected_02 = {"post_store_validation": False}

    assert result_01 == expected_01
    assert result_02 == expected_02


def test_store_the_contents_fail(monkeypatch):
    def mock_content_to_post(content, session):
        return content

    class MockSession:
        def __init__(self) -> None:
            self.commit_done = False

        def commit(self):
            print(0 / 0)

    session = MockSession()

    @contextmanager
    def mock_get_session():
        yield session

    monkeypatch.setattr(store_content_module, "content_to_post", mock_content_to_post)
    monkeypatch.setattr(store_content_module, "get_session", mock_get_session)

    state_01 = {"contents_to_post": [True, False, False, True]}
    state_02 = {"contents_to_post": [False, False]}

    result_01 = cast(Any, store_the_contents)(state_01)
    result_02 = cast(Any, store_the_contents)(state_02)

    expected_01 = {"post_store_validation": False}
    expected_02 = {"post_store_validation": False}

    assert result_01 == expected_01
    assert result_02 == expected_02


def test_store_publication(monkeypatch):
    datetime_exp = datetime(2026, 11, 10, 12, 0, tzinfo=ZoneInfo("localtime"))

    class MockSession:
        def __init__(self) -> None:
            self.actions = []
            self.pub = None

        @contextmanager
        def begin_nested(self):
            yield "session"

        def add(self, instance: Publication):
            self.pub = instance

        def flush(self):
            if self.pub is not None:
                self.pub.id = 404
                self.pub.created_at = datetime_exp
                self.pub.updated_at = datetime_exp

    monkeypatch.setattr(store_content_module, "Session", MockSession)

    result = cast(Any, store_publication)(MockSession())
    assert result == 404
