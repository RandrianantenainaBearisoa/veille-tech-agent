from unittest.mock import MagicMock

from src.data.ingest_data import ingest_feeds as ingest_feeds_module
from src.data.ingest_data.ingest_feeds import (
    get_feed_data,
    get_feed_title,
    get_stored_category_codes,
    get_stored_feeds,
    ingest_rss_categories,
    ingest_rss_feeds,
)
from src.database.models.table import Category, Feed


def test_get_stored_category_codes_returns_set():
    session = MagicMock()
    session.exec.return_value.all.return_value = ["AI", "Cloud", "AI"]

    result = get_stored_category_codes(session)

    assert result == {"AI", "Cloud"}


def test_get_stored_category_codes_returns_empty_set_on_error():
    session = MagicMock()
    session.exec.side_effect = RuntimeError("database unavailable")

    assert get_stored_category_codes(session) == set()


def test_get_stored_feeds_returns_set():
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        "https://example.com/rss",
        "https://example.com/rss",
        "https://example-2.com/rss",
    ]

    assert get_stored_feeds(session) == {
        "https://example.com/rss",
        "https://example-2.com/rss",
    }


def test_get_stored_feeds_returns_empty_set_on_error():
    session = MagicMock()
    session.exec.side_effect = RuntimeError("database unavailable")

    assert get_stored_feeds(session) == set()


def test_get_feed_title_reads_rss_title():
    xml = "<rss><channel><title>  Tech Updates  </title></channel></rss>"

    assert get_feed_title(xml) == "Tech Updates"


def test_get_feed_title_uses_first_child_when_channel_title_is_missing():
    assert get_feed_title("<feed><title>Atom Updates</title></feed>") == "Atom Updates"


def test_get_feed_title_returns_missing_title_for_invalid_xml():
    assert get_feed_title("<rss>") == "MISSING_TITLE"


def test_get_feed_data_skips_stored_feed(monkeypatch):
    feed_url = "https://example.com/rss"
    monkeypatch.setattr(
        ingest_feeds_module, "get_stored_feeds", lambda session: {feed_url}
    )
    fetch_from_url = MagicMock()
    monkeypatch.setattr(ingest_feeds_module, "fetch_from_url", fetch_from_url)

    assert get_feed_data(feed_url, MagicMock()) is None
    fetch_from_url.assert_not_called()


def test_get_feed_data_returns_title_and_url(monkeypatch):
    feed_url = "https://example.com/rss"
    xml = "<rss><channel><title>Example News</title></channel></rss>"
    monkeypatch.setattr(ingest_feeds_module, "get_stored_feeds", lambda session: set())
    monkeypatch.setattr(ingest_feeds_module, "fetch_from_url", lambda url: xml)

    assert get_feed_data(feed_url, MagicMock()) == {
        "name": "Example News",
        "url": feed_url,
    }


def test_get_feed_data_uses_missing_title_when_fetch_fails(monkeypatch):
    feed_url = "https://example.com/rss"
    monkeypatch.setattr(ingest_feeds_module, "get_stored_feeds", lambda session: set())
    monkeypatch.setattr(ingest_feeds_module, "fetch_from_url", lambda url: None)

    assert get_feed_data(feed_url, MagicMock()) == {
        "name": "MISSING_TITLE",
        "url": feed_url,
    }


def test_ingest_rss_categories_stores_only_new_categories(monkeypatch):
    session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = session
    monkeypatch.setattr(ingest_feeds_module, "get_session", lambda: session_context)
    monkeypatch.setattr(
        ingest_feeds_module,
        "get_stored_category_codes",
        lambda current_session: {"AI"},
    )
    monkeypatch.setattr(
        ingest_feeds_module,
        "get_rss_categories",
        lambda: {"AI": "Intelligence artificielle", "Cloud": "Cloud"},
    )

    ingest_rss_categories()

    session.add_all.assert_called_once()
    categories = session.add_all.call_args.args[0]
    assert len(categories) == 1
    assert isinstance(categories[0], Category)
    assert categories[0].code == "Cloud"
    assert categories[0].fr_label == "Cloud"
    session.commit.assert_called_once()


def test_ingest_rss_categories_does_not_commit_when_all_categories_exist(
    monkeypatch,
):
    session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = session
    monkeypatch.setattr(ingest_feeds_module, "get_session", lambda: session_context)
    monkeypatch.setattr(
        ingest_feeds_module,
        "get_stored_category_codes",
        lambda current_session: {"AI"},
    )
    monkeypatch.setattr(
        ingest_feeds_module,
        "get_rss_categories",
        lambda: {"AI": "Intelligence artificielle"},
    )

    ingest_rss_categories()

    session.add_all.assert_not_called()
    session.commit.assert_not_called()


def test_ingest_rss_feeds_stores_new_feeds(monkeypatch):
    session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = session
    monkeypatch.setattr(ingest_feeds_module, "get_session", lambda: session_context)
    monkeypatch.setattr(
        ingest_feeds_module,
        "get_feeds",
        lambda: ["https://example.com/rss", "https://stored.example/rss"],
    )
    monkeypatch.setattr(
        ingest_feeds_module,
        "get_feed_data",
        lambda url, current_session: (
            {"name": "Example News", "url": url}
            if url == "https://example.com/rss"
            else None
        ),
    )

    ingest_rss_feeds()

    session.add_all.assert_called_once()
    feeds = session.add_all.call_args.args[0]
    assert len(feeds) == 1
    assert isinstance(feeds[0], Feed)
    assert feeds[0].name == "Example News"
    assert feeds[0].url == "https://example.com/rss"
    session.commit.assert_called_once()


def test_ingest_rss_feeds_does_not_commit_when_no_new_feeds(monkeypatch):
    session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = session
    monkeypatch.setattr(ingest_feeds_module, "get_session", lambda: session_context)
    monkeypatch.setattr(ingest_feeds_module, "get_feeds", list)

    ingest_rss_feeds()

    session.add_all.assert_not_called()
    session.commit.assert_not_called()
