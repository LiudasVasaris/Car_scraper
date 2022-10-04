from typing import Tuple, List, Dict

import requests
from bs4 import BeautifulSoup

from scraper_car_page import get_car_details, Car

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
MAIN_PAGE = "https://autogidas.lt/"
SEARCH_PAGE = "https://autogidas.lt/skelbimai/automobiliai/?f_13=Vilnius&s=1411740949&f_50=atnaujinimo_laika_asc&page=1"


def get_info_from_search_page(
    search_page: str, main_page: str, header: Dict[str, str]
) -> Tuple[List[Car], int]:
    """Gets info of all not sold cars in given search page
    Args:
        search_page: link to the search page
        main_page: main website domain
        header: header params to use

    Returns: List of car details and last page number
    """
    # fetch link
    page = requests.get(search_page, headers=header)
    # Get HTML content
    soup = BeautifulSoup(page.text, "html.parser")

    articles = soup.find_all("article")
    car_links = sorted(
        {
            a.find(class_="item-link")["href"]
            for a in articles
            if not a.find("div", class_="sold-item")  # Skip sold items
        }
    )

    cars = [
        get_car_details(link=main_page + car_link, header=HEADER)
        for car_link in car_links
    ]

    last_page = int(
        max(soup.find_all("div", class_="page"), key=lambda el: el.text).text
    )

    return cars, last_page
