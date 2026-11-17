from email.utils import parsedate_to_datetime

from lxml import etree

from src.data.extract import extract_from_feeds as extract_from_feeds_module
from src.data.extract.extract_from_feeds import (
    FeedItem,
    extract_from_html,
    fetch_from_url,
    get_feed_item_data,
    get_feed_items,
    get_feeds,
)


def test_get_feeds(monkeypatch):
    topics = [
        {"feeds": ["feed_t_1_1", "feed_t_1_2", "feed_t_1_3", "feed_t_1_4"]},
        {"feeds": ["feed_t_2_1", "feed_t_2_2", "feed_t_2_3", "feed_t_2_4"]},
        {"feeds": ["feed_t_3_1", "feed_t_3_2", "feed_t_3_3", "feed_t_3_4"]},
    ]

    def mock_get_feed_topics():
        return topics

    monkeypatch.setattr(
        extract_from_feeds_module, "get_feed_topics", mock_get_feed_topics
    )
    feeds = get_feeds()

    expected_feeds = [
        "feed_t_1_1",
        "feed_t_1_2",
        "feed_t_1_3",
        "feed_t_1_4",
        "feed_t_2_1",
        "feed_t_2_2",
        "feed_t_2_3",
        "feed_t_2_4",
        "feed_t_3_1",
        "feed_t_3_2",
        "feed_t_3_3",
        "feed_t_3_4",
    ]

    assert feeds == expected_feeds


def test_get_feeds_fail(monkeypatch):
    topics = [
        {"feeds": ["feed_t_1_1", "feed_t_1_2", "feed_t_1_3", "feed_t_1_4"]},
        {"feed": ["feed_t_2_1", "feed_t_2_2", "feed_t_2_3", "feed_t_2_4"]},
        {"feeds": ["feed_t_3_1", "feed_t_3_2", "feed_t_3_3", "feed_t_3_4"]},
    ]

    def mock_get_feed_topics():
        return topics

    monkeypatch.setattr(
        extract_from_feeds_module, "get_feed_topics", mock_get_feed_topics
    )
    feeds = get_feeds()

    expected_feeds = [
        "feed_t_1_1",
        "feed_t_1_2",
        "feed_t_1_3",
        "feed_t_1_4",
        "feed_t_3_1",
        "feed_t_3_2",
        "feed_t_3_3",
        "feed_t_3_4",
    ]

    assert feeds == expected_feeds


def test_get_feeds_fail_2(monkeypatch):
    topics = [
        {"feeds": ["feed_t_1_1", "feed_t_1_2", "feed_t_1_3", "feed_t_1_4"]},
        {"feed": ["feed_t_2_1", "feed_t_2_2", "feed_t_2_3", "feed_t_2_4"]},
        {"feeds": ["feed_t_3_1", "feed_t_3_2", "feed_t_3_3", "feed_t_3_4"]},
    ]

    def mock_get_feed_topics():
        print(0 / 0)
        return topics

    monkeypatch.setattr(
        extract_from_feeds_module, "get_feed_topics", mock_get_feed_topics
    )
    feeds = get_feeds()

    expected_feeds = []

    assert feeds == expected_feeds


def test_fetch_from_url(monkeypatch):
    class MockTrafilatura:
        @classmethod
        def fetch_url(cls, url):
            return url

    monkeypatch.setattr(extract_from_feeds_module, "trafilatura", MockTrafilatura)

    html = fetch_from_url("http://fake-url.com")

    assert html == "http://fake-url.com"


def test_fetch_from_url_fail(monkeypatch):
    class MockTrafilatura:
        @classmethod
        def fetch_url(cls, url):
            print(0 / 0)
            return url

    monkeypatch.setattr(extract_from_feeds_module, "trafilatura", MockTrafilatura)

    html = fetch_from_url("http://fake-url.com")

    assert html == None


def test_extract_from_html(monkeypatch):
    class MockTrafilatura:
        @classmethod
        def fetch_url(cls, url):
            print(0 / 0)
            return url

    monkeypatch.setattr(extract_from_feeds_module, "trafilatura", MockTrafilatura)

    result = extract_from_html("toto")

    assert result == ""


def test_get_feed_items():
    xml_sample = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Veille Tech Dev</title><link>https://mon-site-veille.com</link><description>Actualités sélectionnées pour développeurs</description><item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l\'injection de dépendances.</description><pubDate>Wed, 04 Nov 2026 10:00:00 +0000</pubDate><category>FastAPI</category></item><item><title>Laravel 11 : Support natif des types stricts</title><link>https://example.com/laravel-11-strict-types</link><description>Nouveautés sur la gestion des bases de données et requêtes typées.</description><pubDate>Wed, 04 Nov 2026 14:30:00 +0000</pubDate><category>Laravel</category></item></channel></rss>'
    items = get_feed_items(xml_sample)

    assert len(items) == 2

    titles = [
        "FastAPI 0.110 disponible",
        "Laravel 11 : Support natif des types stricts",
    ]

    for i, item in enumerate(items):
        item_title = item.find("title")
        if item_title is not None:
            assert item_title.text == titles[i]
        else:
            assert False


def test_get_feed_items_fail():
    xml_sample = '<?xml version="1.0" encoding="UTF-8"?><rss '
    items = get_feed_items(xml_sample)

    assert items == []


def test_get_feed_item_data():
    item_ok_str = """<item>
            <title>UK Officials Said AI Would Add £400 Billion to the Economy. That Figure Mainly Came From Google</title>
            <link>https://www.wired.com/story/uk-officials-said-ai-would-add-400-billion-to-the-economy-that-figure-mainly-came-from-google/</link>
            <pubDate>Wed, 04 Nov 2026 13:49:51 +0000</pubDate>
            <description>The AI minister now concedes the estimated figure is less than a third of that. Researchers blame the country’s slow rate of adoption</description>
        </item>"""
    item_no_title_str = """<item>
            <link>https://www.wired.com/story/uk-officials-said-ai-would-add-400-billion-to-the-economy-that-figure-mainly-came-from-google/</link>
            <pubDate>Wed, 04 Nov 2026 13:49:51 +0000</pubDate>
            <description>The AI minister now concedes the estimated figure is less than a third of that. Researchers blame the country’s slow rate of adoption</description>
        </item>"""
    item_no_link_str = """<item>
            <title>UK Officials Said AI Would Add £400 Billion to the Economy. That Figure Mainly Came From Google</title>
            <pubDate>Wed, 04 Nov 2026 13:49:51 +0000</pubDate>
            <description>The AI minister now concedes the estimated figure is less than a third of that. Researchers blame the country’s slow rate of adoption</description>
        </item>"""
    item_no_pub_date_str = """<item>
            <title>UK Officials Said AI Would Add £400 Billion to the Economy. That Figure Mainly Came From Google</title>
            <link>https://www.wired.com/story/uk-officials-said-ai-would-add-400-billion-to-the-economy-that-figure-mainly-came-from-google/</link>
            <description>The AI minister now concedes the estimated figure is less than a third of that. Researchers blame the country’s slow rate of adoption</description>
        </item>"""
    item_no_descri_str = """<item>
            <title>UK Officials Said AI Would Add £400 Billion to the Economy. That Figure Mainly Came From Google</title>
            <link>https://www.wired.com/story/uk-officials-said-ai-would-add-400-billion-to-the-economy-that-figure-mainly-came-from-google/</link>
            <pubDate>Wed, 04 Nov 2026 13:49:51 +0000</pubDate>
        </item>"""

    item_ok = etree.fromstring(
        item_ok_str.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )

    expected_result = FeedItem(
        title="UK Officials Said AI Would Add £400 Billion to the Economy. That Figure Mainly Came From Google",
        pub_date=parsedate_to_datetime("Wed, 04 Nov 2026 13:49:51 +0000"),
        description="The AI minister now concedes the estimated figure is less than a third of that. Researchers blame the country’s slow rate of adoption",
        link="https://www.wired.com/story/uk-officials-said-ai-would-add-400-billion-to-the-economy-that-figure-mainly-came-from-google/",
        feed="https://www.wired.com/",
    )

    item_no_title = etree.fromstring(
        item_no_title_str.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_no_link = etree.fromstring(
        item_no_link_str.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_no_pub_date = etree.fromstring(
        item_no_pub_date_str.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_no_descri = etree.fromstring(
        item_no_descri_str.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )

    result_ok = get_feed_item_data(item_ok, "https://www.wired.com/")
    result_no_title = get_feed_item_data(item_no_title, "https://www.wired.com/")
    result_no_link = get_feed_item_data(item_no_link, "https://www.wired.com/")
    result_no_pub_date = get_feed_item_data(item_no_pub_date, "https://www.wired.com/")
    result_no_descri = get_feed_item_data(item_no_descri, "https://www.wired.com/")

    assert result_ok == expected_result
    assert (
        result_no_title == None
        and result_no_link == None
        and result_no_pub_date == None
        and result_no_descri == None
    )


def test_get_feed_item_data_fail(monkeypatch):
    def mock_get_feed_item_pub_date(item):
        print(0 / 0)

    monkeypatch.setattr(
        extract_from_feeds_module, "get_feed_item_pub_date", mock_get_feed_item_pub_date
    )

    item_ok_str = """<item>
            <title>UK Officials Said AI Would Add £400 Billion to the Economy. That Figure Mainly Came From Google</title>
            <link>https://www.wired.com/story/uk-officials-said-ai-would-add-400-billion-to-the-economy-that-figure-mainly-came-from-google/</link>
            <pubDate>Wed, 04 Nov 2026 13:49:51 +0000</pubDate>
            <description>The AI minister now concedes the estimated figure is less than a third of that. Researchers blame the country’s slow rate of adoption</description>
        </item>"""
    item_ok = etree.fromstring(
        item_ok_str.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    result = get_feed_item_data(item_ok, "https://www.wired.com/")

    assert result == None
