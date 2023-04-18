import datetime
from .bond import Bond, BondType, CouponFrequency
from .single_table_dto import SingleTableDTO
from bs4 import BeautifulSoup, Tag
from typing import Any, List
import urllib
import requests


class ElementNotFoundException(Exception):
  pass


class Scraper:

  def __init__ (self, amount: int | None):
    self.amount = amount

  def find_n_value_from_label(
          self,
          label: str,
          index: int,
          soup: BeautifulSoup) -> str:
    try:
      return soup.find_all(string=label)[index].find_parent(
          "tr").find_all("td")[1].find("span").text.replace("\n", "")
    except BaseException:
      return ""

  def find_value_from_label(self, label: str, soup: BeautifulSoup) -> str:
    try:
      found_element = soup.find(string=label)
      if found_element is None:
        raise ElementNotFoundException()
      tr_found = found_element.find_parent("tr")
      if tr_found is None:
        raise ElementNotFoundException()
      return tr_found.find_all("td")[1].find("span").text.replace("\n", "").strip()
    except BaseException:
      return ""

  def find_value_from_label_float(
          self,
          label: str,
          soup: BeautifulSoup) -> float:
    try:
      return float(
          self.find_value_from_label(
              label,
              soup).replace(
              ".",
              "").replace(
              ",",
              "."))
    except BaseException:
      return 0

  def find_value_from_label_int(self, label: str, soup: BeautifulSoup) -> int:
    try:
      return int(
          self.find_value_from_label(
              label,
              soup).replace(
              ".",
              "").replace(
              ",",
              "."))
    except BaseException:
      return 0

  def analyze_single_bond(self, url: str) -> Bond:
    print("Start analysing " + url)
    headers = {'Accept-Encoding': 'identity'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html5lib')
    bond = Bond()

    h1_title = soup.find("h1")
    if h1_title is not None:
      a_title = h1_title.find("a")
      if a_title is not None:
        name = str(a_title)
        if name is not None:
          bond.name = name

    bond.isin = self.find_value_from_label("Codice Isin", soup)
    bond.subordination = self.find_value_from_label("Subordinazione", soup)
    bond.bond_type = BondType.of(
        self.find_value_from_label("Tipologia", soup))
    bond.bond_structure = self.find_value_from_label(
        "Struttura Bond", soup)
    bond.payout_desription = self.find_value_from_label(
        "Descrizione Payout", soup)
    bond.coupon_percentage = self.find_value_from_label_float(
        "Tasso Prossima Cedola", soup)
    data_inizio_negoziazione = self.find_value_from_label("Data Inizio Negoziazione", soup)
    if(data_inizio_negoziazione != None):
      bond.emission_date = datetime.datetime.strptime(data_inizio_negoziazione, "%d/%m/%y")

    bond.coupon_frequency = CouponFrequency.of(
        self.find_value_from_label("Periodicità cedola", soup))
    # Switch to complete data
    try:
      ul = soup.find("ul", {"class": "tab-nav-wrapper"})
      if ul is None or not isinstance(ul, Tag):
        raise ElementNotFoundException()
      complete_data = ul.findAll("li")[1].find("a", href=True)['href']
      headers = {'Accept-Encoding': 'identity'}
      request_complete_data = requests.get(
          "https://www.borsaitaliana.it" + complete_data, headers=headers)
      soup_complete_data = BeautifulSoup(
          request_complete_data.text, 'html5lib')
    except BaseException as e:
      e.with_traceback()
      print("Error analyzing " + url, e)
      return bond

    bond.negotiation_currency = self.find_value_from_label(
        "Valuta di negoziazione", soup_complete_data)
    bond.liquidation_currency = self.find_value_from_label(
        "Valuta di liquidazione", soup_complete_data)
    bond.total_volume = self.find_value_from_label_float(
        "Volume totale", soup_complete_data)
    bond.minimun_amount = self.find_value_from_label_int(
        "Lotto Minimo", soup_complete_data)
    bond.field_type = self.find_value_from_label(
        "Tipologia", soup_complete_data)
    try:
      bond.ask_price = float(
          self.find_n_value_from_label(
              "Prezzo Acquisto",
              1,
              soup_complete_data).replace(
              ".",
              "").replace(
              ",",
              "."))
    except BaseException:
      bond.ask_price = 0
    try:
      bond.ask_volume = float(
          self.find_n_value_from_label(
              "Volume Acquisto",
              1,
              soup_complete_data).replace(
              ".",
              "").replace(
              ",",
              "."))
    except BaseException:
      bond.ask_volume = 0
    try:
      bond.bid_price = float(
          self.find_n_value_from_label(
              "Prezzo Vendita",
              1,
              soup_complete_data).replace(
              ".",
              "").replace(
              ",",
              "."))
    except BaseException:
      bond.bid_price = 0
    try:
      bond.bid_volume = float(
          self.find_n_value_from_label(
              "Volume Vendita",
              1,
              soup_complete_data).replace(
              ".",
              "").replace(
              ",",
              "."))
    except BaseException:
      bond.bid_volume = 0

    maturity_date = self.find_value_from_label("Scadenza", soup_complete_data)
    if(maturity_date != None):
      bond.maturity_date = datetime.datetime.strptime(maturity_date, "%d/%m/%y")

    return bond

  def get_data_single_url(self, url) -> List[Bond]:
    print("********************* New URL *********************")
    print(url)
    print("***************************************************")
    bonds = []
    data_start = self.analyze_single_table(url)
    for bond in data_start.bonds:
      bonds.append(bond)

    if self.amount != None and len(bonds) > self.amount:
        return bonds
    
    if (data_start.next_url):
      url_rolling = data_start.next_url
      while (url_rolling is not None):
        print("Start cycle", url_rolling)
        data = self.analyze_single_table(url_rolling)
        for bond in data.bonds:
          bonds.append(bond)
        
        if self.amount != None and len(bonds) > self.amount:
          return bonds
        
        print("Next url is", data.next_url)
        url_rolling = data.next_url

    print("End")
    return bonds

  def analyze_single_table(self, url) -> SingleTableDTO:
    bonds: List[Bond] = []
    try:
      headers = {'Accept-Encoding': 'identity'}
      response = requests.get(url, headers=headers)
      soup = BeautifulSoup(response.text, 'html5lib')
      table = soup.find("table")
      if (table is None):
        raise ElementNotFoundException()
      tbody = soup.find("tbody")
      if (tbody is None or not isinstance(tbody, Tag)):
        raise ElementNotFoundException()
      rows = tbody.find_all("tr")
    except Exception as e:
      print("Error", e)
      out_ex = SingleTableDTO()
      out_ex.bonds = bonds
      return out_ex

    for row in rows:
      try:
        single_row = row.find_all("td")
        if single_row is None or len(single_row) == 0:
          continue
        href = single_row[0].find("a", href=True)['href']
        bond = self.analyze_single_bond(
            "https://www.borsaitaliana.it" + href)
        bonds.append(bond)

        if self.amount != None and len(bonds) > self.amount:
          out = SingleTableDTO()
          out.bonds = bonds;
          return out
        
        print("--------------------------------")
      except Exception as e:
        e.with_traceback();
        print("Error", e)

    next_url = None
    try:
      # TODO Remove Any
      ul: Any = soup.find("ul", {"class": "m-pagination__nav"})
      if (ul is None):
        raise ElementNotFoundException()
      a = ul.find("a", title="Successiva", href=True)

      if (a is None):
        raise ElementNotFoundException()
      next_url = "https://www.borsaitaliana.it" + a.get('href')
    except BaseException:
      next_url = None
    out = SingleTableDTO()
    out.next_url = next_url if next_url is not None else None
    out.bonds = bonds
    return out

  def get_data(self) -> List[Bond]:
    urls = [
        "https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html",
        "https://www.borsaitaliana.it/borsa/obbligazioni/extramot/lista.html",
        "https://www.borsaitaliana.it/borsa/obbligazioni/extramot-procube/lista.html",
        "https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/lista.html"]
    bonds: List[Bond] = []
    for url in urls:
      if self.amount != None and len(bonds) > self.amount:
        break
      
      single_bond_list = self.get_data_single_url(url)
      for single in single_bond_list:
        bonds.append(single)
      
    return bonds
