from logger import LOGGER
from scraper_main import run_scraper

def lambda_handler(event, context):
    LOGGER.info(f"Executing lambda function, event: {event}")
    pages_to_scrape = event.get("pages") or 2
    run_scraper(pages=pages_to_scrape)

    return {"message": "Scraper finished"}
