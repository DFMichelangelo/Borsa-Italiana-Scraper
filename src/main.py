from scraper import Scraper

def main():
    print("--- Start ---")
    scraper = Scraper()
    print("--- Finished scraping, init  ---")
    bonds = scraper.get_data()
    for single_bond in bonds:
        single_bond.calculate_yeld_to_maturity()


if __name__ == '__main__':
    main()