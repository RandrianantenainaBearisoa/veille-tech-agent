from src.data.ingest_data.ingest_feeds import (
    ingest_rss_categories,
    ingest_rss_feeds,
)
from src.database.database import create_db_and_tables

create_db_and_tables(re_create=False)
ingest_rss_categories()
ingest_rss_feeds()
