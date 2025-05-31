import sqlite3
import logging
from datetime import datetime, timezone
from typing import List, Any, Optional
from scrapers.config import DB_PATH

def save_articles(articles: List[Any], source_name: str) -> None:
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
                summary = getattr(entry, "summary", None) or getattr(entry, "description", None) or getattr(entry, "title", None)
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
                    source_name,
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
