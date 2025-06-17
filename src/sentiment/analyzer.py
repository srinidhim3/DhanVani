import pandas as pd
import psycopg2
import psycopg2.extras
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import logging

# Download the VADER lexicon (only needs to be done once)
# try:
#     nltk.data.find('sentiment/vader_lexicon.zip')
# except nltk.downloader.DownloadError:
#     nltk.download('vader_lexicon')

from src.database import get_db_connection # Import from centralized location

def run_sentiment_analysis():
    """Fetches articles, analyzes sentiment, and updates the database."""
    logging.info("Starting sentiment analysis...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # Use DictCursor for dictionary-like rows
        logging.info("Connected to the SQLite database for sentiment analysis.")
    except Exception as e: # Catch generic Exception from get_db_connection
        logging.error(f"Database connection failed during sentiment analysis: {e}")
        return # Exit if DB connection fails

    # Ensure columns exist (idempotent operation, can be part of init_db or here)
    # For simplicity, assuming init_db in src.database.py now creates these columns.
    # If not, you can add the ensure_columns_exist logic here, using the 'cursor'.

    # Initialize the VADER sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Fetch articles that haven't been analyzed or need re-analysis
    # For simplicity, fetching all. Could be optimized to fetch only where sentiment_label IS NULL.
    cursor.execute("SELECT id, title, summary FROM raw_articles WHERE sentiment_label IS NULL") # More efficient
    articles = cursor.fetchall()
    logging.info(f"Fetched {len(articles)} articles for sentiment analysis.")

    updated_count = 0
    for article_row in articles:
        article_id, title, summary = article_row['id'], article_row['title'], article_row['summary']
        text_to_analyze = f"{title or ''} {summary or ''}".strip()

        if not text_to_analyze:
            logging.warning(f"Skipping article ID {article_id} due to empty title and summary.")
            continue
            
        sentiment_scores = sid.polarity_scores(text_to_analyze)
        compound_score = sentiment_scores['compound']

        # Determine sentiment label
        if compound_score >= 0.05:
            sentiment_label = 'positive'
        elif compound_score <= -0.05:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'

        # Update the article with sentiment score and label
        cursor.execute("""
            UPDATE raw_articles
            SET sentiment_score = ?, sentiment_label = ?
            WHERE id = %s
        """, (compound_score, sentiment_label, article_id)) # Using %s
        updated_count += cursor.rowcount

    conn.commit()
    logging.info(f"Sentiment analysis completed. Updated {updated_count} articles.")
    
    # Optional: Load data into a DataFrame for logging or further processing if needed
    # df = pd.read_sql_query("SELECT id, title, sentiment_label, sentiment_score FROM raw_articles", conn)
    # logging.info(f"Sample of analyzed data:\n{df.head()}")

    conn.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # init_db() # Ensure DB is initialized if running standalone
    run_sentiment_analysis()
