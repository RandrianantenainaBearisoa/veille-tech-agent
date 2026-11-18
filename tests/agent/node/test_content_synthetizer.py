from typing import Any, cast

from pydantic import BaseModel

from src.agent.node import content_synthetizer as content_synthetizer_module
from src.agent.node.content_synthetizer import (
    ContentFormat,
    content_synthetizer,
    create_content,
    try_create_content,
    validate_content,
    web_scrapping,
)


def test_content_synthetizer_01(monkeypatch):
    class MockContentType(BaseModel):
        data: str

    def mock_create_content(item):
        return item

    monkeypatch.setattr(content_synthetizer_module, "ContentType", MockContentType)
    monkeypatch.setattr(
        content_synthetizer_module, "create_content", mock_create_content
    )

    state = {
        "feed_items_final_list": [
            "item_1",
            "item_2",
            "item_3",
            "item_3",
            "item_4",
            "item_5",
        ]
    }

    result = cast(Any, content_synthetizer)(state)
    expected_result = {
        "contents_to_post": [
            "item_1",
            "item_2",
            "item_3",
            "item_3",
            "item_4",
            "item_5",
        ]
    }

    assert result == expected_result


def test_content_synthetizer_02(monkeypatch):
    class MockContentType(BaseModel):
        data: str

    def mock_create_content(item):
        return item

    monkeypatch.setattr(content_synthetizer_module, "ContentType", MockContentType)
    monkeypatch.setattr(
        content_synthetizer_module, "create_content", mock_create_content
    )

    state = {
        "feed_items_final_list": ["item_1", "item_2", None, "item_3", "item_4", None]
    }

    result = cast(Any, content_synthetizer)(state)
    expected_result = {
        "contents_to_post": [
            "item_1",
            "item_2",
            "item_3",
            "item_4",
        ]
    }

    assert result == expected_result


def test_content_synthetizer_fail(monkeypatch):
    class MockContentType(BaseModel):
        data: str

    def mock_create_content(item):
        print(0 / 0)
        return item

    monkeypatch.setattr(content_synthetizer_module, "ContentType", MockContentType)
    monkeypatch.setattr(
        content_synthetizer_module, "create_content", mock_create_content
    )

    state = {
        "feed_items_final_list": [
            "item_1",
            "item_2",
            "item_3",
            "item_3",
            "item_4",
            "item_5",
        ]
    }

    result = cast(Any, content_synthetizer)(state)
    expected_result = {}

    assert result == expected_result


def test_web_scrapping(monkeypatch):
    def mock_fetch_from_url(url):
        return f"fetched_{url}"

    def mock_extract_from_html(html):
        return f"extracted_{html}"

    monkeypatch.setattr(
        content_synthetizer_module, "fetch_from_url", mock_fetch_from_url
    )
    monkeypatch.setattr(
        content_synthetizer_module, "extract_from_html", mock_extract_from_html
    )

    result = web_scrapping("url")
    expected_result = "extracted_fetched_url"

    assert result == expected_result


def test_web_scrapping_fail(monkeypatch):
    def mock_fetch_from_url(url):
        print(0 / 0)
        return f"fetched_{url}"

    def mock_extract_from_html(html):
        return f"extracted_{html}"

    monkeypatch.setattr(
        content_synthetizer_module, "fetch_from_url", mock_fetch_from_url
    )
    monkeypatch.setattr(
        content_synthetizer_module, "extract_from_html", mock_extract_from_html
    )

    result = web_scrapping("url")
    expected_result = ""

    assert result == expected_result


example_content = """
langid.py is a robust, lightweight language detection library that offers high accuracy for general text while maintaining minimal dependencies and being markup-agnostic.
langid.py is a robust, lightweight language detection library that offers high accuracy for general text while maintaining minimal dependencies and being markup-agnostic.  It supports 97 languages and is particularly effective for longer documents and microblog data, often outperforming older tools like langdetect in speed and consistency.
However, it has notable limitations: it performs poorly on very short texts (under 60 characters) compared to modern alternatives like fastText or Lingua, and it is significantly slower than C-based libraries like pyCLD3. Consequently, it is best suited for legacy systems, environments requiring zero-dependency portability, or use cases involving longer text segments where its high accuracy and ease of integration are prioritized over raw inference speed.
"""
content_format_object = ContentFormat(
    title="titre",
    subtitle="sous tittre",
    icon_suggestions=["ico_01", "ico_02", "ico_03"],
    content=example_content,
    categories=[
        "AI",
        "WebDev",
        "Software",
    ],
)


def test_validate_content_01(monkeypatch):

    def mock_lang_validator(text_to_validate, expected_lang):
        return True

    monkeypatch.setattr(
        content_synthetizer_module, "lang_validator", mock_lang_validator
    )

    result = validate_content(content_format_object)
    expected_result = True

    assert result == expected_result


def test_validate_content_02(monkeypatch):

    def mock_lang_validator(text_to_validate, expected_lang):
        return False

    monkeypatch.setattr(
        content_synthetizer_module, "lang_validator", mock_lang_validator
    )

    result = validate_content(content_format_object)
    expected_result = False

    assert result == expected_result


def test_validate_content_03(monkeypatch):
    content_format_object = ContentFormat(
        title="titre",
        subtitle="sous tittre",
        icon_suggestions=["ico_01", "ico_02", "ico_03"],
        content=example_content,
        categories=[
            "AI",
            "WebDev",
            "Softwares",
        ],
    )

    def mock_lang_validator(text_to_validate, expected_lang):
        return False

    monkeypatch.setattr(
        content_synthetizer_module, "lang_validator", mock_lang_validator
    )

    result = validate_content(content_format_object)
    expected_result = False

    assert result == expected_result


def test_validate_content_04(monkeypatch):

    def mock_lang_validator(text_to_validate, expected_lang):
        print(0 / 0)
        return True

    monkeypatch.setattr(
        content_synthetizer_module, "lang_validator", mock_lang_validator
    )

    result = validate_content(content_format_object)
    expected_result = False

    assert result == expected_result


def test_try_create_content_01(monkeypatch):
    class MOCK_CONTENT_MAKER:
        def invoke(self, input):
            return content_format_object

    def mock_validate_content(content):
        return True

    monkeypatch.setattr(
        content_synthetizer_module, "CONTENT_MAKER", MOCK_CONTENT_MAKER()
    )
    monkeypatch.setattr(
        content_synthetizer_module, "validate_content", mock_validate_content
    )

    result = try_create_content(
        "title", "descri", "content", "here is a feed link", "here is the source"
    )
    expected_result = {
        "title": "titre",
        "subtitle": "sous tittre",
        "icon_suggestions": ["ico_01", "ico_02", "ico_03"],
        "content": example_content,
        "categories": [
            "AI",
            "WebDev",
            "Software",
        ],
        "feed": "here is a feed link",
        "source": "here is the source",
    }

    assert result == expected_result


def test_try_create_content_02(monkeypatch):
    class MOCK_CONTENT_MAKER:
        def invoke(self, input):
            return "toto"  # not an instance of ContentFormat

    def mock_validate_content(content):
        return True

    monkeypatch.setattr(
        content_synthetizer_module, "CONTENT_MAKER", MOCK_CONTENT_MAKER()
    )
    monkeypatch.setattr(
        content_synthetizer_module, "validate_content", mock_validate_content
    )

    result = try_create_content(
        "title", "descri", "content", "here is a feed link", "here is the source"
    )

    assert result is None


def test_try_create_content_03(monkeypatch):
    class MOCK_CONTENT_MAKER:
        def invoke(self, input):
            return content_format_object

    def mock_validate_content(content):
        return False

    monkeypatch.setattr(
        content_synthetizer_module, "CONTENT_MAKER", MOCK_CONTENT_MAKER()
    )
    monkeypatch.setattr(
        content_synthetizer_module, "validate_content", mock_validate_content
    )

    result = try_create_content(
        "title", "descri", "content", "here is a feed link", "here is the source"
    )

    assert result is None


example_item = {
    "title": "raw_title",
    "pub_date": "raw_date",
    "description": "raw_descri",
    "link": "raw_link",
    "feed": "raw_feed",
}


def test_create_content_01(monkeypatch):
    def mock_web_scrapping(url):
        return "raw_content"

    def mock_try_create_content(raw_title, raw_description, raw_content, feed, source):
        return f"{raw_title}_{raw_description}_{raw_content}_{feed}_{source}"

    monkeypatch.setattr(content_synthetizer_module, "web_scrapping", mock_web_scrapping)
    monkeypatch.setattr(
        content_synthetizer_module, "try_create_content", mock_try_create_content
    )

    result = cast(Any, create_content)(example_item)
    expected_result = "raw_title_raw_descri_raw_content_raw_feed_raw_link"

    assert result == expected_result


def test_create_content(monkeypatch):
    def mock_web_scrapping(url):
        return "raw_content"

    def mock_try_create_content(raw_title, raw_description, raw_content):
        return None

    monkeypatch.setattr(content_synthetizer_module, "web_scrapping", mock_web_scrapping)
    monkeypatch.setattr(
        content_synthetizer_module, "try_create_content", mock_try_create_content
    )

    result = cast(Any, create_content)(example_item)

    assert result is None
