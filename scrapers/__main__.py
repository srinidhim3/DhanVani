import logging
from scrapers.config import init_config
from scrapers.db import init_db
from scrapers.fetcher import fetch_articles
from scrapers.saver import save_articles
from scrapers.sources import SOURCES

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    init_config()
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
