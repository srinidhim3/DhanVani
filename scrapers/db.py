import sqlite3
import logging
from typing import Optional
from scrapers.config import DB_PATH

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
