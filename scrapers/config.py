import os

# Config (can be overridden by environment variables)
DB_PATH = os.getenv("DB_PATH", "data/db.sqlite")

def init_config():
    # Ensure data folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
