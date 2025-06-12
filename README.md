# DhanVani: Financial News Sentiment Analysis Platform

DhanVani is a comprehensive platform for scraping, analyzing, and visualizing sentiment in financial news articles from multiple sources. It features automated news collection, sentiment analysis, a REST API, and an interactive dashboard for data exploration.

---

## Features

- **Automated News Scraping:** Collects articles from multiple financial news sources.
- **Sentiment Analysis:** Assigns sentiment labels (positive, neutral, negative) to articles.
- **REST API:** Serves articles and sentiment data for integration or further analysis.
- **Interactive Dashboard:** Visualizes sentiment trends, article counts, and word clouds.
- **Scheduler:** Automates scraping and analysis at regular intervals.

---

## Project Structure

```
DhanVani/
├── api/                  # FastAPI backend for serving data
│   └── app.py
├── dashboard/            # Dash/Plotly dashboard for visualization
│   └── dashboard.py
├── scrapers/             # News scrapers for various sources
│   └── ...
├── sentiment/            # Sentiment analysis logic
│   └── sentiment_analyzer.py
├── data/                 # SQLite database and related files
│   └── db.sqlite
├── run_every_30_minutes.py # Scheduler script
├── environment.yml       # Conda environment specification
└── README.md             # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd DhanVani
```

### 2. Create the Conda Environment

```bash
conda env create -f environment.yml
conda activate dhanvani
```

### 3. Initialize the Database

Ensure the SQLite database exists at `data/db.sqlite`. If not, run the scrapers or provide a migration script.

---

## Running the Components

### 1. Start the FastAPI Backend

```bash
uvicorn api.app:app --reload
```
- The API will be available at [http://localhost:8000](http://localhost:8000).

### 2. Start the Dashboard

```bash
python dashboard/dashboard.py
```
- The dashboard will be available at [http://localhost:8050](http://localhost:8050).

### 3. Run the Scrapers

From the project root or `scrapers/` directory:

```bash
python scrapers/<scraper_name>.py
```
- Replace `<scraper_name>.py` with the actual scraper script for each news source.

### 4. Run Sentiment Analysis

```bash
python sentiment/sentiment_analyzer.py
```
- This will process new articles and update their sentiment in the database.

### 5. Schedule Automated Runs

To run scraping and analysis every 30 minutes:

```bash
python run_every_30_minutes.py
```

---

## Usage

- **Dashboard:**  
  - Filter articles by sentiment, source, and date.
  - View sentiment distribution, articles per day, and word clouds.
- **API:**  
  - Access articles and sentiment data via REST endpoints (see FastAPI docs at `/docs`).

---

## Customization

- **Add New Sources:**  
  - Implement new scrapers in the `scrapers/` directory and update the scheduler if needed.
- **Change Sentiment Logic:**  
  - Modify `sentiment/sentiment_analyzer.py` for different models or rules.

---

## Troubleshooting

- Ensure the FastAPI backend is running before starting the dashboard.
- If you encounter missing dependencies, update `environment.yml` and re-create the environment.
- For database errors, check that `data/db.sqlite` exists and is accessible.

---

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes.

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

- [Dash](https://dash.plotly.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [NLTK](https://www.nltk.org/)
- [WordCloud](https://github.com/amueller/word_cloud)