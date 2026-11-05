from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from lxml import etree

from src.data.extract.extract_from_feeds import get_feed_items
from src.data.extract.feed_filters import filter_tech_item, is_feed_date_valid


def test_filter_tech_item():
    xml_str = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
    <channel>
        <title>Jeu de Test - Veille Tech</title>
        <link>https://example.com/rss</link>
        <description>Flux RSS de test pour valider le filtrage regex</description>
        <!--Pass-->
        <item>
        <title>Google Warns LLMjacking Attacks Are Costing Enterprise Cloud Accounts Millions</title>
        <description>Hackers target misconfigured API keys to run unauthorized LLM workloads in cloud environments.</description>
        <category>AI</category>
        <category>Security</category>
        <category>Cloud</category>
        <media:keywords>LLM, Google Cloud, AI security, vulnerability</media:keywords>
        </item>
        <!--Reject-->
        <item>
        <title>50% Off DoorDash Promo Code | November 2026</title>
        <description>Get the best discounts on food delivery using our exclusive November coupons.</description>
        <category>Deals</category>
        <category>Lifestyle</category>
        <media:keywords>DoorDash, Promo Code, Coupon, Discount</media:keywords>
        </item>
        <!--Pass-->
        <item>
        <title>Red Hat Patches 9.8-Rated Linux TCP RCE Flaw</title>
        <description>Ubuntu and Red Hat release urgent kernel updates to address a critical remote code execution vulnerability.</description>
        <category>DevOps</category>
        <category>Linux</category>
        <category>Security</category>
        <media:keywords>RCE, Linux, Patch, Vulnerability</media:keywords>
        </item>
        <!--Reject-->
        <item>
        <title>Beginner's Guide to REST APIs with Python</title>
        <description>A simple step-by-step tutorial on how to install requests and build your first API.</description>
        <category>Python</category>
        <category>Tutorial</category>
        <media:keywords>Python, Tutorial, Beginner's guide, REST API</media:keywords>
        </item>
        <!--Pass-->
        <item>
        <title>FastAPI 0.110 Released with Native Async Improvements</title>
        <description>The new version introduces faster routing performance and cleaner dependency injection.</description>
        <category>Python</category>
        <category>Backend</category>
        <media:keywords>FastAPI, Python, REST API, Framework</media:keywords>
        </item>
        <!--Reject-->
        <item>
        <title>Trump Revolts After Midterms Wipeout in New Jersey</title>
        <description>Political reactions and voting statistics from the latest local election results.</description>
        <category>Politics</category>
        <category>News</category>
        <media:keywords>Trump, Election results, Politics</media:keywords>
        </item>
        <!--Reject-->
        <item>
        <title>Optimizing Multipliers in Hardware: Multi-Thread Performance</title>
        <description>An in-depth look at architecture tips for CPU register allocation.</description>
        <category>Hardware</category>
        <category>Architecture</category>
        <media:keywords>Multipliers, Performance, CPU</media:keywords>
        </item>
        <!--Pass-->
        <item>
        <title>Laravel 11 Introduces Native Support for pgvector and Strict Types</title>
        <description>Modern PHP backend design now natively supports vector embeddings for AI applications.</description>
        <category>PHP</category>
        <category>Laravel</category>
        <category>PostgreSQL</category>
        <media:keywords>Laravel, PHP, pgvector, PostgreSQL, AI</media:keywords>
        </item>
        <!--Reject-->
        <item>
        <title>Best Wireless Earbuds Review (2026): Apple vs Bose</title>
        <description>We tested the top noise-canceling headphones to buy right now with 20% discount.</description>
        <category>Tech Review</category>
        <category>Shopping</category>
        <media:keywords>Review, Discount, Buy, Earbuds</media:keywords>
        </item>
        <!--Pass-->
        <item>
        <title>Deploying LangGraph Agents with Docker and Docker Compose</title>
        <description>How production infrastructure manages stateful multi-agent orchestrations at scale.</description>
        <category>AI</category>
        <category>DevOps</category>
        <media:keywords>LangGraph, Agent, Docker, Container, CI/CD</media:keywords>
        </item>

    </channel>
    </rss>    
"""
    items = get_feed_items(xml_str)
    results = []
    for item in items:
        results.append(filter_tech_item(item))

    expected_result = [True, False, True, False, True, False, False, True, False, True]

    assert results == expected_result


def test_is_feed_date_valid():
    now = datetime.now(ZoneInfo("localtime"))

    item_str_today = f"<item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l'injection de dépendances.</description><pubDate>{now.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><category>FastAPI</category></item>"
    item_str_yesterday = f"<item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l'injection de dépendances.</description><pubDate>{(now - timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><category>FastAPI</category></item>"
    item_str_2day_ago = f"<item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l'injection de dépendances.</description><pubDate>{(now - timedelta(days=2)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><category>FastAPI</category></item>"
    item_str_3day_ago = f"<item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l'injection de dépendances.</description><pubDate>{(now - timedelta(days=3)).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><category>FastAPI</category></item>"

    invalid_xml_0 = "<item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l'injection de dépendances.</description><category>FastAPI</category></item>"
    invalid_xml_1 = "<item><title>FastAPI 0.110 disponible</title><link>https://example.com/fastapi-0110</link><description>Amélioration des performances de routage et de l'injection de dépendances.</description><pubDate></pubDate><category>FastAPI</category></item>"

    item_today = etree.fromstring(
        item_str_today.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_str_yesterday = etree.fromstring(
        item_str_yesterday.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_2day_ago = etree.fromstring(
        item_str_2day_ago.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_str_3day_ago = etree.fromstring(
        item_str_3day_ago.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )

    item_str_no_date_0 = etree.fromstring(
        invalid_xml_0.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )
    item_str_no_date_1 = etree.fromstring(
        invalid_xml_1.encode("utf-8"),
        parser=etree.XMLParser(encoding="utf-8"),
    )

    today_is_valid = is_feed_date_valid(item_today)
    yesterday_is_valid = is_feed_date_valid(item_str_yesterday)
    two_day_ago_is_valid = is_feed_date_valid(item_2day_ago)
    three_day_ago_is_valid = is_feed_date_valid(item_str_3day_ago)
    no_date_0_is_valid = is_feed_date_valid(item_str_no_date_0)
    no_date_1_is_valid = is_feed_date_valid(item_str_no_date_1)

    assert (
        today_is_valid
        and yesterday_is_valid
        and not (two_day_ago_is_valid)
        and not (three_day_ago_is_valid)
        and not (no_date_0_is_valid)
        and not (no_date_1_is_valid)
    )
