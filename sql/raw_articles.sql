create database dhanvani;

CREATE SCHEMA stage;

CREATE TABLE IF NOT EXISTS stage.raw_articles (
                id SERIAL PRIMARY KEY,
                title TEXT,
                link TEXT UNIQUE,
                published TIMESTAMP WITH TIME ZONE, -- More appropriate for PostgreSQL
                summary TEXT,
                source TEXT,
                type TEXT,          -- Retained from original scraper schema
                created_at TEXT,    -- Retained from original scraper schema
                sentiment_score REAL,
                sentiment_label TEXT
            );
