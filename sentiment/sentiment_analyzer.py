import pandas as pd
import sqlite3
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import logging

# Download the VADER lexicon (only needs to be done once)
nltk.download('vader_lexicon')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the SQLite database
try:
    conn = sqlite3.connect('data/db.sqlite')
    cursor = conn.cursor()
    logging.info("Connected to the SQLite database.")
except sqlite3.Error as e:
    logging.error(f"Database connection failed: {e}")
    raise

# Check and add missing columns
def ensure_columns_exist():
    cursor.execute("PRAGMA table_info(raw_articles)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'sentiment_score' not in columns:
        cursor.execute("ALTER TABLE raw_articles ADD COLUMN sentiment_score REAL")
        logging.info("Added 'sentiment_score' column.")
    if 'sentiment_label' not in columns:
        cursor.execute("ALTER TABLE raw_articles ADD COLUMN sentiment_label TEXT")
        logging.info("Added 'sentiment_label' column.")

ensure_columns_exist()

# Initialize the VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

# Fetch all articles from the raw_articles table
cursor.execute("SELECT id, title, summary FROM raw_articles")
articles = cursor.fetchall()
logging.info(f"Fetched {len(articles)} articles from the raw_articles table.")

# Analyze sentiment for each article
for article in articles:
    article_id, title, summary = article
    text = f"{title} {summary}"
    sentiment_scores = sid.polarity_scores(text)
    sentiment_score = sentiment_scores['compound']

    # Determine sentiment label
    if sentiment_score >= 0.05:
        sentiment_label = 'positive'
    elif sentiment_score <= -0.05:
        sentiment_label = 'negative'
    else:
        sentiment_label = 'neutral'

    # Update the article with sentiment score and label
    cursor.execute("""
        UPDATE raw_articles
        SET sentiment_score = ?, sentiment_label = ?
        WHERE id = ?
    """, (sentiment_score, sentiment_label, article_id))

# Load data into a DataFrame
df = pd.read_sql_query("SELECT * FROM raw_articles", conn)
logging.info(df)

# Commit the changes and close the connection
conn.commit()
conn.close()
logging.info("Sentiment analysis completed and database updated.")
