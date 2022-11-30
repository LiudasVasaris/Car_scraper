from Scraper.logger import LOGGER
from Scraper.scraper_main import run_scraper


def lambda_handler(event, context):
    LOGGER.info(f"Executing lambda function, event: {event}")
    run_scraper(pages=2)

    return {"message": "Scraper finished"}
