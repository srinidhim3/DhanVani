import os
import requests
import sqlite3
import feedparser
from datetime import datetime, timezone
import logging
from typing import List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Config (can be overridden by environment variables)
RSS_URL = os.getenv("RSS_URL", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms")
DB_PATH = os.getenv("DB_PATH", "data/db.sqlite")

# Ensure data folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db() -> None:
    """Initialize the raw_articles table in the SQLite database."""
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                link TEXT UNIQUE,
                published TEXT,
                summary TEXT,
                source TEXT,
                type TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        if conn is not None:
            conn.close()

def fetch_articles() -> Optional[List[Any]]:
    """Fetch articles from the RSS feed."""
    try:
        logging.info(f"Fetching RSS feed from {RSS_URL} ...")
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed.entries
    except Exception as e:
        logging.error(f"Error fetching RSS feed: {e}")
        return None

def save_articles(articles: List[Any]) -> None:
    """Save articles to the SQLite database."""
    if not articles:
        logging.warning("No articles to save.")
        return
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        count_inserted = 0

        for entry in articles:
            try:
                title = getattr(entry, "title", None)
                link = getattr(entry, "link", None)
                published = getattr(entry, "published", None)
                summary = getattr(entry, "summary", None)
                if not (title and link and published):
                    logging.warning(f"Skipping incomplete entry: {entry}")
                    continue

                cursor.execute("""
                    INSERT OR IGNORE INTO raw_articles
                    (title, link, published, summary, source, type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    title,
                    link,
                    published,
                    summary,
                    "Economic Times",
                    "news",
                    datetime.now(timezone.utc).isoformat()
                ))
                count_inserted += cursor.rowcount
            except Exception as e:
                logging.error(f"Error inserting article: {e}")

        conn.commit()
        logging.info(f"Saved {count_inserted} new articles.")
    except Exception as e:
        logging.error(f"Error saving articles to database: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    init_db()
    articles = fetch_articles()
    if articles is not None:
        save_articles(articles)
    logging.info("News scraping completed.")