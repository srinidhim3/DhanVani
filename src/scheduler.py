# import schedule # No longer using the schedule library here
# import time     # No longer using time.sleep here
import subprocess
import warnings
import logging

# Import the main functions from your modules
from src.scrapers.__main__ import main as run_scraper_main
from src.sentiment.analyzer import run_sentiment_analysis

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def perform_scraping_and_analysis():
    """Performs the scraping and sentiment analysis tasks."""
    logging.info("Starting task: Scraping and Sentiment Analysis")
    try:
        logging.info("Running scraper...")
        run_scraper_main() # Call the scraper's main function
        logging.info("Scraping finished.")

        logging.info("Running sentiment analysis...")
        run_sentiment_analysis() # Call the sentiment analysis function
        logging.info("Sentiment analysis finished.")
    except Exception as e:
        logging.error(f"Error during scheduled task: {e}")
    logging.info("Task: Scraping and Sentiment Analysis completed.")

# The following block is removed as scheduling will be external
# # Run immediately once
# # perform_scraping_and_analysis() # Can be called for testing if needed
# # Schedule the task every 30 minutes
# # schedule.every(30).minutes.do(perform_scraping_and_analysis) ...
