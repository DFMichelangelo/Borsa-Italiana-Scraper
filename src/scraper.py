import datetime
from .bond import Bond
from .single_table_dto import SingleTableDTO
from bs4 import BeautifulSoup, Tag
from typing import Any
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# if it does not work, use this link with bs4:
#https://www.borsaitaliana.it/borsa/obbligazioni/advanced-search.html?size=&lang=it&page=30 

class ElementNotFoundException(Exception):
  pass


class Scraper:

  def __init__(self, amount: int | None = None):
    self.amount = amount
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    self.driver = driver

  def find_n_value_from_label(
          self,
          label: str,
          index: int,
          soup: BeautifulSoup) -> str:
    try:
      return soup.find_all(string=label)[index].find_parent(
          "tr").find_all("td")[1].find("span").text.replace("\n", "")
    except (ElementNotFoundException, IndexError):
      print(f"warning for label '{label}', at index '{index}'", )
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
    except ElementNotFoundException:
      return ""

  def find_value_from_label_float(self, label: str, soup: BeautifulSoup) -> float:
    try:
      return float(self.find_value_from_label(label, soup).replace(".", "").replace(",", "."))
    except ElementNotFoundException:
      return 0
    except ValueError:
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
    except ElementNotFoundException:
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
      if a_title is not None and not isinstance(a_title, int):
        name = str(a_title.text)
        if name is not None:
          bond.name = name

    bond.isin = self.find_value_from_label("Codice Isin", soup)
    bond.subordination = self.find_value_from_label("Subordinazione", soup)
    bond.bond_structure = Bond.BondStructure.of(
        self.find_value_from_label(
            "Struttura Bond", soup))
    bond.bond_structure_raw = self.find_value_from_label(
        "Struttura Bond", soup)
    bond.bond_type = self.find_value_from_label("Tipologia", soup)
    bond.payout_desription = self.find_value_from_label(
        "Descrizione Payout", soup)
    bond.coupon_percentage = self.find_value_from_label_float(
        "Tasso Prossima Cedola", soup)
    data_inizio_negoziazione = self.find_value_from_label("Data Inizio Negoziazione", soup)
    if (data_inizio_negoziazione is not None):
      bond.emission_date = datetime.datetime.strptime(data_inizio_negoziazione, "%d/%m/%y")

    bond.coupon_frequency = Bond.CouponFrequency.of(
        self.find_value_from_label("Periodicità cedola", soup))
    bond.coupon_frequency_raw = self.find_value_from_label("Periodicità cedola", soup)
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
    except ElementNotFoundException as e:
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
    except (ElementNotFoundException, ValueError):
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
    except (ElementNotFoundException, ValueError):
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
    except (ElementNotFoundException, ValueError):
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
    except (ElementNotFoundException, ValueError):
      bond.bid_volume = 0

    maturity_date = self.find_value_from_label("Scadenza", soup_complete_data)
    if (maturity_date is not None):
      bond.maturity_date = datetime.datetime.strptime(maturity_date, "%d/%m/%y")

    return bond

  def get_data_single_url(self, url) -> list[Bond]:
    print("********************* New URL *********************")
    print(url)
    print("***************************************************")
    bonds = []
    data_start = self.analyze_single_table(url, None)
    bonds += data_start.bonds
    # for bond in data_start.bonds:
    #  bonds.append(bond)

    if self.amount is not None and len(bonds) > self.amount - 1:
      return bonds

    if (data_start.next_url_to_click):
      url_rolling = data_start.next_url_to_click
      while (url_rolling is not None):
        print("Start cycle", url_rolling)
        data = self.analyze_single_table(None, url_rolling)
        bonds += data.bonds
        # for bond in data.bonds:
        #  bonds.append(bond)

        if self.amount is not None and len(bonds) > self.amount - 1:
          return bonds

        print("Next url is", data.next_url_to_click)
        url_rolling = data.next_url_to_click

    print("End")
    return bonds

  def analyze_single_table(self, url, url_to_click=None) -> SingleTableDTO:
    bonds: list[Bond] = []
    try:
      # navigate to the webpage
      if url_to_click is None and url is not None:
        self.driver.get(url)
      else:
        url_to_click.click()

      # wait for the "Tipo" dropdown to load and select "Obbligazioni"
      wait = WebDriverWait(self.driver, 5)
      if url is not None:
        button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Accetta tutti i cookie di profilazione')]")))
        button.click()
      wait.until(EC.visibility_of_element_located((By.ID, "tableResults")))
      ul_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "m-pagination__nav")))
      link_element = wait.until(
          EC.presence_of_element_located(
              (By.CSS_SELECTOR, "a[title='Successiva']"))
      )

      # soup = BeautifulSoup(self.driver.page_source, 'html5lib')
      tableResults = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "table")))
      table_selenium = tableResults.get_attribute("outerHTML")

      soup_table = BeautifulSoup(table_selenium, 'html5lib')
      table = soup_table.find("table")

      if (table is None):
        raise ElementNotFoundException()
      tbody = soup_table.find("tbody")
      if (tbody is None or not isinstance(tbody, Tag)):
        raise ElementNotFoundException()
      rows = tbody.find_all("tr")
    except Exception as e:
      print("Error: ", e)
      out_ex = SingleTableDTO()
      out_ex.bonds = bonds
      out_ex.next_url_to_click = None
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

        if self.amount is not None and len(bonds) > self.amount - 1:
          out = SingleTableDTO()
          out.bonds = bonds
          return out

      except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

    next_url = None
    try:
      # TODO Remove Any
     # ul: Any = soup.find("ul", {"class": "m-pagination__nav"})
      # if (ul is None):
      #  raise ElementNotFoundException()
      # a = ul.find("a", title="Successiva", href=True)

      # if (a is None):
      if (link_element is None):
        raise ElementNotFoundException("link_element not found")
      next_url = link_element

    except BaseException:
      next_url = None
    out = SingleTableDTO()
    out.next_url_to_click = next_url if next_url is not None else None
    out.bonds = bonds
    return out

  def get_data(self) -> list[Bond]:
    urls = [
        "https://www.borsaitaliana.it/borsa/obbligazioni/ricerca-avanzata.html",
        # "https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html",
        # "https://www.borsaitaliana.it/borsa/obbligazioni/extramot/lista.html",
        # "https://www.borsaitaliana.it/borsa/obbligazioni/extramot-procube/lista.html",
        # "https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/lista.html"
    ]
    bonds: list[Bond] = []
    for url in urls:
      if self.amount is not None and len(bonds) > self.amount:
        break

      single_bond_list = self.get_data_single_url(url)
      for single in single_bond_list:
        bonds.append(single)
    self.driver.close()
    return bonds
