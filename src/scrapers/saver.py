# import sqlite3 # No longer using SQLite
import psycopg2
import logging
from datetime import datetime, timezone
from typing import List, Any, Optional
from ..database import get_db_connection # Use the centralized connection getter

def save_articles(articles: List[Any], source_name: str) -> None:
    """Save articles to the PostgreSQL database."""
    if not articles:
        logging.warning("No articles to save.")
        return
    conn: Optional[psycopg2.extensions.connection] = None
    try:
        conn = get_db_connection()
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
                    INSERT INTO stage.raw_articles
                    (title, link, published, summary, source, type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (link) DO NOTHING
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
                conn.rollback()

        conn.commit()
        logging.info(f"Saved {count_inserted} new articles.")
    except Exception as e:
        logging.error(f"Error saving articles to database: {e}")
    finally:
        if conn is not None:
            conn.close()
