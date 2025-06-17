import logging
from src.config import init_app_config # Updated import
from src.database import init_db      # Updated import
from .fetcher import fetch_articles   # Relative import within the package
from .saver import save_articles      # Relative import
from .sources import SOURCES          # Relative import

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    init_app_config() # Call the centralized config initialization
    init_db()

    for source in SOURCES:
        for url in source["urls"]:
            logging.info(f"Scraping from {source['name']} - {url}")
            articles = fetch_articles({"url": url, "headers": source.get("headers")})
            if articles is not None:
                save_articles(articles, source["name"])

    logging.info("News scraping completed.")

if __name__ == "__main__":
    main()
