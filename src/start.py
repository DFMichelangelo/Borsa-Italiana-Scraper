from .scraper import Scraper
from .file_service import FileService


def start():
  print("--- Start ---")
  scraper = Scraper(10)
  bonds = scraper.get_data()
  print("--- Finished scraping, saving file  ---")
  file_service = FileService()
  #file_service.save_csv(file_service.create_csv(bonds))")
  file_service.save_excel(file_service.create_dataframe_from_bonds(bonds))
