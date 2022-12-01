from ETL.etl_car_scraper import run_etl
from ETL.logger import LOGGER


def lambda_handler(event, context):
    LOGGER.info(f"Executing lambda function, event: {event}")
    run_etl()

    return {"message": "ETL finished"}
