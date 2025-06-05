import schedule
import time
import subprocess
import warnings
warnings.filterwarnings("ignore")

def run_scraper():
    print("Running scraper")
    result = subprocess.run(["python", "-m", "scrapers.__main__"])
    print(result.stdout)
    print(result.stderr)


# Run immediately once
run_scraper()

# Schedule the task every 30 minutes
schedule.every(30).minutes.do(run_scraper)

print("Scheduler started. Running every 30 minutes...")
while True:
    schedule.run_pending()
    time.sleep(1)
