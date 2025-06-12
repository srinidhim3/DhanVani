from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB connection helper
def get_db_connection():
    conn = sqlite3.connect("data/db.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


# Pydantic model
class Article(BaseModel):
    id: int
    title: str
    url: str
    published: str
    source: str
    sentiment_label: str


# /articles endpoint with filters and pagination
@app.get("/articles", response_model=List[Article])
def get_articles(
    sentiment_label: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    published: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    limit: int = Query(10000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM raw_articles WHERE 1=1"
        params = []

        # treat empty strings as None (no filter)
        if sentiment_label == "":
            sentiment_label = None
        if source == "":
            source = None

        if sentiment_label:
            query += " AND sentiment_label = ?"
            params.append(sentiment_label)
        if source:
            query += " AND source = ?"
            params.append(source)
        if published:
            query += " AND published LIKE ?"
            params.append(f"{published}%")

        query += " ORDER BY published DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        articles = cursor.fetchall()
        conn.close()
        articles_list = [
            {
                **{k: v for k, v in dict(article).items() if k != "link"},
                "url": dict(article).get("link"),
            }
            for article in articles
        ]
        return articles_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Extra endpoint for sentiment summary
@app.get("/sentiment-summary")
def get_sentiment_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT sentiment_label, COUNT(*) as count
            FROM raw_articles
            GROUP BY sentiment_label
        """
        )
        results = cursor.fetchall()
        conn.close()
        return {row["sentiment_label"]: row["count"] for row in results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
