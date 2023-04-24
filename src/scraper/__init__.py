import datetime
from src.scraper.data_converters import scraped_str_to_subordination, str_to_bond_structure, str_to_coupon_frequency
from src.utils import datetimes_difference_in_years
from ..bond import Bond
from ..single_table_dto import SingleTableDTO
from bs4 import BeautifulSoup, Tag
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class ElementNotFoundException(Exception):
  pass


class Scraper:

  def __init__(self, amount_to_scrape: int | None = None):
    self.amount_to_scrape = amount_to_scrape
    self.amount = 0
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/usr/bin/chromedriver')
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
    except ValueError:
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
    bond.issuer = self.find_value_from_label("Emittente", soup)
    data_godimento = self.find_value_from_label("Data Godimento", soup)
    if data_godimento is not None and data_godimento != "":
      bond.date_start_maturation = datetime.datetime.strptime(data_godimento, "%d/%m/%y")
    bond.subordination = scraped_str_to_subordination(
        self.find_value_from_label("Subordinazione", soup))
    bond.bond_structure = str_to_bond_structure(
        self.find_value_from_label(
            "Struttura Bond", soup))
    bond.bond_structure_raw = self.find_value_from_label(
        "Struttura Bond", soup)
    bond.bond_type = self.find_value_from_label("Tipologia", soup)
    bond.coupon_percentage = self.find_value_from_label_float(
        "Tasso Prossima Cedola", soup) / 100
    data_inizio_negoziazione = self.find_value_from_label("Data Inizio Negoziazione", soup)
    if (data_inizio_negoziazione is not None):
      bond.emission_date = datetime.datetime.strptime(data_inizio_negoziazione, "%d/%m/%y")
    bond.coupon_frequency = str_to_coupon_frequency(
        self.find_value_from_label("Periodicità cedola", soup))
    bond.coupon_frequency_raw = self.find_value_from_label("Periodicità cedola", soup)
    bond.BI_gross_ytm = self.find_value_from_label_float(
        "Rendimento effettivo a scadenza lordo", soup) / 100
    bond.BI_net_ytm = self.find_value_from_label_float(
        "Rendimento effettivo a scadenza netto", soup) / 100
    bond.payout_desription = self.find_value_from_label(
        "Descrizione Payout", soup)
    # Switch to complete data
    try:
      ul = soup.find("ul", {"class": "tab-nav-wrapper"})
      if ul is None or not isinstance(ul, Tag):
        raise ElementNotFoundException()
      complete_data = ul.findAll("li")[1].find("a", href=True)['href']
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
      pass
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
      pass
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
    bond.face_value = 100
    bond.years_to_maturity = datetimes_difference_in_years(datetime.datetime.today(), bond.maturity_date)
    return bond

  def get_data_single_url(self, url, paginated, click_on_search, is_eurotlx) -> list[Bond]:
    print(f"************ New URL ************\n{url}\n*********************************")
    bonds = []
    page = 1
    if paginated:
      url_rolling = url + f"?&page={page}"
    else:
      url_rolling = url
    while (url_rolling is not None):
      print(f"Start page {page}, {url_rolling}")

      if paginated is True:
        data = self.analyze_single_table(url_rolling, None, True, False, False)
        page += 1
        if data.bonds == []:
          url_rolling = None
        else:
          url_rolling = url + f"?&page={page}"
      else:
        data = self.analyze_single_table(
            None,
            url_rolling,
            False,
            click_on_search,
            is_eurotlx) if page > 1 else self.analyze_single_table(
            url,
            None,
            False,
            click_on_search if page == 1 else False,
            is_eurotlx)
        url_rolling = data.next_url_to_click

      bonds += data.bonds

    return bonds

  def analyze_single_bond_eurotlx(self, url: str) -> Bond:
    print("Start analysing (eurotlx) " + url)
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

    bond.BI_gross_ytm = self.find_value_from_label_float(
        "Rendimento effettivo a scadenza lordo", soup) / 100
    bond.BI_net_ytm = self.find_value_from_label_float(
        "Rendimento effettivo a scadenza netto", soup) / 100
    bond.isin = self.find_value_from_label("ISIN", soup)
    # Switch to complete data
    try:
      complete_data = f"/borsa/obbligazioni/eurotlx/dati-completi.html?isin={bond.isin}&lang=it"
      headers = {'Accept-Encoding': 'identity'}
      request_complete_data = requests.get(
          "https://www.borsaitaliana.it" + complete_data, headers=headers)
      soup_complete_data = BeautifulSoup(
          request_complete_data.text, 'html5lib')
    except ElementNotFoundException as e:
      print("Error analyzing " + url, e)
      return bond
    bond.issuer = self.find_value_from_label("Emittente", soup_complete_data)
    bond.ask_price = self.find_value_from_label_float("Prezzo di chiusura", soup_complete_data)
    bond.bid_price = bond.ask_price
    bond.bond_type = self.find_value_from_label("Tipologia", soup)
    bond.coupon_percentage = self.find_value_from_label_float(
        "Tasso cedola in corso", soup) / 100
    bond.coupon_frequency = str_to_coupon_frequency(
        self.find_value_from_label("Frequenza di pagamento", soup))
    bond.coupon_frequency_raw = self.find_value_from_label("Frequenza di pagamento", soup)
    bond.negotiation_currency = self.find_value_from_label(
        "Valuta di negoziazione", soup_complete_data)
    bond.total_volume = self.find_value_from_label_float(
        "Volume giornaliero", soup_complete_data)
    bond.minimun_amount = self.find_value_from_label_int(
        "Lotto minimo", soup_complete_data)
    bond.field_type = self.find_value_from_label(
        "Tipologia", soup_complete_data)
    maturity_date = self.find_value_from_label("Data di scadenza", soup_complete_data)
    if (maturity_date is not None and maturity_date != ""):
      bond.maturity_date = datetime.datetime.strptime(maturity_date, "%d/%m/%Y")
    bond.face_value = 100
    bond.years_to_maturity = datetimes_difference_in_years(datetime.datetime.today(), bond.maturity_date)
    return bond

  def analyze_row(self, row, is_eurotlx: bool) -> Bond | None:
    try:
      self.amount += 1
      single_row = row.find_all("td")
      if single_row is None or len(single_row) == 0:
        return None

      href = single_row[0].find("a", href=True)['href']
      if is_eurotlx:
        # isin=single_row[0].find("a", href=True).text
        bond = self.analyze_single_bond_eurotlx(
            "https://www.borsaitaliana.it" + href)
      else:
        bond = self.analyze_single_bond(
            "https://www.borsaitaliana.it" + href)
      return bond
    except Exception as e:
      print("Error: ", e)
      traceback.print_exc()
      return None

  def analyze_single_table(
          self,
          url,
          url_to_click,
          paginated: bool,
          click_on_search: bool,
          is_eurotlx: bool) -> SingleTableDTO:
    bonds: list[Bond] = []
    try:
      # navigate to the webpage
      if url_to_click is None and url is not None:
        self.driver.get(url)
      else:
        url_to_click.click()
      wait = WebDriverWait(self.driver, 3)

      if paginated is False:
        if url is not None:
          try:
            button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(),'Accetta tutti i cookie di profilazione')]")))
            button.click()
            if click_on_search:
              search_button = wait.until(
                  EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Cerca']")))
              search_button.click()
          except BaseException:
            pass
          try:
            link_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='Successiva']")))
          except BaseException:
            print("link_element not found")
            link_element = None
          ul_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "m-pagination__nav")))
        try:
          wait.until(EC.visibility_of_element_located((By.ID, "tableResults")))
        except BaseException:
          pass

      try:
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "m-table -firstlevel")))
      except BaseException:
        pass

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
      traceback.print_exc()
      out_ex = SingleTableDTO()
      out_ex.bonds = bonds
      out_ex.next_url_to_click = None
      return out_ex

    for row in rows:
      # TODO REMOVE
      bond = self.analyze_row(row, is_eurotlx)
      if (bond is not None):
        bonds.append(bond)
      if self.amount_to_scrape is not None and len(bonds) >= self.amount_to_scrape:
        break

    next_url = None
    if paginated:
      try:
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
        # "https://www.borsaitaliana.it/borsa/obbligazioni/ricerca-avanzata.html", #pagination https://www.borsaitaliana.it/borsa/obbligazioni/advanced-search.html?size=&lang=it&page=30
        ["https://www.borsaitaliana.it/borsa/obbligazioni/eurotlx/ricerca-avanzata.html", False],
        ["https://www.borsaitaliana.it/borsa/obbligazioni/advanced-search.html?size=&lang=it", True],  # pagination https://www.borsaitaliana.it/borsa/obbligazioni/advanced-search.html?size=&lang=it&page=30
        ["https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html", True],
        ["https://www.borsaitaliana.it/borsa/obbligazioni/extramot/lista.html", True],
        ["https://www.borsaitaliana.it/borsa/obbligazioni/extramot-procube/lista.html", True],
        ["https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/lista.html", True]
    ]
    bonds: list[Bond] = []
    for url in urls:
      click_on_search = url[0] == "https://www.borsaitaliana.it/borsa/obbligazioni/eurotlx/ricerca-avanzata.html"
      single_bond_list = self.get_data_single_url(url[0], url[1], click_on_search, click_on_search)
      bonds += single_bond_list
    self.driver.close()
    return bonds
