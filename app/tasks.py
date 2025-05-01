from apscheduler.schedulers.background import BackgroundScheduler
from .crud import store_rate
from .database import SessionLocal
import httpx, os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
FIXER_API_KEY = os.getenv("FIXER_API_KEY")

def fetch_and_store_rates():
    db = SessionLocal()
    url = f"https://data.fixer.io/api/latest?access_key={FIXER_API_KEY}"

    try:
        res = httpx.get(url)
        data = res.json()
        if "error" in data:
            logger.error(f"Fixer.io API Error: {data['error']}")
            return

        base = data["base"]
        rates = data["rates"]
        for target, rate in rates.items():
            store_rate(db, base, target, rate)

        logger.info("Exchange rates updated successfully!")

    except Exception as e:
        logger.error(f"Failed to update rates: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_rates, "interval", hours=24)
    scheduler.start()
    print("Scheduled jobs:", scheduler.get_jobs())
    logger.debug("Scheduler started successfully!")

