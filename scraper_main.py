from typing import List, Dict

import boto3

from scraper_car_page import Car
from scraper_search_page import get_info_from_search_page

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
MAIN_PAGE = "https://autogidas.lt/"
SEARCH_PAGE = "https://autogidas.lt/skelbimai/automobiliai/?f_13=Vilnius&s=1411740949&f_50=atnaujinimo_laika_asc&page={page_nr}"


def scrape_pages(
    pages_to_scrape: int, initial_link: str, main_page: str, header: Dict[str, str]
) -> List[Car]:
    """Scrapes pages to get information about cars
    Args:
        pages_to_scrape: number of pages to scrape
        initial_link: search page link
        main_page: main page link
        header: header params to use

    Returns: List of cars from pages
    """
    cars_from_pages = list()
    for i in range(1, pages_to_scrape + 1):
        cars, last_page = get_info_from_search_page(
            initial_link.format(page_nr=i), main_page=main_page, header=header
        )
        cars_from_pages += cars
        if i >= last_page:
            break

    return cars_from_pages


def write_to_db(cars_from_pages: List[Car]):
    """Writes scraped car info to DynamoDB
    Args:
        cars_from_pages (): List of cars to write to db
    """
    client_dynamo = boto3.resource("dynamodb")
    table = client_dynamo.Table("car_table")
    with table.batch_writer() as batch:
        for car in cars_from_pages:
            batch.put_item(Item=car.get_json())


if __name__ == "__main__":

    scraped_cars = scrape_pages(
        pages_to_scrape=2, initial_link=SEARCH_PAGE, main_page=MAIN_PAGE, header=HEADER
    )
    write_to_db(scraped_cars)
