import os

# Centralized Config
# DB_PATH = os.getenv("DB_PATH", "data/db.sqlite") # No longer primary DB path
DATABASE_URL = os.getenv("DATABASE_URL") # For Supabase PostgreSQL

# Ensure data folder exists - can be called by main application entry points
def init_app_config():
    # os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) # Not needed for remote DB
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL environment variable is not set.")