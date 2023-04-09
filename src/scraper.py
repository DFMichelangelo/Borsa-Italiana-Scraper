from .bond import Bond
from .single_table_dto import SingleTableDTO
from bs4 import BeautifulSoup
from typing import List
import urllib
import requests

class Scraper:

    def find_n_value_from_label(self, label: str, index: int, soup: BeautifulSoup) -> str:
        try:
            return soup.find_all(string=label)[index].find_parent("tr").find_all("td")[1].find("span").text.replace("\n", "")
        except:
            return "";

    def find_value_from_label(self, label: str, soup: BeautifulSoup) -> str:
        try:
            return soup.find(string=label).find_parent("tr").find_all("td")[1].find("span").text.replace("\n", "")
        except:
            return "";
    
    def find_value_from_label_float(self, label: str, soup: BeautifulSoup) -> float:
        try:
            return float(self.find_value_from_label(label, soup).replace(".", "").replace(",", "."))
        except:
            return 0;
    
    def find_value_from_label_int(self, label: str, soup: BeautifulSoup) -> int:
        try:
            return int(self.find_value_from_label(label, soup).replace(".", "").replace(",", "."))
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
        bond.emission_date = self.find_value_from_label("Data Inizio Negoziazione",soup)
        bond.coupoon_frequency = self.find_value_from_label("Periodicità cedola",soup)

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

        try:
            bond.ask_price = float(self.find_n_value_from_label("Prezzo Acquisto",1,soup_complete_data).replace(".", "").replace(",", "."))
        except:
            bond.ask_price = 0
        try:
            bond.ask_volume = float(self.find_n_value_from_label("Volume Acquisto",1,soup_complete_data).replace(".", "").replace(",", "."))
        except:
            bond.ask_volume = 0
        try:
            bond.bid_price = float(self.find_n_value_from_label("Prezzo Vendita",1,soup_complete_data).replace(".", "").replace(",", "."))
        except:
            bond.bid_price = 0
        try:
            bond.bid_volume = float(self.find_n_value_from_label("Volume Vendita",1,soup_complete_data).replace(".", "").replace(",", "."))
        except:
            bond.bid_volume = 0

        bond.maturity_date = self.find_value_from_label("Scadenza",soup_complete_data)
        
        return bond;

    def get_data_single_url(self, url) -> List[Bond]:
        print("********************* New URL *********************")
        print(url)
        print("***************************************************")
        bonds = []
        data_start = self.analyze_single_table(url)
        for bond in data_start.bonds:
            bonds.append(bond)

        if(data_start.next_url):
            url_rolling = data_start.next_url
            while(url_rolling != None):
                print("Start cycle", url_rolling)
                data = self.analyze_single_table(url_rolling)
                for bond in data.bonds:
                    bonds.append(bond)
                print("Next url is", data.next_url)
                url_rolling = data.next_url
                
        print("End")
        return bonds
    
    def analyze_single_table(self, url) -> SingleTableDTO:
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
            print("--------------------------------")
        
        next_url = None
        try:
            next_url = "https://www.borsaitaliana.it" + soup.find("ul", {"class": "m-pagination__nav"}).find("a", title="Successiva", href=True)['href'];
        except: 
            next_url = None
        out = SingleTableDTO()
        out.next_url = next_url
        out.bonds = bonds;
        return out

    def get_data(self) -> List[Bond]:
        urls = [
            "https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html",
            "https://www.borsaitaliana.it/borsa/obbligazioni/extramot/lista.html",
            "https://www.borsaitaliana.it/borsa/obbligazioni/extramot-procube/lista.html",
            "https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/lista.html"
        ]
        bonds : List[Bond]= []
        for url in urls:
            single_bond_list = self.get_data_single_url(url)
            for single in single_bond_list:
                bonds.append(single)
        
        return bonds;