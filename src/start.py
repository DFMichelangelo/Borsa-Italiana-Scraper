from src.bond import BondType
from src.email_sender import EmailSenderResource
from .scraper import Scraper
from .file_service import FileService
import os

  

def start():
  print("--- Start ---")
  scraper = Scraper(2)
  bonds = scraper.get_data()
  print("--- Finished scraping, Preparing Data  ---")
  fixed_bonds = [bond for bond in bonds if bond.bond_type == BondType.FIXED or bond.bond_type == BondType.ZERO_COUPON]
  fixed_bonds_with_ytm = list(map(lambda bond: bond.assign_ytm(), fixed_bonds))

  # Get bonds zero coupon and fixed rate and assign a YTM.
  df_bonds = FileService.create_dataframe_from_bonds(bonds)
  

  data_to_excel = [
    tuple("all_bonds", df_bonds),
    tuple("fixed_bonds", fixed_bonds_with_ytm),
    ]
  FileService.save_excel([data_to_excel])
  # send report
  should_send_email = os.environ("SHOULD_SEND_EMAIL")
  if should_send_email is not None and bool(should_send_email):
    with EmailSenderResource(
        smtp_server=os.environ("SMTP_SERVER"),
        port=int(os.environ("PORT")),
        sender_email=os.environ("EMAIL"),
        password=os.environ("PASSWORD"),
    ) as email_sender:
      email_sender.send_report_email(receivers=os.environ("RECEIVERS"))
