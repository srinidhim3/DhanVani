# import sqlite3 # No longer using SQLite as the primary DB
import psycopg2
import psycopg2.extras # For dictionary cursor
import logging
from typing import Optional
from .config import DATABASE_URL

def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """Helper to get a database connection."""
    if not DATABASE_URL:
        logging.error("DATABASE_URL is not configured.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to PostgreSQL database: {e}")
        return None

def init_db() -> None:
    """
    Initialize the raw_articles table in the PostgreSQL database.
    Note: For Supabase, you typically create tables via their UI or SQL editor.
    This function can be used for initial setup or ensuring schema.
    """
    conn: Optional[psycopg2.extensions.connection] = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_articles (
                id SERIAL PRIMARY KEY,
                title TEXT,
                link TEXT UNIQUE,
                published TIMESTAMP WITH TIME ZONE, -- More appropriate for PostgreSQL
                summary TEXT,
                source TEXT,
                type TEXT,          -- Retained from original scraper schema
                created_at TEXT,    -- Retained from original scraper schema
                sentiment_score REAL,
                sentiment_label TEXT
            )
        """)
        conn.commit()
        logging.info("Database table 'raw_articles' checked/initialized successfully.")
    except psycopg2.Error as e:
        logging.error(f"Error initializing database: {e}")
    except AttributeError: # If conn is None
        logging.error("Database connection could not be established for init_db.")
    finally:
        if conn is not None:
            conn.close()

# Example of how you might alter the table if needed, e.g., after initial creation
# def alter_table_example():
#     conn = get_db_connection()
#     if conn:
#         with conn.cursor() as cursor:
#             cursor.execute("ALTER TABLE raw_articles ALTER COLUMN published TYPE TIMESTAMP WITH TIME ZONE USING published::timestamp with time zone;")
#             conn.commit()
#         conn.close()