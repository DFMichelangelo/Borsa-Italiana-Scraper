from .bond import Bond
from bs4 import BeautifulSoup
from typing import List
import urllib
import requests

class Scraper:

    def find_value_from_label(self, label: str, soup: BeautifulSoup) -> str:
        try:
            return soup.find(string=label).find_parent("tr").find_all("td")[1].find("span").text
        except:
            return "";
    
    def find_value_from_label_float(self, label: str, soup: BeautifulSoup) -> float:
        try:
            return float(self.find_value_from_label(label, soup))
        except:
            return 0;
    
    def find_value_from_label_int(self, label: str, soup: BeautifulSoup) -> int:
        try:
            return int(self.find_value_from_label(label, soup))
        except:
            return 0;

    def analyze_single_bond(self, url: str) -> Bond:
        print("Start analysing " + url)
        headers = {'Accept-Encoding': 'identity'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html5lib')
        bond = Bond()
        bond.name = soup.find("h1").find("a").string;
        bond.isin = self.find_value_from_label("Codice Isin",soup)
        bond.subordination = self.find_value_from_label("Subordinazione",soup)
        bond.bond_type = self.find_value_from_label("Tipologia",soup)
        bond.bond_structure = self.find_value_from_label("Struttura Bond",soup)
        bond.payout_desription = self.find_value_from_label("Descrizione Payout",soup)
        bond.coupon_percentage = self.find_value_from_label_float("Tasso Prossima Cedola",soup)

        #Switch to complete data
        try:
            complete_data = soup.find("ul", {"class": "tab-nav-wrapper"}).findAll("li")[1].find("a", href=True)['href'];
            headers = {'Accept-Encoding': 'identity'}
            request_complete_data = requests.get("https://www.borsaitaliana.it" + complete_data, headers=headers)
            soup_complete_data = BeautifulSoup(request_complete_data.text, 'html5lib')
        except:
            print("Error analyzing " + url)
            return bond;
    
        bond.negotiation_currency = self.find_value_from_label("Valuta di negoziazione",soup_complete_data)
        bond.liquidation_currency = self.find_value_from_label("Valuta di liquidazione",soup_complete_data)
        bond.total_volume = self.find_value_from_label_float("Volume totale",soup_complete_data)
        bond.minimun_amount = self.find_value_from_label_int("Lotto Minimo",soup_complete_data)
        bond.field_type  = self.find_value_from_label("Tipologia",soup_complete_data)
        
        bond.ask_price = self.find_value_from_label_float("Prezzo Acquisto",soup_complete_data)
        bond.ask_volume = self.find_value_from_label_float("Volume Acquisto",soup_complete_data)
        bond.bid_price = self.find_value_from_label_float("Prezzo Vendita",soup_complete_data)
        bond.bid_volume = self.find_value_from_label_float("Volume Vendita",soup_complete_data)

        print("End", bond)
        return bond;

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
            bond = self.analyze_single_bond("https://www.borsaitaliana.it" + href)
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