from fastapi import FastAPI, Query
from typing import Optional
import sqlite3

app = FastAPI()

# Database connection
def get_db_connection():
    conn = sqlite3.connect('data/db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint: /articles
@app.get("/articles")
def get_articles(
    sentiment_label: Optional[str] = Query(None, description="Filter by sentiment label (positive, neutral, negative)"),
    source: Optional[str] = Query(None, description="Filter by source"),
    published: Optional[str] = Query(None, description="Filter by published date (YYYY-MM-DD)")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM raw_articles WHERE 1=1"
    params = []

    if sentiment_label:
        query += " AND sentiment_label = ?"
        params.append(sentiment_label)
    if source:
        query += " AND source = ?"
        params.append(source)
    if published:
        query += " AND published LIKE ?"
        params.append(f"{published}%")

    cursor.execute(query, params)
    articles = cursor.fetchall()
    conn.close()

    return [dict(article) for article in articles]
