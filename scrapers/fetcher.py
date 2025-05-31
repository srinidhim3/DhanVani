import requests
import feedparser
import logging
from typing import List, Any, Optional

def fetch_articles(source: dict) -> Optional[List[Any]]:
    """Fetch articles from the RSS feed."""
    try:
        logging.info(f"Fetching RSS feed from {source['url']} ...")
        response = requests.get(source['url'], timeout=10, headers=source.get('headers'), verify=False)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed.entries
    except Exception as e:
        logging.error(f"Error fetching RSS feed: {e}")
        return None
