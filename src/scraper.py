from .bond import Bond
from bs4 import BeautifulSoup
from typing import List
import requests

class Scraper:

    def get_data(self) -> List[Bond]:
        print("Started get data d")
        headers = {'Accept-Encoding': 'identity'}
        response = requests.get("https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html", headers=headers)
        print("Ho preso" + response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("scraper")
        return [Bond(),Bond(),Bond()]