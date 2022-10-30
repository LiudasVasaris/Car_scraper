import json
import re
from decimal import Decimal
from typing import Dict, Tuple, Optional

import requests
from bs4 import BeautifulSoup


def extract_engine_and_kw(s: str) -> Tuple[Optional[float], Optional[int]]:
    """Extracts engine liter and power in KW
    Args:
        s: string to parse containing liters and KW

    Returns:
        Tuple containing liters and KW
    """
    try:
        liters = float(re.findall(r"[\d.]+", (re.findall(r"\d+.*l", s)[0]))[0])
    except IndexError:
        liters = None
    try:
        kw = int(re.findall(r"\d+", (re.findall(r"\d+ kW", s)[0]))[0])
    except IndexError:
        kw = None
    return liters, kw


def extract_mileage_or_price(s: str) -> int:
    """Extracts mileage or price from string
    Args:
        s: string to parse containing price or mileage

    Returns: mileage or price
    """
    return None if not s else int("".join(filter(str.isdigit, s)))


# noinspection SpellCheckingInspection
class Car:
    """Data model for car
    Args:
        link: link to the post
        kwargs: other details about car
    """

    def __init__(self, link: str, **kwargs):
        self.price = extract_mileage_or_price(kwargs.get("Kaina"))
        self.brand = kwargs.get("Markė")
        self.model = kwargs.get("Modelis")
        self.year = kwargs.get("Metai")
        self.engine, self.kw = extract_engine_and_kw(kwargs.get("Variklis"))
        self.fuel = kwargs.get("Kuro tipas")
        self.body = kwargs.get("Kėbulo tipas")
        self.color = kwargs.get("Spalva")
        self.transmission = kwargs.get("Pavarų dėžė")
        self.milage = extract_mileage_or_price(kwargs.get("Rida"))
        self.wheel_drive = kwargs.get("Varomieji ratai")
        self.defects = kwargs.get("Defektai")
        self.steering_wheel = kwargs.get("Vairo padėtis")
        self.doors = kwargs.get("Durų skaičius")
        self.docs = kwargs.get("TA iki")
        self.rims = kwargs.get("Ratlankiai")
        self.first_registration = kwargs.get("Pirmosios registracijos šalis")
        self.consumption_city = (
            None if not kwargs.get("Mieste") else float(kwargs.get("Mieste"))
        )
        self.consumption_road = (
            None if not kwargs.get("Užmiestyje") else float(kwargs.get("Užmiestyje"))
        )
        self.consumption_mixed = (
            None if not kwargs.get("Mišrus") else float(kwargs.get("Mišrus"))
        )

        self.url = link

    def get_json(self):
        """Creates Json output of all information"""
        return json.loads(json.dumps(self.__dict__), parse_float=Decimal)

    def __repr__(self):
        return f"{self.brand} {self.model}, {self.year}, {self.price} eur."


def get_car_details(link: str, header: Dict[str, str]) -> Car:
    """Get details about a car provided via link
    Args:
        link: link to the page of a car
        header: header params to use

    Returns: Car data model
    """
    page = requests.get(link, headers=header)
    soup = BeautifulSoup(page.text, "html.parser")

    params = filter(
        lambda tag: tag["class"] == ["param"], soup.find_all("div", class_="param")
    )

    car_details = {
        (param.find("div", class_="left").text.strip()): (
            param.find("div", class_="right").text.strip()
        )
        for param in params
    }

    return Car(link=link, **car_details)
