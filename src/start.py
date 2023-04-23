from src.bond import Bond
from src.email_sender import EmailSender
from .scraper import Scraper
from .file_service import FileService
import os


def start():
  print("--- Scraping Data ---")
  scraper = Scraper(2)
  bonds = scraper.get_data()
  print("--- Preparing Data  ---")
  fixed_bonds = [bond for bond in bonds if bond.bond_structure ==
                 Bond.BondStructure.PLAIN_VANILLA]
  fixed_bonds_with_ytm = list(map(lambda bond: bond.assign_ytm(), fixed_bonds))

  # Get bonds zero coupon and fixed rate and assign a YTM.
  df_bonds = FileService.create_dataframe_from_bonds(bonds)
  df_fixed_bonds_with_ytm = FileService.create_dataframe_from_bonds(fixed_bonds_with_ytm)

  data_to_excel = [
      ("all_bonds", df_bonds),
      ("fixed_bonds", df_fixed_bonds_with_ytm),
  ]
  print("--- Saving Data in Excel  ---")
  FileService.save_excel(data_to_excel)

  should_send_email = os.environ.get("SHOULD_SEND_EMAIL")

  if should_send_email is not None and bool(should_send_email):
    print("--- Sending email  ---")
    email_sender = EmailSender(
        smtp_server=os.environ.get("SMTP_SERVER"),
        port=int(os.environ.get("PORT")),
        sender_email=os.environ.get("EMAIL"),
        password=os.environ.get("PASSWORD")
    )
    email_sender.send_report_email(receivers=os.environ.get("RECEIVERS"))
    print("--- email Sent ---")
    email_sender.close_connection()
