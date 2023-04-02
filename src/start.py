from .scraper import Scraper
from .fileService import FileService

def start():
    print("--- Start ---")
    scraper = Scraper()
    bonds = scraper.get_data()
    print("--- Finished scraping, saving file  ---")
    file_service = FileService()
    file_service.save_csv(file_service.create_csv(bonds))