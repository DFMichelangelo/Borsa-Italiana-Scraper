from .bond import Bond
from bs4 import BeautifulSoup
from typing import List
import urllib
import requests

class Scraper:

    def analyze_single_bond(self, url):
        print("Start analysing " + url)
        headers = {'Accept-Encoding': 'identity'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html5lib')
        print("End")

    def get_data_single_url(self, url) -> List[Bond]:
        print("Started get data")
        headers = {'Accept-Encoding': 'identity'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html5lib')
        rows = soup.find("table").find("tbody").find_all("tr")
        bonds = []
        for row in rows:
            single_row = row.find_all("td")
            if single_row == None or len(single_row) == 0 : continue
            href = single_row[0].find("a", href=True)['href']
            #bond = self.analyze_single_bond(urllib.urlparse(url).urljoin(href))
            bonds.append(bond)
            print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
        
        print("End")
        return bonds
    
    def get_data(self) -> List[Bond]:
        urls = [
            "https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html",
            "https://www.borsaitaliana.it/borsa/obbligazioni/extramot/lista.html"
        ]
        bonds = []
        for url in urls:
            single_bond_list = self.get_data_single_url(url)
            bonds.append(single_bond_list)
        
        return bonds;