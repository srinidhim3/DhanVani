import logging
import os
from fastapi import FastAPI, Query, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel
from src.database import get_db_connection, init_db  # Ensure init_db is called appropriately (e.g., on startup)
from src.scheduler import perform_scraping_and_analysis # Import the task function
import psycopg2.extras # For DictCursor

# --- Environment Variables ---
# Expected: SCRAPER_API_SECRET (for securing the trigger endpoint)
# Expected: DATABASE_URL (for Supabase connection, handled by src.config & src.database)
SCRAPER_API_SECRET = os.getenv("SCRAPER_API_SECRET")

app = FastAPI()

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Article(BaseModel):
    id: int
    title: str
    url: str # Note: DB stores 'link', API maps it
    published: str # Consider datetime type if more precision is needed by clients
    source: str
    sentiment_label: str

class ScraperStatus(BaseModel):
    status: str
    message: str

# --- Database Dependency ---
# This ensures that init_db is called once when the application starts
# For Render, you might also run init_db as part of a build or release command.
@app.on_event("startup")
async def startup_event():
    logging.info("Application startup: Initializing database schema if necessary...")
    # init_db() # Call this to ensure tables are created.
    # Be cautious if your Supabase tables are managed entirely via Supabase UI/migrations.
    # If so, this call might be redundant or could be used to verify connection.
    conn = get_db_connection()
    if conn:
        logging.info("Successfully connected to the database on startup.")
        conn.close()
    else:
        logging.error("Failed to connect to the database on startup.")


# --- API Endpoints ---

@app.get("/articles", response_model=List[Article])
def get_articles(
    sentiment_label: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    published: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    limit: int = Query(10000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=503, detail="Database service unavailable")

        # Use DictCursor for dictionary-like row access
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT id, title, link, published, source, sentiment_label FROM stage.raw_articles WHERE 1=1" # Explicitly list columns
        params = []

        if sentiment_label == "": sentiment_label = None
        if source == "": source = None

        if sentiment_label:
            query += " AND sentiment_label = %s"
            params.append(sentiment_label)
        if source:
            query += " AND source = %s"
            params.append(source)
        if published:
            # Ensure 'published' column is a date or timestamp type for efficient querying
            # If it's TEXT, LIKE is okay. If TIMESTAMP, adjust query.
            # Assuming 'published' is TIMESTAMP WITH TIME ZONE as per database.py change
            query += " AND DATE(published) = %s" # Cast to DATE for YYYY-MM-DD comparison
            params.append(published)

        query += " ORDER BY published DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params)) # psycopg2 expects a tuple for params
        articles_db = cursor.fetchall()
        
        articles_list = [
            Article(
                id=row["id"],
                title=row["title"],
                url=row["link"], # Map 'link' from DB to 'url' in response
                published=str(row["published"]), # Convert datetime to string
                source=row["source"],
                sentiment_label=row["sentiment_label"]
            ) for row in articles_db
        ]
        return articles_list

    except psycopg2.Error as db_err:
        logging.error(f"Database error in /articles: {db_err}")
        raise HTTPException(status_code=500, detail="Internal database error")
    except Exception as e:
        logging.error(f"Unexpected error in /articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@app.get("/sentiment-summary")
def get_sentiment_summary():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            """
            SELECT sentiment_label, COUNT(*) as count
            FROM stage.raw_articles
            GROUP BY sentiment_label
            """
        )
        results = cursor.fetchall()
        return {row["sentiment_label"]: row["count"] for row in results}
    except psycopg2.Error as db_err:
        logging.error(f"Database error in /sentiment-summary: {db_err}")
        raise HTTPException(status_code=500, detail="Internal database error")
    except Exception as e:
        logging.error(f"Unexpected error in /sentiment-summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.get("/sources", response_model=List[str])
def get_all_sources():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=503, detail="Database service unavailable")

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT DISTINCT source FROM stage.raw_articles WHERE source IS NOT NULL AND source != '' ORDER BY source")
        sources = [row["source"] for row in cursor.fetchall()]
        # DISTINCT and ORDER BY in SQL should handle deduplication and sorting
        return sources
    except psycopg2.Error as db_err:
        logging.error(f"Database error in /sources: {db_err}")
        raise HTTPException(status_code=500, detail="Internal database error")
    except Exception as e:
        logging.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

# --- New Scraper Trigger Endpoint ---
@app.post("/trigger-scraper", response_model=ScraperStatus)
async def trigger_scraper_endpoint(
    background_tasks: BackgroundTasks,
    x_scraper_secret: Optional[str] = Header(None)
):
    if not SCRAPER_API_SECRET:
        logging.error("SCRAPER_API_SECRET is not configured on the server.")
        raise HTTPException(status_code=500, detail="Scraper trigger is not configured.")
    if x_scraper_secret != SCRAPER_API_SECRET:
        logging.warning("Unauthorized attempt to trigger scraper.")
        raise HTTPException(status_code=403, detail="Invalid or missing secret.")
    try:
        logging.info("Scraper task triggered via API.")
        background_tasks.add_task(perform_scraping_and_analysis)
        return ScraperStatus(status="success", message="Scraping and analysis task started in background.")
    except Exception as e:
        logging.error(f"Error during API-triggered scraper task: {e}")
        raise HTTPException(status_code=500, detail=f"Scraper task failed: {str(e)}")

