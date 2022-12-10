from etl_car_scraper import run_etl
from logger_etl import LOGGER


def lambda_handler(event, context):
    LOGGER.info(f"Executing lambda function, event: {event}")
    run_etl()

    return {"message": "ETL finished"}
